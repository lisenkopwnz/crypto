from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_get_currency_success():
    mock_data = [
        {"ticker": "btc_usd", "price": 63083.39, "updated": 1785574860},
        {"ticker": "btc_usd", "price": 63083.36, "updated": 1785574861}
    ]

    with patch('app.api.v1.endpoints.currency_information.CurrencyDBAdapter') as MockAdapter:
        mock_instance = MockAdapter.return_value
        mock_instance.get_all_by_ticker.return_value = mock_data

        response = client.get("/api/v1/currency_information/?ticker=btc_usd")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["ticker"] == "btc_usd"
        assert data[0]["price"] == 63083.39


def test_get_currency_empty():
    with patch('app.api.v1.endpoints.currency_information.CurrencyDBAdapter') as MockAdapter:
        mock_instance = MockAdapter.return_value
        mock_instance.get_all_by_ticker.return_value = []

        response = client.get("/api/v1/currency_information/?ticker=btc_usd")

        assert response.status_code == 200
        assert response.json() == []


def test_get_currency_with_date():
    mock_data = [
        {"ticker": "btc_usd", "price": 63083.39, "updated": 1785574860}
    ]

    with patch('app.api.v1.endpoints.currency_information.CurrencyDBAdapter') as MockAdapter:
        mock_instance = MockAdapter.return_value
        mock_instance.get_all_by_ticker.return_value = mock_data

        response = client.get("/api/v1/currency_information/?ticker=btc_usd&on_date=2026-08-01")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ticker"] == "btc_usd"


def test_get_latest_price_success():
    mock_data = {"ticker": "eth_usd", "price": 1868.11, "updated": 1785574861}

    with patch('app.api.v1.endpoints.currency_information.CurrencyDBAdapter') as MockAdapter:
        mock_instance = MockAdapter.return_value
        mock_instance.get_last_price.return_value = mock_data

        response = client.get("/api/v1/currency_information/latest-price/?ticker=eth_usd")

        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "eth_usd"
        assert data["price"] == 1868.11
