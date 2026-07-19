import io

from api import upload


class FakeStore:
    def __init__(self):
        self.saved = {}

    def put(self, key, value):
        self.saved[key] = value


def test_upload_stores_body():
    store = FakeStore()
    request = {
        "stream": io.BytesIO(b"hello"),
        "filename": "greeting.txt",
        "store": store,
    }
    assert upload.handle_upload(request) == {"status": 201}
    assert store.saved["greeting.txt"] == b"hello"
