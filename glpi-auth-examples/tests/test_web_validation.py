import json
import os
import importlib
from web import app as webapp

def test_csrf_protection():
    client = webapp.app.test_client()
    # no csrf
    res = client.post('/login', json={'login':'u', 'password':'password'})
    assert res.status_code == 400

def test_field_validation():
    client = webapp.app.test_client()
    t = client.get('/csrf').get_json()['token']
    # missing fields
    res = client.post('/login', headers={'X-CSRF-Token': t}, json={'login':'', 'password':''})
    j = res.get_json()
    assert res.status_code == 400
    assert 'login' in j['errors'] and 'password' in j['errors']

def test_password_min_length():
    client = webapp.app.test_client()
    t = client.get('/csrf').get_json()['token']
    res = client.post('/login', headers={'X-CSRF-Token': t}, json={'login':'u', 'password':'short'})
    assert res.status_code == 400

