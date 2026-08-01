#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_server(db_path: str):
    os.environ['NEWSLETTER_DB'] = db_path
    os.environ['ANALYTICS_SECRET'] = 'test-secret-do-not-use'
    spec = importlib.util.spec_from_file_location('nk_newsletter_test', ROOT / 'newsletter/server.py')
    if spec is None or spec.loader is None:
        raise RuntimeError('Nelze načíst newsletter/server.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request(module, path: str, method: str = 'GET', payload: dict | None = None, cookie: str = '', ua: str = 'PollTest/1'):
    body = json.dumps(payload or {}).encode('utf-8') if payload is not None else b''
    captured: dict[str, object] = {}

    def start(status, headers):
        captured['status'] = status
        captured['headers'] = headers

    if '?' in path:
        path_info, query = path.split('?', 1)
    else:
        path_info, query = path, ''
    env = {
        'PATH_INFO': path_info,
        'QUERY_STRING': query,
        'REQUEST_METHOD': method,
        'CONTENT_LENGTH': str(len(body)),
        'CONTENT_TYPE': 'application/json',
        'wsgi.input': io.BytesIO(body),
        'REMOTE_ADDR': '198.51.100.10',
        'HTTP_USER_AGENT': ua,
        'HTTP_COOKIE': cookie,
    }
    response = b''.join(module.app(env, start))
    data = json.loads(response.decode('utf-8')) if response else {}
    headers = {str(k).lower(): str(v) for k, v in captured.get('headers', [])}
    return str(captured.get('status', '')), headers, data


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        module = load_server(str(Path(tmp) / 'poll.sqlite3'))
        poll = 'test-visible-counts'

        status, headers, first = request(module, '/poll/vote', 'POST', {'pollId': poll, 'choice': 'vyssi'})
        assert status.startswith('200'), (status, first)
        assert first['ok'] is True and first['accepted'] is True
        assert first['selected'] == 'vyssi'
        assert first['total'] == 1 and first['counts']['vyssi'] == 1
        assert first['percentages']['vyssi'] == 100.0
        set_cookie = headers.get('set-cookie', '')
        assert set_cookie.startswith('nk_poll_device='), headers
        cookie = set_cookie.split(';', 1)[0]

        status, _, second = request(module, '/poll/vote', 'POST', {'pollId': poll, 'choice': 'soucasny'}, cookie=cookie, ua='PollTest/changed-agent')
        assert status.startswith('200'), (status, second)
        assert second['accepted'] is False and second['selected'] == 'vyssi'
        assert second['total'] == 1 and second['counts']['vyssi'] == 1

        status, _, visible = request(module, f'/poll/results?poll={poll}', cookie=cookie)
        assert status.startswith('200'), (status, visible)
        assert visible['ok'] is True and visible['selected'] == 'vyssi'
        assert visible['total'] == 1 and visible['counts']['vyssi'] == 1

        status, _, third = request(module, '/poll/vote', 'POST', {'pollId': poll, 'choice': 'podle-mista'}, ua='AnotherDevice/1')
        assert status.startswith('200'), (status, third)
        assert third['accepted'] is True and third['total'] == 2
        assert third['counts']['vyssi'] == 1 and third['counts']['podle-mista'] == 1
        assert third['percentages']['vyssi'] == 50.0
        assert third['percentages']['podle-mista'] == 50.0

    site = (ROOT / 'site.js').read_text(encoding='utf-8')
    assert '/api/newsletter/poll/vote' in site
    assert '/api/newsletter/poll/results' in site
    assert 'Průběžné výsledky' in site
    assert 'poll-result-value' in site
    print('Hlasování, zákaz druhého hlasu i viditelné výsledky fungují.')


if __name__ == '__main__':
    main()
