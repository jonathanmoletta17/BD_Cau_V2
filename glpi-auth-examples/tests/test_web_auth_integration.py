import json
from web import app as webapp
import glpi_auth

def test_login_success(monkeypatch):
    client = webapp.app.test_client()
    t = client.get('/csrf').get_json()['token']

    def fake_basic(login, password, get_full_session=False):
        return 'TOKEN123456'

    def fake_full(session_token):
        return {'session': {'glpifriendlyname': 'User X'}}

    def stub_basic(self, l, p, get_full_session=False):
        return fake_basic(l, p, get_full_session)
    monkeypatch.setattr(glpi_auth.AuthManager, 'glpi_init_session_basic_header', stub_basic)
    monkeypatch.setattr(glpi_auth.AuthManager, 'get_my_user', lambda self, st: fake_full(st))

    res = client.post('/login', headers={'X-CSRF-Token': t}, json={'login':'user','password':'passwordOK'})
    j = res.get_json()
    assert res.status_code == 200
    assert j['ok'] is True
    assert j['user'] == 'User X'

def test_login_failure(monkeypatch):
    client = webapp.app.test_client()
    t = client.get('/csrf').get_json()['token']

    def stub_fail(self, l, p, get_full_session=False):
        return None
    monkeypatch.setattr(glpi_auth.AuthManager, 'glpi_init_session_basic_header', stub_fail)

    res = client.post('/login', headers={'X-CSRF-Token': t}, json={'login':'user','password':'passwordOK'})
    assert res.status_code == 401
