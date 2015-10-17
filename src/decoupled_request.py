import urllib

import treq
from twisted.internet import reactor
from twisted.internet.defer import CancelledError
from twisted.internet.task import deferLater

from twisted.python import log

from src.config import BACKEND_REQUEST_TIMEOUT, BACKEND_URL


class DecoupledRequest(object):
    def __init__(self, factory, _id, client_request):
        self.factory = factory
        self.id = _id
        self.client_request = client_request

        self.request_defer = self.do_request()

        # save timeout_Defer for later to be cancelled in case callback got received in time
        self.timeout_defer = deferLater(reactor, BACKEND_REQUEST_TIMEOUT, self.on_timeout)
        self.timeout_defer.addErrback(self.on_timeout_error)

        # if client disconnects (close browser) then cancel all activity
        client_request.notifyFinish().addErrback(self.on_client_disconnect)

    def create_url(self):
        args = self.client_request.args
        args['request_id'] = [self.id]
        query_string = urllib.urlencode(self.client_request.args, True)
        return "%s?%s" % (BACKEND_URL, query_string)

    @staticmethod
    def on_timeout_error(error):
        if not isinstance(error.value, CancelledError):
            raise error.value

    def on_client_disconnect(self, _):
        self.log('client disconnected, destroying request')

        self.timeout_defer.cancel()
        self.request_defer.cancel()
        self.destroy()

    def do_request(self):
        self.log('requesting backend')

        d = treq.get(self.create_url())
        d.addCallback(self.on_request_success)
        d.addErrback(self.on_request_error)
        return d

    def on_request_success(self, response):
        if response.code == 200:
            self.log('request successful. waiting for callback')
        else:
            return treq.content(response).addCallback(self.print_error, 502)

    def on_request_error(self, failure):
        self.log('request error')
        self.print_error(failure.getErrorMessage(), 503)
        self.destroy()

    def print_error(self, msg, code):
        self.client_request.setResponseCode(code)
        self.client_request.write("Backend failed with: %s" % msg)
        self.client_request.finish()

    def on_timeout(self):
        self.log('got timeout')

        self.request_defer.cancel()

        self.client_request.setResponseCode(503)
        self.client_request.write('Response took longer than %s sec, cancelled. '
                                  'Please try again later.' % BACKEND_REQUEST_TIMEOUT)
        self.client_request.finish()

        self.destroy()

    def notify(self, callback_request):
        value = callback_request.content.getvalue()

        self.log('got callback: %s' % value)

        self.client_request.write(value)
        self.client_request.finish()

        self.destroy()

    def destroy(self):
        self.timeout_defer.cancel()
        self.factory.remove_by_id(self.id)

    def log(self, msg):
        log.msg('request %s: %s' % (self.id, msg))
