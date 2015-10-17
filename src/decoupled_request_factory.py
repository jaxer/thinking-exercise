import uuid

from src.decoupled_request import DecoupledRequest


class DecoupledRequestFactory(object):
    def __init__(self):
        self.requests = dict()

    def create_request(self, client_request):
        _id = str(uuid.uuid4())
        request = DecoupledRequest(self, _id, client_request)
        self.requests[_id] = request

    def get_by_id(self, _id):
        return self.requests.get(_id)

    def remove_by_id(self, _id):
        self.requests.pop(_id, None)


# create a singleton for holding all ongoing requests
factory = DecoupledRequestFactory()
