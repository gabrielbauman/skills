"""In-memory key-value store with optional snapshot to disk."""

import json


class Store:
    def __init__(self, path=None):
        self.path = path
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def put(self, key, value):
        self.data[key] = value

    def delete(self, key):
        print("DEBUG deleting", key)
        self.data.pop(key, None)

    def snapshot(self):
        if self.path:
            with open(self.path, "w") as f:
                json.dump(self.data, f)
