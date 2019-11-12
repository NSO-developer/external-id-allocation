import requests


def request(self, request_name):
    error = ''
    allocated_id = ''
    ipam_response = None

    try:
        ipam_response = requests.get("http://localhost:8091/id/request/" + request_name)
        if ipam_response.status_code != 200:
            self.log.info('ipam server HTTP error: ' + str(ipam_response.status_code))
            error += 'ipam server HTTP error: ' + str(ipam_response.status_code)
    except requests.exceptions.ConnectionError as e:
        # Maybe set up for a retry, or continue in a retry loop
        error += 'Connection error'
        self.log.info('Connection error exception: ' + str(e))
    except requests.exceptions.Timeout as e:
        # Maybe set up for a retry, or continue in a retry loop
        error += 'Connection timeout'
        self.log.info('Connection timeout exception: ' + str(e))
    except requests.exceptions.TooManyRedirects as e:
        # Tell the user their URL was bad and try a different one
        error += 'Bad URL'
        self.log.info('Allocation request exception: ' + str(e))
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        error += 'Allocation request exception: ' + str(e)
        self.log.info('Allocation request exception: ' + str(e))

    if not error:
        allocated_id = ipam_response.content.decode('utf-8')

    return str(allocated_id), error


def release(self, response_name):
    error = ''
    ipam_response = None
    try:
        ipam_response = requests.get("http://localhost:8091/id/release/" + response_name)
        if ipam_response.status_code != 200:
            self.log.info('ipam server HTTP error: ' + str(ipam_response.status_code))
            error += 'ipam server HTTP error: ' + str(ipam_response.status_code)
    except requests.exceptions.ConnectionError as e:
        # Maybe set up for a retry, or continue in a retry loop
        error += 'Connection error'
        self.log.info('Connection error exception: ' + str(e))
    except requests.exceptions.Timeout as e:
        # Maybe set up for a retry, or continue in a retry loop
        error += 'Connection timeout'
        self.log.info('Connection timeout exception: ' + str(e))
    except requests.exceptions.TooManyRedirects as e:
        # Tell the user their URL was bad and try a different one
        error += 'Bad URL'
        self.log.info('Allocation request exception: ' + str(e))
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        error += 'Allocation request exception: ' + str(e)
        self.log.info('Allocation request exception: ' + str(e))
    return error
