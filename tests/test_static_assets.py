"""Tests for static frontend assets served by FastAPI.

Verifies that the HTML page, CSS, JS, and favicon are all
reachable and return the expected content types.
"""

from __future__ import annotations


def test_ui_page_returns_html(client):
    response = client.get("/ui")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_ui_page_contains_predict_form(client):
    response = client.get("/ui")
    assert response.status_code == 200
    assert '<form id="predict-form"' in response.text


def test_static_css_reset(client):
    response = client.get("/static/css/reset.css")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")


def test_static_js_app(client):
    response = client.get("/static/js/app.js")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/javascript") or response.headers["content-type"].startswith("application/javascript")


def test_static_favicon(client):
    response = client.get("/static/assets/favicon.svg")
    assert response.status_code == 200
    assert "image/svg+xml" in response.headers["content-type"]
