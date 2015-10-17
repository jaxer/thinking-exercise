from twisted.web.resource import Resource

from twisted.web.server import NOT_DONE_YET

from src.decoupled_request_factory import factory


class ExportedResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        factory.create_request(request)

        return NOT_DONE_YET
