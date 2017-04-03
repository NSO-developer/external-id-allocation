all: netsim start

#NCS runtime folder
NCS_RUN = ../../../ncs

build: all

#ncs-netsim add-to-network packages/cisco-ios 1 c;
netsim:
	(cd $(NCS_RUN); \
	if [ ! -d netsim ]; then \
		ncs-netsim create-device cisco-ios c0; \
	else \
		ncs-netsim add-device cisco-ios c0; \
	fi)
	(cd $(NCS_RUN); ncs-netsim ncs-xml-init > ncs-cdb/cisco.xml)

start:
	(cd $(NCS_RUN); \
	 ncs-netsim start)
	#echo "request packages reload" | ncs_cli -u admin
	@echo "cisco-ios_netsim_started"
	(cd $(NCS_RUN); \
	 ${NCS_DIR}/bin/ncs_load -l -m -F x -u admin -g admin ncs-cdb/cisco.xml)

stop:
	(cd $(NCS_RUN); \
	ncs-netsim stop c0)

clean:
	(cd $(NCS_RUN); \
	ncs-netsim stop c0; \
	rm -rf ncs-cdb/cisco.xml; \
	rm -rf netsim; \
	rm -rf packages/cisco-ios)

test:
	~/stash.tail-f.com/lux/bin/lux run.lux

