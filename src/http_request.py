"""
A simpler wrapper around twisted own HTTP request implementation.
Taken mostly from https://gist.github.com/lukemarsden/846545

Did some minor style tweaks and added requests pool.
"""

from twisted.internet.defer import succeed, fail, Deferred
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, connectionDone
from twisted.web.iweb import IBodyProducer
from twisted.web.client import Agent, HTTPConnectionPool
from twisted.web.http_headers import Headers
from zope.interface import implements

agent = Agent(reactor, pool=HTTPConnectionPool(reactor))


class BadReplyError(Exception):
    pass


class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


def http_request(url, data=None, headers=None, method='POST'):
    if not headers:
        headers = {}

    request_defer = agent.request(
        method,
        url,
        Headers(headers),
        StringProducer(data) if data else None)

    def handle_response(response):
        class SimpleReceiver(Protocol):
            def __init__(self, _d):
                self.buf = ''
                self.d = _d

            def dataReceived(self, _data):
                self.buf += _data

            def connectionLost(self, reason=connectionDone):
                self.d.callback(self.buf)

        deferred = Deferred()
        response.deliverBody(SimpleReceiver(deferred))
        deferred.addCallback(handle_body, response.code)

        return deferred

    def handle_body(body, code):
        if code != 200:
            return fail(BadReplyError(body))
        else:
            return succeed(body)

    request_defer.addCallback(handle_response)
    return request_defer
