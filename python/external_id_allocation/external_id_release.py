# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from ncs.dp import Action
import requests
import ipam

class RedeployAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        #if the your actions take more than 240 seconds, increase the action_set_timeout
        #_ncs.dp.action_set_timeout(uinfo,240)
        with ncs.maapi.single_read_trans(uinfo.username, uinfo.context) as trans:
            request = ncs.maagic.get_node(trans, kp)
            #request_name = request.name
            allocating_service = request.allocating_service
            m = ncs.maapi.Maapi()
            self.log.info('action re-deploy-service starting: ', str(kp))
            try:
                service_kpath = m.xpath2kpath(str(allocating_service))
                service = ncs.maagic.get_node(trans, service_kpath, shared=False)
                service.reactive_re_deploy()
                self.log.info('OK did action re-deploy-service: ', str(service_kpath))
            except KeyError:
                self.log.info('ERR action re-deploy-service service in key path: ', str(kp))
            # output.result = ''

class ReleaseAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        #HERE YOU SHOULD DO YOUR EXTERNAL RELEASE
        #if the your actions take more than 240 seconds, increase the action_set_timeout
        #_ncs.dp.action_set_timeout(uinfo,240)
        response_name = ''
        error = ''
        ipam_response = None

        with ncs.maapi.single_read_trans(uinfo.username, uinfo.context) as trans:
            response = ncs.maagic.get_node(trans, kp)
            response_name = response.name

        error = ipam.release(self, response_name)

        with ncs.maapi.single_write_trans(uinfo.username, uinfo.context) as trans:
            response = ncs.maagic.get_node(trans, kp)
            response_name = response.name
            resplist = response._parent
            if input.force_clean:
                print('forceclean')
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

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        #self.register_service('external-id-redeploy-servicepoint', ServiceCallbacks)

        # When using actions, this is how we register them:
        #
        self.register_action('external-id-redeploy-action', RedeployAction)
        self.register_action('external-id-release-action', ReleaseAction)

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
