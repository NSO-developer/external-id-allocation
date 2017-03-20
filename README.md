# external-id-allocation
Example of an external ID allocation package for NSO. The code does not go out to any external system for the allocation but the framework is there to easily add that code.

It consists of three actions and two kickers. Should be three but today kickers cant explicitly run on delete so delets are handled in a subscriber.

The three actions are

 * allocate
    does the actual allocation and creates an entry in the response list
 * release
    releases the allocation from the external system and also deletes the response entry for the service in question
 * re-deploy-service
    re-deploys the service that requested the allocation

The two kickers are

 * external-id-allocator
    executes the allocate action when a request is created
* external-id-redeploy
    exectues the re-deploy-service action when a response entry is created

To use it manually (just to show the steps), you need to have a service instance created already.

first create the two kickers
```
ncs_cli -u admin
unhide debug
configure
set external-id-allocation create-kickers
show kickers
commit
```

then create an allocation request (the current example will just created a random intiger). The allocating service needs to be an existing instance

```
set external-id-allocation request service-1 allocating-service /vlan[name=volvo]
commit
```

This will execute the allocation action and populate the response list

```
run show external-id-allocation
external-id-allocation create-kickers
NAME   ALLOCATING SERVICE   ERROR  ID
----------------------------------------
volvo  /vlan[name='volvo']  -      152

```

the allocate action can be manually executed if needed

```
request external-id-allocation request volvo allocate
```

to release the id the release action is executed
```
request external-id-allocation response volvo release
```
when the allocation is done the service should be re-deployed
```
request external-id-allocation response volvo re-deploy-service
```

And then putting the whole thing together with a service you let the service create the allocation request and then the kickers (and the subscriber) autmatically handles the rest.

Here is an example that populates the request, it will then create the switchport if the response has been created and also set allocated VLAN-id in trunk allowed vlans

```XML
<config-template xmlns="http://tail-f.com/ns/config/1.0" servicepoint="vlan">
  <external-id-allocation xmlns="http://example.com/external-id-allocation">
    <request>
      <name>{/name}</name>
      <allocating-service xmlns:vlan="http://com/example/vlan">/vlan:vlan[vlan:name='{/name}']</allocating-service>
    </request>
  </external-id-allocation>
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device>
      <name>{/device}</name>
      <config>
      <interface xmlns="urn:ios">
        <FastEthernet>
          <name>1/0</name>
          <switchport when="{../ext-id:external-id-allocation/ext-id:response[ext-id:name=/name]/ext-id:id}">
            <mode>
              <trunk/>
            </mode>
            <trunk>
              <allowed>
                <vlan>
                  <vlans>{../ext-id:external-id-allocation/ext-id:response[ext-id:name=/name]/ext-id:id}</vlans>
                </vlan>
              </allowed>
            </trunk>
          </switchport>
        </FastEthernet>
      </interface>
      </config>
    </device>
  </devices>
</config-template>
```
