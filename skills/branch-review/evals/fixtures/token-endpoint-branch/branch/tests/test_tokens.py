from app.store import Store
from app import tokens


def test_issue_and_validate():
    store = Store()
    token = tokens.issue_token(store, "ada")
    assert tokens.validate_token(store, token) == "ada"
