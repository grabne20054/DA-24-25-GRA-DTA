import pytest
from datetime import datetime, timedelta
from collections import defaultdict

from DataAnalysis.descriptive.CustomerSignup import CustomerSignup


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
        {"signedUp": today - timedelta(days=3)},
        {"signedUp": today - timedelta(days=2)},
        {"signedUp": today - timedelta(days=2)},
        {"signedUp": today - timedelta(days=1)},
        {"signedUp": today},
    ]


@pytest.fixture
def customer_signup(monkeypatch, sample_data):
    """
    Monkeypatch the APIDataHandlerFactory to return mock data
    """

    def mock_create_data_handler(_):
        return MockHandler(sample_data)

    monkeypatch.setattr(
        "DataAnalysis.preprocessing.APIDataHandlerFactory.APIDataHandlerFactory.create_data_handler",
        mock_create_data_handler
    )

    return CustomerSignup()


# -------------------------
# Tests
# -------------------------

def test_collect_returns_data(customer_signup):
    data = customer_signup.collect()
    assert isinstance(data, list)
    assert len(data) == 5


def test_growth_by_days(customer_signup):
    result = customer_signup.perform()

    assert "growth" in result
    assert "cumulative_growth" in result
    assert result["typeofgraph"] == "line"

    # total growth should equal 5
    assert sum(result["growth"].values()) == 5


def test_growth_last_days_filter(customer_signup):
    result = customer_signup.perform(last_days=2)

    assert all(
        key >= (datetime.now().date() - timedelta(days=2))
        for key in result["cumulative_growth"]
    )


def test_monthly_growth(customer_signup):
    result = customer_signup.perform(month=True)

    assert "growth" in result
    assert len(result["growth"]) >= 1
    assert sum(result["growth"].values()) == 5


def test_yearly_growth(customer_signup):
    result = customer_signup.perform(year=True)

    current_year = datetime.now().year
    assert current_year in result["growth"]
    assert result["growth"][current_year] == 5


def test_showzeros_daily(customer_signup):
    result = customer_signup.perform(showzeros=True)

    # Should contain continuous dates
    growth_keys = list(result["growth"].keys())
    assert len(growth_keys) >= 4


def test_negative_last_days(customer_signup):
    with pytest.raises(ValueError):
        customer_signup.perform(last_days=-5)


def test_machine_learning_disables_cumulative(customer_signup):
    result = customer_signup.perform(machine_learning=True)

    # cumulative growth should be empty
    assert result["cumulative_growth"] == {}

    