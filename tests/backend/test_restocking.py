"""
Tests for restocking API endpoints and the demand forecast fields they depend on.
"""
from datetime import datetime

import pytest

import main


@pytest.fixture(autouse=True)
def clear_restock_orders():
    """Reset submitted orders between tests.

    restock_orders is a module-level list that persists for the process lifetime,
    so without this every test would inherit orders created by the ones before it
    and the id/order_number sequence assertions would drift.
    """
    main.restock_orders.clear()
    yield
    main.restock_orders.clear()


def build_item(sku="FLT-405", name="Oil Filter Cartridge", quantity=150,
               unit_cost=12.4, supplier="FilterWorks Supply", lead_time_days=5):
    """Build a valid restock order line item."""
    return {
        "sku": sku,
        "name": name,
        "quantity": quantity,
        "unit_cost": unit_cost,
        "supplier": supplier,
        "lead_time_days": lead_time_days,
        "line_total": round(quantity * unit_cost, 2),
    }


class TestDemandForecastRestockFields:
    """The restocking feature reads cost and lead time off the demand forecast."""

    def test_demand_forecasts_expose_restock_fields(self, client):
        """Test that every forecast carries unit_cost, supplier, and lead_time_days."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        for forecast in data:
            assert "unit_cost" in forecast
            assert "supplier" in forecast
            assert "lead_time_days" in forecast

    def test_restock_field_types(self, client):
        """Test that the new forecast fields have usable types and ranges."""
        response = client.get("/api/demand")
        data = response.json()

        for forecast in data:
            assert isinstance(forecast["unit_cost"], (int, float))
            assert isinstance(forecast["supplier"], str)
            assert isinstance(forecast["lead_time_days"], int)
            assert forecast["unit_cost"] > 0
            assert forecast["lead_time_days"] > 0
            assert forecast["supplier"] != ""

    def test_declining_demand_item_has_negative_shortfall(self, client):
        """Test that MTR-304 still has falling demand.

        The recommendation algorithm excludes any item whose forecast is below
        current demand. If this data ever flipped positive, the client would start
        recommending a part nobody needs and no other test would catch it.
        """
        response = client.get("/api/demand")
        forecasts = {f["item_sku"]: f for f in response.json()}

        motor = forecasts["MTR-304"]
        assert motor["forecasted_demand"] < motor["current_demand"]

    def test_psu_501_cost_matches_inventory(self, client):
        """Test that the one SKU in both datasets is priced identically.

        PSU-501 is the only forecast SKU that also exists in inventory, so a user
        can compare the Restocking and Inventory tabs directly.
        """
        forecasts = {f["item_sku"]: f for f in client.get("/api/demand").json()}
        inventory = {i["sku"]: i for i in client.get("/api/inventory").json()}

        assert forecasts["PSU-501"]["unit_cost"] == inventory["PSU-501"]["unit_cost"]


class TestRestockOrderEndpoints:
    """Test suite for submitting and listing restocking orders."""

    def test_get_restock_orders_empty(self, client):
        """Test that listing returns an empty list before anything is submitted."""
        response = client.get("/api/restock-orders")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_restock_order(self, client):
        """Test submitting a valid restocking order."""
        payload = {"budget": 10000, "items": [build_item()]}

        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["id"] == "1"
        assert order["order_number"] == f"RST-{datetime.now().year}-0001"
        assert order["status"] == "Submitted"
        assert order["item_count"] == 1
        assert order["budget"] == 10000
        assert len(order["items"]) == 1

    def test_created_order_structure(self, client):
        """Test that a submitted order returns every field the Orders view needs."""
        response = client.post(
            "/api/restock-orders",
            json={"budget": 10000, "items": [build_item()]},
        )
        order = response.json()

        for field in ("id", "order_number", "items", "total_value", "budget",
                      "item_count", "status", "submitted_date",
                      "expected_delivery", "lead_time_days"):
            assert field in order

        for item in order["items"]:
            assert "sku" in item
            assert "name" in item
            assert "quantity" in item
            assert "unit_cost" in item
            assert "supplier" in item
            assert "lead_time_days" in item

    def test_total_value_calculation(self, client):
        """Test that the order total is the sum of quantity x unit cost."""
        items = [
            build_item(sku="FLT-405", quantity=150, unit_cost=12.4, lead_time_days=5),
            build_item(sku="WDG-001", name="Industrial Widget Type A",
                       quantity=150, unit_cost=42.5,
                       supplier="Acme Industrial", lead_time_days=14),
        ]

        response = client.post("/api/restock-orders", json={"budget": 10000, "items": items})
        order = response.json()

        expected = sum(i["quantity"] * i["unit_cost"] for i in items)
        assert abs(order["total_value"] - expected) < 0.01
        assert order["total_value"] == 8235.0

    def test_lead_time_is_max_not_sum(self, client):
        """Test that order lead time is the slowest item, not the total.

        A shipment is complete when its last item lands, so 5-day and 14-day
        items together make a 14-day order, never a 19-day one.
        """
        items = [
            build_item(sku="FLT-405", lead_time_days=5),
            build_item(sku="WDG-001", quantity=10, unit_cost=42.5, lead_time_days=14),
            build_item(sku="GSK-203", quantity=10, unit_cost=6.2, lead_time_days=7),
        ]

        response = client.post("/api/restock-orders", json={"budget": 10000, "items": items})
        order = response.json()

        assert order["lead_time_days"] == 14

    def test_expected_delivery_matches_lead_time(self, client):
        """Test that expected delivery is submission date plus the lead time."""
        response = client.post(
            "/api/restock-orders",
            json={"budget": 10000, "items": [build_item(lead_time_days=5)]},
        )
        order = response.json()

        submitted = datetime.fromisoformat(order["submitted_date"])
        delivery = datetime.fromisoformat(order["expected_delivery"])

        assert (delivery - submitted).days == order["lead_time_days"] == 5

    def test_submitted_order_appears_in_list(self, client):
        """Test that a submitted order is retrievable, so the Orders tab can show it."""
        created = client.post(
            "/api/restock-orders",
            json={"budget": 10000, "items": [build_item()]},
        ).json()

        response = client.get("/api/restock-orders")
        assert response.status_code == 200

        orders = response.json()
        assert len(orders) == 1
        assert orders[0]["order_number"] == created["order_number"]

    def test_orders_returned_newest_first(self, client):
        """Test that listing is newest-first so the client needs no sort."""
        for _ in range(3):
            client.post("/api/restock-orders",
                        json={"budget": 10000, "items": [build_item()]})

        orders = client.get("/api/restock-orders").json()
        assert len(orders) == 3
        assert [o["order_number"] for o in orders] == [
            f"RST-{datetime.now().year}-000{n}" for n in (3, 2, 1)
        ]


class TestRestockOrderValidation:
    """Test suite for restocking order rejection paths."""

    def test_empty_items_rejected(self, client):
        """Test that an order with no items is rejected."""
        response = client.post("/api/restock-orders", json={"budget": 5000, "items": []})
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "at least one item" in data["detail"].lower()

    def test_over_budget_rejected(self, client):
        """Test that an order costing more than its budget is rejected."""
        response = client.post(
            "/api/restock-orders",
            json={"budget": 100, "items": [build_item(quantity=10, unit_cost=50.0)]},
        )
        assert response.status_code == 400

        data = response.json()
        assert "exceeds budget" in data["detail"].lower()

    def test_zero_quantity_rejected(self, client):
        """Test that a zero-quantity line is rejected."""
        response = client.post(
            "/api/restock-orders",
            json={"budget": 5000, "items": [build_item(quantity=0)]},
        )
        assert response.status_code == 400

        data = response.json()
        assert "quantities" in data["detail"].lower()

    def test_negative_quantity_rejected(self, client):
        """Test that a negative-quantity line is rejected."""
        response = client.post(
            "/api/restock-orders",
            json={"budget": 5000, "items": [build_item(quantity=-5)]},
        )
        assert response.status_code == 400

    def test_order_exactly_at_budget_accepted(self, client):
        """Test the boundary: spending the budget to the cent is allowed."""
        item = build_item(quantity=100, unit_cost=10.0)

        response = client.post("/api/restock-orders", json={"budget": 1000.0, "items": [item]})
        assert response.status_code == 201
        assert response.json()["total_value"] == 1000.0

    def test_missing_required_field_rejected(self, client):
        """Test that a malformed item fails Pydantic validation."""
        response = client.post(
            "/api/restock-orders",
            json={"budget": 5000, "items": [{"sku": "FLT-405", "quantity": 10}]},
        )
        assert response.status_code == 422

    def test_rejected_order_is_not_stored(self, client):
        """Test that a rejected submission leaves no partial order behind."""
        client.post("/api/restock-orders", json={"budget": 100, "items": [build_item()]})

        assert client.get("/api/restock-orders").json() == []
