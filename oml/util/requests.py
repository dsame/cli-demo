from oml.exceptions import OMLException


def handle_response(func):
    def _handle_response(*args, **kwargs):
        res = func(*args, **kwargs)
        if res.status_code == 200 or res.status_code == 201:
            return res.json()
        else:
            raise OMLException(res.text)
    return _handle_response
