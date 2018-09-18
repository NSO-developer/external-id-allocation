all:  ncs-setup packages/external-id-allocation packages/vlan netsim

build: all

packages/external-id-allocation:
	(cd packages; ln -s ../../../../external-id-allocation .)
	(cd packages/external-id-allocation/src; make all)

packages/vlan:
	(cd packages; ln -s ../../package/vlan .)
	(cd packages/vlan/src; make all)

ncs-setup:
	ncs-setup --no-netsim --ned-package cisco-ios-cli-3.8 --dest .
	cp -f ncs.conf.with-debug ncs.conf

netsim:
	if [ ! -d netsim ]; then \
		ncs-netsim create-device cisco-ios-cli-3.8 c0; \
	else \
		ncs-netsim add-device cisco-ios-cli-3.8 c0; \
	fi
	ncs-netsim ncs-xml-init > ncs-cdb/cisco.xml

start-ipam:
	if [ -e "../ipam.pid" ]; then (kill `cat ../ipam.pid` && rm ../ipam.pid); fi
	(cd ../;python ipam-server.py > /dev/null 2>&1 & echo $$! > ipam.pid)

start:
	`which ncs` || exit 0
	`which ncs-netsim` start || exit 0

stop:
	`which ncs` --stop
	`which ncs-netsim` stop
	if [ -e "../ipam.pid" ]; then (kill `cat ../ipam.pid` && rm ../ipam.pid); fi


clean:
	if [ -d "packages/vlan/src" ]; then (cd packages/vlan/src; make clean); fi
	if [ -d "packages/external-id-allocation/src" ]; then (cd packages/external-id-allocation/src; make clean); fi
	rm -rf README.ncs logs ncs-cdb ncs.conf packages/* scripts state netsim ../ipam-server.log ../ipam.pid

cli:
	ncs_cli -u admin
