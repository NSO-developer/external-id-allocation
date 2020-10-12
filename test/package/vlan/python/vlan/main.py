# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import ncs.experimental
import _ncs
import ipam
import random
import time
# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    #@Service.create
    #def cb_create(self, tctx, root, service, proplist):
    #    self.log.info('Service create(service=', service._path, ')')
    #    vars = ncs.template.Variables()
    #    template = ncs.template.Template(service)
    #    template.apply('vlan-template', vars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    @Service.pre_lock_create
    def cb_pre_lock_create(self, tctx, root, service, proplist):
        self.log.info('Service plcreate(service=', service._path, ')')
        allocated_id = random.randint(100, 1000)
        time.sleep(5)
        vars = ncs.template.Variables()
        self.log.info('Allocated VLAN: ', allocated_id)
        vars.add('VLAN', allocated_id)
        template = ncs.template.Template(service)
        template.apply('vlan-template', vars)


    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

class DeleteSubscriber(ncs.cdb.Subscriber):
    def init(self):
        self.register('/vlan:vlanid', priority=100)

    # Initate your local state
    def pre_iterate(self):
        return []

    # Iterate over the change set
    def iterate(self, keypath, op, oldval, newval, state):
        self.log.info('Delete Subscriber kp: ' + str(keypath) + ' old value: ' + str(oldval) + ' new value: ' + str(newval))
        #2: 'MOP_DELETED',
        #3: 'MOP_MODIFIED'
        if op == 2:
            response_kp = str(keypath).replace('request', 'response')
            state.append(response_kp)
        return ncs.ITER_RECURSE

    # This will run in a separate thread to avoid a transaction deadlock
    def post_iterate(self, state):
        self.log.info('DeleteSubscriber: post_iterate, state=', state)
        #response_kp = state[0]
        # with ncs.maapi.single_read_trans('system', 'system') as trans:
        #     for response_kp in state:
        #         allocation = ncs.maagic.get_node(trans, response_kp)
        #         #allocation.ext_id__release()

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
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('vlan', ServiceCallbacks)

        # Create your subscriber
        self.sub = DeleteSubscriber(app=self)
        self.sub.start()

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.
        self.sub.stop()
        self.log.info('Main FINISHED')
