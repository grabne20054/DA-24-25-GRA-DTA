import pytest
from datetime import datetime, timedelta
from collections import defaultdict

from DataAnalysis.descriptive.OrdersAmount import OrdersAmount


# -------------------------
# Helpers / Fixtures
# -------------------------

class MockHandler:
    def __init__(self, data):
        self._data = data

    def start(self):
        return self._data


@pytest.fixture
def sample_data():
    today = datetime.now()
    return [
        {"orderDate": today - timedelta(days=3)},
        {"orderDate": today - timedelta(days=2)},
        {"orderDate": today - timedelta(days=2)},
        {"orderDate": today - timedelta(days=1)},
        {"orderDate": today},
    ]


@pytest.fixture
def orders_amount(monkeypatch, sample_data):
    """
    Monkeypatch the APIDataHandlerFactory to return mock data
    """

    def mock_create_data_handler(_):
        return MockHandler(sample_data)

    monkeypatch.setattr(
        "DataAnalysis.preprocessing.APIDataHandlerFactory.APIDataHandlerFactory.create_data_handler",
        mock_create_data_handler
    )

    return OrdersAmount()


# -------------------------
# Tests
# -------------------------

def test_collect_returns_data(orders_amount):
    data = orders_amount.collect()
    assert isinstance(data, list)
    assert len(data) == 5


def test_growth_by_days(orders_amount   ):
    result = orders_amount.perform()

    assert "growth" in result
    assert "cumulative_growth" in result
    assert result["typeofgraph"] == "line"

    # total growth should equal 5
    assert sum(result["growth"].values()) == 5


def test_growth_last_days_filter(orders_amount):
    result = orders_amount.perform(last_days=2)

    assert all(
        key >= (datetime.now().date() - timedelta(days=2))
        for key in result["cumulative_growth"]
    )


def test_monthly_growth(orders_amount):
    result = orders_amount.perform(month=True)

    assert "growth" in result
    assert len(result["growth"]) >= 1
    assert sum(result["growth"].values()) == 5


def test_yearly_growth(orders_amount):
    result = orders_amount.perform(year=True)

    current_year = datetime.now().year
    assert current_year in result["growth"]
    assert result["growth"][current_year] == 5


def test_showzeros_daily(orders_amount):
    result = orders_amount.perform(showzeros=True)

    # Should contain continuous dates
    growth_keys = list(result["growth"].keys())
    assert len(growth_keys) >= 4


def test_negative_last_days(orders_amount):
    with pytest.raises(ValueError):
        orders_amount.perform(last_days=-5)


def test_machine_learning_disables_cumulative(orders_amount):
    result = orders_amount.perform(machine_learning=True)

    # cumulative growth should be empty
    assert result["cumulative_growth"] == {}

def test_machine_learning_growth_calculation(orders_amount):
    result = orders_amount.perform(machine_learning=True)

    # growth should be calculated using the mock data
    assert sum(result["growth"].values()) == 5

def test_percentage_growth_calculation(orders_amount):
    result = orders_amount.perform(percentage=True)

    # percentage growth should be calculated based on the mock data
    assert result["growth"] != {
        (datetime.now() - timedelta(days=3)).date(): 100.0,
        (datetime.now() - timedelta(days=2)).date(): 100.0,
        (datetime.now() - timedelta(days=1)).date(): 100.0,
        datetime.now().date(): 100.0,
    }

    assert result["growth"] == {
        (datetime.now() - timedelta(days=3)).date(): [
            0.0,
            1.0
        ],
        (datetime.now() - timedelta(days=2)).date(): [
            100.0,
            2.0
        ],
        (datetime.now() - timedelta(days=1)).date(): [
            -50.0,
            1.0
        ],
        datetime.now().date(): [
            0.0,
            1.0
        ],
    }
    