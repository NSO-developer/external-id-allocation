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

