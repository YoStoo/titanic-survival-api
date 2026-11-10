"""Smoke tests for the Titanic survival API (added Nov 2026, not part of the original sprint)."""
import json

import pytest
from fastapi.testclient import TestClient

import app as api

client = TestClient(api.app)

POOR_MAN = {"Pclass": 3, "Sex": "male", "Age": 25.0, "SibSp": 0, "Parch": 0, "Fare": 8.05, "Embarked": "S"}
RICH_WOMAN = {"Pclass": 1, "Sex": "female", "Age": 30.0, "SibSp": 0, "Parch": 0, "Fare": 50.0, "Embarked": "S"}


def test_health_says_model_loaded():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["model_loaded"] is True


def test_model_info_matches_metadata_file():
    with open("models/model_metadata.json") as f:
        meta = json.load(f)
    r = client.get("/model-info")
    assert r.status_code == 200
    body = r.json()
    assert body["model_type"] == "RandomForestClassifier"
    assert body["accuracy"] == meta["accuracy"]
    assert body["features"] == meta["feature_names"]


@pytest.mark.parametrize("passenger", [POOR_MAN, RICH_WOMAN])
def test_predict_returns_a_valid_probability(passenger):
    r = client.post("/predict", json=passenger)
    assert r.status_code == 200
    body = r.json()
    assert body["survived"] in (0, 1)
    assert 0.0 <= body["survival_probability"] <= 1.0
    assert body["prediction_confidence"] in ("High", "Medium", "Low")
    # The 0/1 answer should agree with the probability.
    assert body["survived"] == int(body["survival_probability"] >= 0.5)


def test_model_learned_the_famous_pattern():
    """First-class woman should be far more likely to survive than a third-class man."""
    poor = client.post("/predict", json=POOR_MAN).json()["survival_probability"]
    rich = client.post("/predict", json=RICH_WOMAN).json()["survival_probability"]
    assert rich > poor


def test_predict_batch_counts_every_passenger():
    r = client.post("/predict-batch", json=[POOR_MAN, RICH_WOMAN])
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 2
    assert len(body["predictions"]) == 2


def test_missing_field_is_rejected():
    bad = dict(POOR_MAN)
    del bad["Age"]
    r = client.post("/predict", json=bad)
    assert r.status_code == 422
