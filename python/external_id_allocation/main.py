# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from ncs.dp import Action
import ncs.experimental
# random is just used for testing
import random
from . import ipam



class AllocateAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        self.log.info('action kp: ', str(kp))
        # if the your actions take more than 240 seconds, increase the action_set_timeout
        # _ncs.dp.action_set_timeout(uinfo,240)

        request_name = ''
        use_random = False
        # Check if we have already an allocated value
        with ncs.maapi.single_read_trans(uinfo.username, uinfo.context) as trans:
            request = ncs.maagic.get_node(trans, kp)
            request_name = request.name

            if request._parent._parent.use_random:
                use_random = True
                self.log.info('Will use random ids instead of asking the ipam server')

            # Check if we want to reallocate the id, if so we dont need to check if it exists
            if not input.re_allocate:
                if request._parent._parent.response.exists(request_name):
                    response = request._parent._parent.response[request_name]
                    if response.id:
                        output.result = 'id: ' + str(response.id) + ' already allocated'
                        self.log.info('action alloction id already exists: ', str(response.id))
                        # What do you want to do if its already allocate? Exit?
                        return

        error = ''
        # To test without any ipam server
        if use_random:
            self.log.info('using random')
            allocated_id = random.randint(100, 1000)
        else:
            # to test with the small python ipam-server example
            self.log.info('allocating via ipam')
            allocated_id, error = ipam.request(self, request_name)

        with ncs.maapi.single_write_trans(uinfo.username, uinfo.context) as trans:
            request = ncs.maagic.get_node(trans, kp)
            response = request._parent._parent.response.create(request.name)
            response.allocating_service = request.allocating_service
            # check if allocation went OK, if failed we should write to response.error
            if error:
                response.error = error
            elif not allocated_id:
                # should not happen
                response.error = 'No ID allocated, check log file for error'
            else:
                # Clean up old errors
                del response.error
                response.id = allocated_id
            trans.apply()
            self.log.info('action allocated id: ', str(response.id))


class ServiceCallbacks(Service):
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        """Creates the two kickers (allocate, re-deploy-service"""
        self.log.info('Service create(service=', service._path, ')')
        vars = ncs.template.Variables()
        template = ncs.template.Template(service)
        template.apply('external-id-allocation-template', vars)


# ------------------------------------------------
# SUBSCRIBER for deletes, only here until kickers can distinguish between create/delete
# ------------------------------------------------
#class DeleteSubscriber(ncs.cdb.Subscriber):
class DeleteSubscriber(ncs.cdb.Subscriber):
    def init(self):
        self.register('/ext-id:external-id-allocation/ext-id:request', priority=100)

    # Initate your local state
    def pre_iterate(self):
        return []

    # Iterate over the change set
    def iterate(self, keypath, op, oldval, newval, state):
        self.log.info('Delete Subscriber kp: ' + str(keypath))
        # 2: 'MOP_DELETED'
        if op == 2:
            # replace the request keypath with response as that is where the
            # release action is
            response_kp = str(keypath).replace('request', 'response')
            state.append(response_kp)
        return ncs.ITER_RECURSE

    # This will run in a separate thread to avoid a transaction deadlock
    def post_iterate(self, state):
        self.log.info('DeleteSubscriber: post_iterate, state=', state)
        with ncs.maapi.single_read_trans('system', 'system') as trans:
            for response_kp in state:
                allocation = ncs.maagic.get_node(trans, response_kp)
                allocation.ext_id__release()
                self.log.info('Allocation released: ', response_kp)

    # determine if post_iterate() should run
    def should_post_iterate(self, state):
        return state != []


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main external-id-allocation RUNNING')
        self.register_service('external-id-allocation-servicepoint', ServiceCallbacks)
        self.register_action('external-id-allocation-action', AllocateAction)

        # Create your subscriber
        self.sub = DeleteSubscriber(app=self)
        self.sub.start()

    def teardown(self):
        self.sub.stop()
        self.log.info('Main FINISHED')
