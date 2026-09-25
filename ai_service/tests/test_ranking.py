"""Unit tests for the stateless ranking logic.

These use hand-built vectors and need neither torch nor the model.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from ai_service.ranking import RankInputError, parse_request, rank


def _unit(*components) -> list[float]:
    v = np.asarray(components, dtype=np.float32)
    return (v / np.linalg.norm(v)).tolist()


def test_identical_view_scores_near_one():
    q = _unit(1, 0, 0)
    payload = {
        "queries": [q],
        "candidates": [
            {
                "object_id": "match",
                "tags": ["wallet", "black"],
                "views": [{"view_label": "top", "vector": q}],
            },
            {
                "object_id": "other",
                "tags": ["bottle"],
                "views": [{"view_label": "top", "vector": _unit(0, 1, 0)}],
            },
        ],
    }
    queries, candidates, _, _ = parse_request(payload)
    result = rank(queries, candidates, threshold=0.5, top_k=5)

    assert result["matches"][0]["object_id"] == "match"
    assert result["matches"][0]["confidence"] > 0.99
    assert result["confident"] is True
    assert result["decision"] == "match"


def test_orthogonal_query_is_not_confident():
    q = _unit(0, 0, 1)
    payload = {
        "queries": [q],
        "candidates": [
            {
                "object_id": "a",
                "tags": ["x"],
                "views": [{"view_label": "top", "vector": _unit(1, 0, 0)}],
            }
        ],
    }
    queries, candidates, _, _ = parse_request(payload)
    result = rank(queries, candidates, threshold=0.5, top_k=5)

    # Orthogonal -> cosine 0 -> clamped confidence 0 -> below threshold.
    assert result["matches"][0]["confidence"] == pytest.approx(0.0, abs=1e-6)
    assert result["confident"] is False
    assert result["decision"] == "no confident match"


def test_best_view_selected_per_object():
    q = _unit(0, 1, 0)
    payload = {
        "queries": [q],
        "candidates": [
            {
                "object_id": "a",
                "tags": [],
                "views": [
                    {"view_label": "top", "vector": _unit(1, 0, 0)},
                    {"view_label": "side", "vector": q},  # exact match
                ],
            }
        ],
    }
    queries, candidates, _, _ = parse_request(payload)
    result = rank(queries, candidates, threshold=0.5, top_k=5)

    assert result["matches"][0]["best_view"] == "side"
    assert result["matches"][0]["confidence"] > 0.99


def test_multi_query_averages_best_per_query():
    q1 = _unit(1, 0, 0)
    q2 = _unit(0, 1, 0)
    payload = {
        "queries": [q1, q2],
        "candidates": [
            {
                "object_id": "a",
                "tags": [],
                "views": [
                    {"view_label": "top", "vector": q1},
                    {"view_label": "side", "vector": q2},
                ],
            }
        ],
    }
    queries, candidates, _, _ = parse_request(payload)
    result = rank(queries, candidates, threshold=0.5, top_k=5)
    # Each query matches its own view exactly -> average ~1.
    assert result["matches"][0]["confidence"] > 0.99
    assert len(result["matches"][0]["per_query_scores"]) == 2


def test_tag_confidence_tracks_best_object():
    q = _unit(1, 0, 0)
    payload = {
        "queries": [q],
        "candidates": [
            {
                "object_id": "strong",
                "tags": ["wallet", "shared"],
                "views": [{"view_label": "top", "vector": q}],
            },
            {
                "object_id": "weak",
                "tags": ["bottle", "shared"],
                "views": [{"view_label": "top", "vector": _unit(0.2, 1, 0)}],
            },
        ],
    }
    queries, candidates, _, _ = parse_request(payload)
    result = rank(queries, candidates, threshold=0.5, top_k=5)

    tags = {t["tag"]: t["confidence"] for t in result["tag_confidence"]}
    # "wallet" only on the strong match -> high confidence.
    assert tags["wallet"] > 0.99
    # "shared" appears on both -> takes the max (strong object) confidence.
    assert tags["shared"] == pytest.approx(tags["wallet"], abs=1e-6)
    # "bottle" only on the weaker object -> strictly lower confidence.
    assert tags["bottle"] < tags["wallet"]


def test_top_k_limits_results():
    q = _unit(1, 0, 0)
    payload = {
        "queries": [q],
        "candidates": [
            {
                "object_id": f"o{i}",
                "tags": [],
                "views": [{"view_label": None, "vector": _unit(1, i * 0.1, 0)}],
            }
            for i in range(6)
        ],
    }
    queries, candidates, _, _ = parse_request(payload)
    result = rank(queries, candidates, threshold=0.5, top_k=3)
    assert len(result["matches"]) == 3


# --- validation ---


def test_parse_defaults_signal_omitted_threshold_and_top_k():
    payload = {
        "queries": [_unit(1, 0, 0)],
        "candidates": [{"object_id": "a", "views": [{"vector": _unit(1, 0, 0)}]}],
    }
    _, _, threshold, top_k = parse_request(payload)
    assert math.isnan(threshold)  # caller substitutes config default
    assert top_k == 0  # caller substitutes config default


def test_parse_rejects_empty_queries():
    with pytest.raises(RankInputError):
        parse_request({"queries": [], "candidates": [{"object_id": "a", "views": []}]})


def test_parse_rejects_dimension_mismatch():
    with pytest.raises(RankInputError):
        parse_request(
            {
                "queries": [_unit(1, 0, 0)],
                "candidates": [{"object_id": "a", "views": [{"vector": [1.0, 0.0]}]}],
            }
        )


def test_parse_rejects_missing_object_id():
    with pytest.raises(RankInputError):
        parse_request(
            {
                "queries": [_unit(1, 0, 0)],
                "candidates": [{"views": [{"vector": _unit(1, 0, 0)}]}],
            }
        )
