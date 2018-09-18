# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.dp import Action
import ipam


class RedeployAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: {}'.format(name))
        # if the your actions take more than 240 seconds, increase the action_set_timeout
        # _ncs.dp.action_set_timeout(uinfo,240)
        with ncs.maapi.single_read_trans(uinfo.username, uinfo.context) as trans:
            request = ncs.maagic.get_node(trans, kp)
            # request_name = request.name
            allocating_service = request.allocating_service
            m = ncs.maapi.Maapi()
            self.log.info('action re-deploy-service starting: {}'.format(str(kp)))
            try:
                service_kpath = m.xpath2kpath(str(allocating_service))
                service = ncs.maagic.get_node(trans, service_kpath, shared=False)
                input = service.reactive_re_deploy.get_input()
                # Do the reactive-re-deploy synchronous, no input needed if you want to run it asynchronous
                input.sync.create()
                service.reactive_re_deploy(input)
                #service.reactive_re_deploy()
                #service.re_deploy()
                self.log.info('OK did action re-deploy-service: {}'.format(str(service_kpath)))
            except KeyError:
                self.log.info('ERR action re-deploy-service service in keypath: {}'.format(str(kp)))
            except Exception as err:
                self.log.info('ERR unknown error: {}'.format(err))


class ReleaseAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        # HERE YOU SHOULD DO YOUR EXTERNAL RELEASE
        # if your action take more than 240 seconds, increase the action_set_timeout
        # _ncs.dp.action_set_timeout(uinfo, 240)
        response_name = ''
        error = ''
        use_random = False
        with ncs.maapi.single_read_trans(uinfo.username, uinfo.context) as trans:
            response = ncs.maagic.get_node(trans, kp)
            response_name = response.name
            if response._parent._parent.use_random:
                use_random = True

        # release with the ipam server, if we are using the random value we dont
        # need to contact anything else
        if not use_random:
            error = ipam.release(self, response_name)

        with ncs.maapi.single_write_trans(uinfo.username, uinfo.context) as trans:
            response = ncs.maagic.get_node(trans, kp)
            response_name = response.name
            resplist = response._parent
            if input.force_clean:
                del resplist[response_name]
            elif not error:
                    del resplist[response_name]
            else:
                response.error = error
            trans.apply()
            self.log.info('action release id: ', str(response_name))


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main external-id-redeploy RUNNING')
        #
        self.register_action('external-id-redeploy-action', RedeployAction)
        self.register_action('external-id-release-action', ReleaseAction)

    def teardown(self):

        self.log.info('Main FINISHED')
