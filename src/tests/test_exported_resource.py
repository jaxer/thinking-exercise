from StringIO import StringIO
from unittest import TestCase

from mock import patch

from twisted.web.test._util import _render

from twisted.web.test.requesthelper import DummyRequest

from src.decoupled_request_factory import DecoupledRequestFactory
from src.exported_resource import ExportedResource


class ExportedResourceTest(TestCase):
    def setUp(self):
        self.resource = ExportedResource()
        self.resource.factory = DecoupledRequestFactory()
        self.request = DummyRequest([''])

    def test_success(self):
        def on_rendered(_):
            self.assertEqual(['backend reply'], self.request.written)

        d = _render(self.resource, self.request).addCallback(on_rendered)

        callback_request = DummyRequest([''])
        callback_request.content = StringIO('backend reply')

        self.resource.factory.requests.values()[0].notify(callback_request)
        return d
