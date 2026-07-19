from app.store import Store


def test_put_then_get():
    store = Store()
    store.put("k", "v")
    assert store.get("k") == "v"
