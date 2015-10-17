from datetime import datetime
import json

import treq

from twisted.internet import reactor
from twisted.internet.task import deferLater
from twisted.web.client import Agent
from twisted.python import log
from twisted.web.resource import Resource

from src.config import SERVICE_CALLBACK_URL


class DelayFormatError(Exception):
    pass


class BackendResource(Resource):
    isLeaf = True

    def __init__(self):
        Resource.__init__(self)
        self.agent = Agent(reactor)

    @staticmethod
    def compose_callback_data(request_id):
        return json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'response': 'dummy data for request %s' % request_id
        })

    def do_callback(self, request_id):
        d = treq.post("%s?request_id=%s" % (SERVICE_CALLBACK_URL, request_id),
                      self.compose_callback_data(request_id))
        d.addCallback(self.on_callback_success, request_id)
        d.addErrback(self.on_callback_error, request_id)
        return d

    @staticmethod
    def on_callback_error(error, request_id):
        # just give up. in real system, there should probably be done something else here.
        # i.e reschedule few times and notify somebody if still fails.
        log.msg('%s: POST failed (%s)' % (request_id, error.getErrorMessage()))

    @staticmethod
    def on_callback_success(response, request_id):
        log.msg('%s: POST successful' % request_id)

    def schedule_callback(self, delay, request_number):
        d = deferLater(reactor, delay, lambda: request_number)
        d.addCallback(self.do_callback)
        return d

    @staticmethod
    def parse_delay(request):
        """
        Extracts delay from URI, parses and returns it.
        Can fire DelayFormatException.
        """
        try:
            if 'delay' in request.args:
                delay = float(request.args['delay'][0])
            else:
                delay = 0
        except ValueError:
            raise DelayFormatError('not a number')

        if delay < 0:
            raise DelayFormatError('negative')

        return delay

    def render_GET(self, request):
        try:
            delay = self.parse_delay(request)

        except DelayFormatError as e:
            request.setResponseCode(502)
            message = "Delay is %s" % e.message

        else:
            message = ("Request scheduled. "
                       "Callback will trigger in %s seconds" % delay)

            if 'request_id' in request.args:
                request_id = request.args['request_id'][0]
            else:
                request_id = 'no-request-id'

            self.schedule_callback(delay, request_id)

        log.msg(message)

        return message
