#!/usr/bin/env python
import web
import xml.etree.ElementTree as ET
import os
import random
import logging

os.environ["PORT"] = "8091"

urls = (
    '/id/request/(.*)', 'request_id',
    '/id/release/(.*)', 'release_id'
)

logging.basicConfig(filename='ipam-server.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s line: %(lineno)d - %(message)s')
tree = ET.parse('ipam-data.xml')
root = tree.getroot()

allocations = {}
pre_allocations = {}
for id in root:
    name = id.attrib['name']
    id = id.attrib['id']
    print('attrib:' + name)
    pre_allocations[name] = id
    logging.info('Loading pre-allocation {} id {}'.format(name, id))

app = web.application(urls, globals())

class request_id:
    def GET(self, request_name):
        if pre_allocations.has_key(request_name):
            logging.info('request: ' + request_name + ' pre allocated: ' + str(pre_allocations[request_name]))
            allocations[request_name] = pre_allocations[request_name]
            return allocations[request_name]
        elif allocations.has_key(request_name):
            logging.info('request: ' + request_name + ' already allocated: ' + str(allocations[request_name]))
            return allocations[request_name]
        else:
            allocations[request_name] = random.randint(1001, 1999)
            logging.info('request: ' + request_name + ' randomly allocated: ' + str(allocations[request_name]))
            return allocations[request_name]

    def POST(self, request_name):
        for id in root:
            if id.attrib['name'] == request_name:
                return str(id.attrib['id'])

class release_id:
    def GET(self, request_name):
        if allocations.has_key(request_name):
            logging.info('released: ' + request_name + ' id: ' + str(allocations[request_name]))
            del allocations[request_name]
        else:
            logging.info('tried to release ' + request_name + ' but no allocation was found')
            for requests in allocations:
                print("found allocations " + requests)
        return str('OK')

if __name__ == "__main__":
    app.run()
