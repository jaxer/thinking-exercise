from twisted.python import log
from twisted.web import resource

from src.decoupled_request_factory import factory


class CallbackResource(resource.Resource):
    isLeaf = True

    factory = factory

    def render_POST(self, request):
        _id = request.args.get('request_id')

        if not _id:
            log.err('callback received without request_id')
            request.setResponseCode(503)
            return 'No request_id given'
        else:
            _id = _id[0]

        decoupled_request = self.factory.get_by_id(_id)

        if not decoupled_request:
            log.err('callback received for unknown request_id: %s' % _id)
            request.setResponseCode(503)
            return 'Request not found'

        log.msg('callback received')

        decoupled_request.notify(request)

        return "ok"
