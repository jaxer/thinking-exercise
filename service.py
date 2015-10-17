from twisted.application import service, internet

from twisted.web import server
from twisted.web.resource import Resource

from src.callback_resource import CallbackResource

from src.exported_resource import ExportedResource


def get_server():
    service_method = Resource()
    service_method.putChild('method', ExportedResource())

    callback_method = Resource()
    callback_method.putChild('method', CallbackResource())

    root = Resource()
    root.putChild('service', service_method)
    root.putChild('callback.service', callback_method)

    return internet.TCPServer(8080, server.Site(root))


application = service.Application("Thinking exercise: service")
get_server().setServiceParent(application)
