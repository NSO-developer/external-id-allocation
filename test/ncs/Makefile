all: packages/external-id-allocation packages/vlan

packages/external-id-allocation:  ncs-setup
	rm -rf packages/external-id-allocation
	(cd packages; ln -s ../../../../external-id-allocation .)
	(cd packages/external-id-allocation/src; make all)

packages/vlan:  ncs-setup
	rm -rf packages/vlan
	(cd packages; ln -s ../../package/vlan .)

ncs-setup:
	ncs-setup --package cisco-ios --dest .
	cp -f ncs.conf.with-debug ncs.conf

start:
	`which ncs` || exit 0
	`which ncs-netsim` start || exit 0

stop:
	`which ncs` --stop
	`which ncs-netsim` stop

clean:
	rm -rf README.ncs logs ncs-cdb ncs.conf packages/* scripts state

cli:
	ncs_cli -u admin
