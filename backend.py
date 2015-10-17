from twisted.application import service, internet

from twisted.web import server
from twisted.web.resource import Resource

from src.backend_resource import BackendResource


def get_server():
    service_method = Resource()
    service_method.putChild('method', BackendResource())

    root = Resource()
    root.putChild('backend-service', service_method)

    return internet.TCPServer(8081, server.Site(root))


application = service.Application("Thinking exercise: backend")
get_server().setServiceParent(application)
