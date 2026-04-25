"""Tests for CSV export endpoints."""

import csv
from io import StringIO

from fastapi import status
from fastapi.testclient import TestClient


def _read_csv_rows(response_text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(StringIO(response_text))
    return list(reader)


class TestCsvExports:
    def test_export_requires_auth(self, client: TestClient):
        response = client.get("/api/v0/exports/products.csv")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_forbidden_non_admin(self, client: TestClient, user_token: str):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/exports/products.csv", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only admins can export data" in response.json()["detail"]

    def test_export_products_csv_admin(self, client: TestClient, admin_token: str, test_product):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v0/exports/products.csv", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert "text/csv" in response.headers.get("content-type", "")
        assert "products.csv" in response.headers.get("content-disposition", "")

        rows = _read_csv_rows(response.text)
        assert len(rows) >= 1
        assert "product_name" in rows[0]
        assert any(row["product_name"] == test_product.product_name for row in rows)

    def test_export_users_csv_admin_excludes_password(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v0/exports/users.csv", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        rows = _read_csv_rows(response.text)
        assert len(rows) >= 1
        assert "User_password" not in rows[0]
        assert "User_mail" in rows[0]

    def test_export_meal_logs_csv_empty_has_header_only(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v0/exports/meal-logs.csv", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        lines = [line for line in response.text.splitlines() if line.strip()]
        assert len(lines) == 1
        assert lines[0].startswith("Log_ID,User_ID,Product_ID,Log_Date")
