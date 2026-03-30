"""Tests for product endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.product import Product
from src.models.user import User


class TestCreateProduct:
    """Tests for product creation endpoint."""
    
    def test_create_product_success_admin(self, client: TestClient, admin_token: str):
        """Test admin can create products."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v0/products/",
            json={
                "product_name": "Chicken Breast",
                "product_kcal": 165.0,
                "product_protein": 31.0,
                "product_carbs": 0.0,
                "product_fat": 3.6,
                "product_fiber": 0.0,
                "product_sugar": 0.0,
            },
            headers=headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_name"] == "Chicken Breast"
        assert data["product_kcal"] == 165.0
        assert "Product_ID" in data
        assert "created_at" in data

    def test_create_product_forbidden_non_admin(self, client: TestClient, user_token: str):
        """Test regular user cannot create products."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(
            "/api/v0/products/",
            json={
                "product_name": "Test Product",
                "product_kcal": 100.0,
            },
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only admins can manage products" in response.json()["detail"]
    
    def test_create_product_unauthorized(self, client: TestClient):
        """Test creating product without authentication fails."""
        response = client.post(
            "/api/v0/products/",
            json={
                "product_name": "Test Product",
                "product_kcal": 100.0,
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_product_minimal_admin(self, client: TestClient, admin_token: str):
        """Test admin can create product with minimal data."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v0/products/",
            json={
                "product_name": "Apple",
            },
            headers=headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_name"] == "Apple"
        assert data["product_kcal"] is None
    
    def test_create_product_missing_name_admin(self, client: TestClient, admin_token: str):
        """Test creating product without name fails for admin too."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v0/products/",
            json={
                "product_kcal": 100.0,
            },
            headers=headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGetProducts:
    """Tests for getting products endpoint."""
    
    def test_get_products_unauthorized(self, client: TestClient):
        """Test getting products without authentication fails."""
        response = client.get("/api/v0/products/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_products_success(self, client: TestClient, user_token: str, test_product: Product):
        """Test getting products list."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/products/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        product_names = [p["product_name"] for p in data]
        assert test_product.product_name in product_names
    
    def test_get_products_pagination(self, client: TestClient, user_token: str, db: Session):
        """Test getting products with pagination."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Create multiple products
        for i in range(5):
            product = Product(product_name=f"Product {i}")
            db.add(product)
        db.commit()
        
        # Test with limit
        response = client.get("/api/v0/products/?limit=2", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2
    
    def test_get_products_with_skip(self, client: TestClient, user_token: str, db: Session):
        """Test getting products with skip parameter."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Create multiple products
        for i in range(3):
            product = Product(product_name=f"Product {i}")
            db.add(product)
        db.commit()
        
        response = client.get("/api/v0/products/?skip=1&limit=10", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2


class TestGetProductById:
    """Tests for getting product by ID."""
    
    def test_get_product_success(self, client: TestClient, user_token: str, test_product: Product):
        """Test getting a product by ID."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/api/v0/products/{test_product.Product_ID}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["Product_ID"] == test_product.Product_ID
        assert data["product_name"] == test_product.product_name
    
    def test_get_product_not_found(self, client: TestClient, user_token: str):
        """Test getting non-existent product fails."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/products/99999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Product not found" in response.json()["detail"]
    
    def test_get_product_unauthorized(self, client: TestClient, test_product: Product):
        """Test getting product without authentication fails."""
        response = client.get(f"/api/v0/products/{test_product.Product_ID}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateProduct:
    """Tests for updating product endpoint."""
    
    def test_update_product_success_admin(self, client: TestClient, admin_token: str, test_product: Product):
        """Test admin can update products."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.put(
            f"/api/v0/products/{test_product.Product_ID}",
            json={
                "product_name": "Updated Product",
                "product_kcal": 200.0,
                "product_protein": 25.0,
            },
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["product_name"] == "Updated Product"
        assert data["product_kcal"] == 200.0

    def test_update_product_forbidden_non_admin(self, client: TestClient, user_token: str, test_product: Product):
        """Test regular user cannot update products."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.put(
            f"/api/v0/products/{test_product.Product_ID}",
            json={
                "product_name": "Updated Product",
            },
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only admins can manage products" in response.json()["detail"]
    
    def test_update_product_unauthorized(self, client: TestClient, test_product: Product):
        """Test updating product without authentication fails."""
        response = client.put(
            f"/api/v0/products/{test_product.Product_ID}",
            json={
                "product_name": "Updated",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_product_not_found_admin(self, client: TestClient, admin_token: str):
        """Test updating non-existent product fails."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.put(
            "/api/v0/products/99999",
            json={
                "product_name": "Updated",
            },
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Product not found" in response.json()["detail"]


class TestDeleteProduct:
    """Tests for deleting product endpoint."""

    def test_delete_product_success_admin(self, client: TestClient, admin_token: str, test_product: Product):
        """Test admin can delete products."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(
            f"/api/v0/products/{test_product.Product_ID}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_product_forbidden_non_admin(self, client: TestClient, user_token: str, test_product: Product):
        """Test regular user cannot delete products."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.delete(
            f"/api/v0/products/{test_product.Product_ID}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only admins can manage products" in response.json()["detail"]

    def test_delete_product_not_found_admin(self, client: TestClient, admin_token: str):
        """Test deleting non-existent product fails."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(
            "/api/v0/products/99999",
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Product not found" in response.json()["detail"]

    def test_delete_product_unauthorized(self, client: TestClient, test_product: Product):
        """Test deleting product without auth fails."""
        response = client.delete(f"/api/v0/products/{test_product.Product_ID}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
