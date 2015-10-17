from StringIO import StringIO
from unittest import TestCase

from twisted.web.test._util import _render
from twisted.web.test.requesthelper import DummyRequest

from src.callback_resource import CallbackResource
from src.decoupled_request import DecoupledRequest
from src.decoupled_request_factory import DecoupledRequestFactory


class CallbackResourceTest(TestCase):
    def setUp(self):
        self.resource = CallbackResource()
        self.resource.factory = DecoupledRequestFactory()
        self.request = DummyRequest([''])
        self.request.method = 'POST'
        self.request.content = StringIO()

    def test_no_request_id(self):
        def on_rendered(_):
            self.assertEqual(self.request.responseCode, 503)
            self.assertEqual(['No request_id given'], self.request.written)

        return _render(self.resource, self.request).addCallback(on_rendered)

    def test_unknown_request_id(self):
        self.request.addArg('request_id', 'xxx')

        def on_rendered(_):
            self.assertEqual(self.request.responseCode, 503)
            self.assertEqual(['Request not found'], self.request.written)

        return _render(self.resource, self.request).addCallback(on_rendered)

    def test_success(self):
        self.request.addArg('request_id', 'xxx')
        self.resource.factory.requests['xxx'] = DecoupledRequest(
            self.resource.factory, 'xxx', DummyRequest(['']))

        def on_rendered(_):
            self.assertEqual(['ok'], self.request.written)

        return _render(self.resource, self.request).addCallback(on_rendered)
