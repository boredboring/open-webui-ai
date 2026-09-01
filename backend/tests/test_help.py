from fastapi import FastAPI
from fastapi.testclient import TestClient

from open_webui.routers.help import router


def make_client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_get_help_documentation_returns_markdown():
    client = make_client()

    response = client.get('/')

    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Open WebUI 项目说明文档'
    assert '项目概述' in data['content']
    assert 'Open WebUI' in data['content']
