#!/usr/bin/env python
import web
import xml.etree.ElementTree as ET
import os
import random

os.environ["PORT"] = "8091"

tree = ET.parse('ipam-data.xml')
root = tree.getroot()

urls = (
    '/id/request/(.*)', 'request_id',
    '/id/release/(.*)', 'release_id'
)

allocations = {}
for id in root:
    allocations[id.attrib['name']] = id.attrib['id']

app = web.application(urls, globals())

class request_id:
    def GET(self, request_name):
        # for id in root:
        #     print('request name: ' + request_name)
        #     if id.attrib['name'] == request_name:
        #         print('request name: ' + request_name + ' return id: ' + id)
        #         return str(id.attrib['id'])
        #if not prepopulated, generate a new random number

        if allocations.has_key(request_name):
            print('request: ' + request_name + ' allocated: ' + str(allocations[request_name]))
            return allocations[request_name]
        else:
            allocations[request_name] = random.randint(1001, 2000)
            print('request: ' + request_name + ' allocated: ' + str(allocations[request_name]))
            return allocations[request_name]

    def POST(self, request_name):
        for id in root:
            if id.attrib['name'] == request_name:
                return str(id.attrib['id'])

class release_id:
    def GET(self, request_name):
        print('released: ' + request_name + ' id: ' + str(allocations[request_name]))
        del allocations[request_name]
        return str('OK')

if __name__ == "__main__":
    app.run()
