"""Stateless object ranking over embeddings.

The app backend supplies query embeddings and a set of candidate objects
(each with its per-view reference embeddings and tags). This module computes
visual match confidence per object and a derived per-tag confidence. It stores
nothing and never touches a database.

Scoring
-------
Similarity is cosine similarity (dot product after L2 normalization). For each
candidate object we take, per query, the best-matching reference view, then
average those best-per-query scores across all queries. This mirrors the
matching algorithm in ai-implementation.md and avoids letting duplicate photos
of one view dominate.

Confidence values are raw, uncalibrated similarities clamped to [0, 1]. They
are NOT probabilities. The rejection threshold must be calibrated from held-out
known/unknown images by the backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


class RankInputError(ValueError):
    """Raised when a /rank request payload is malformed."""


@dataclass
class View:
    view_label: str | None
    vector: np.ndarray


@dataclass
class Candidate:
    object_id: str
    tags: list[str]
    views: list[View]


@dataclass
class RankedObject:
    object_id: str
    confidence: float
    best_view: str | None
    per_query_scores: list[float]


def _as_vector(value: Any, dim: int | None, where: str) -> np.ndarray:
    arr = np.asarray(value, dtype=np.float32)
    if arr.ndim != 1 or arr.size == 0:
        raise RankInputError(f"{where}: expected a non-empty 1-D numeric vector")
    if not np.all(np.isfinite(arr)):
        raise RankInputError(f"{where}: vector contains non-finite values")
    if dim is not None and arr.size != dim:
        raise RankInputError(
            f"{where}: dimension {arr.size} does not match expected {dim}"
        )
    return arr


def _l2_normalize(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return mat / norms


def parse_request(payload: Any) -> tuple[np.ndarray, list[Candidate], float, int]:
    """Validate and coerce a /rank JSON body.

    Returns:
        (queries, candidates, threshold, top_k)

    Raises:
        RankInputError: on any malformed field.
    """
    if not isinstance(payload, dict):
        raise RankInputError("request body must be a JSON object")

    raw_queries = payload.get("queries")
    if not isinstance(raw_queries, list) or not raw_queries:
        raise RankInputError("'queries' must be a non-empty list of vectors")

    dim = len(np.asarray(raw_queries[0], dtype=np.float32).ravel()) or None
    queries = np.stack(
        [_as_vector(q, dim, f"queries[{i}]") for i, q in enumerate(raw_queries)]
    )

    raw_candidates = payload.get("candidates")
    if not isinstance(raw_candidates, list) or not raw_candidates:
        raise RankInputError("'candidates' must be a non-empty list")

    candidates: list[Candidate] = []
    for ci, raw in enumerate(raw_candidates):
        if not isinstance(raw, dict):
            raise RankInputError(f"candidates[{ci}] must be an object")
        object_id = raw.get("object_id")
        if not isinstance(object_id, str) or not object_id:
            raise RankInputError(f"candidates[{ci}].object_id must be a non-empty string")

        tags_raw = raw.get("tags", [])
        if tags_raw is None:
            tags_raw = []
        if not isinstance(tags_raw, list) or not all(isinstance(t, str) for t in tags_raw):
            raise RankInputError(f"candidates[{ci}].tags must be a list of strings")

        views_raw = raw.get("views")
        if not isinstance(views_raw, list) or not views_raw:
            raise RankInputError(f"candidates[{ci}].views must be a non-empty list")

        views: list[View] = []
        for vi, v in enumerate(views_raw):
            if not isinstance(v, dict):
                raise RankInputError(f"candidates[{ci}].views[{vi}] must be an object")
            vec = _as_vector(v.get("vector"), dim, f"candidates[{ci}].views[{vi}].vector")
            label = v.get("view_label")
            if label is not None and not isinstance(label, str):
                raise RankInputError(
                    f"candidates[{ci}].views[{vi}].view_label must be a string or null"
                )
            views.append(View(view_label=label, vector=vec))

        candidates.append(Candidate(object_id=object_id, tags=list(tags_raw), views=views))

    threshold = payload.get("threshold")
    if threshold is None:
        threshold = float("nan")  # caller substitutes its configured default
    else:
        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            raise RankInputError("'threshold' must be a number")

    top_k = payload.get("top_k")
    if top_k is None:
        top_k = 0  # caller substitutes its configured default
    else:
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
            raise RankInputError("'top_k' must be a positive integer")

    return queries, candidates, threshold, top_k


def _score_candidate(queries: np.ndarray, cand: Candidate) -> tuple[float, str | None, list[float]]:
    """Score one object: best view per query, averaged across queries."""
    view_matrix = _l2_normalize(np.stack([v.vector for v in cand.views]))
    # sims[q, v] = cosine(query_q, view_v)
    sims = queries @ view_matrix.T  # (n_queries, n_views)

    best_view_idx_per_query = np.argmax(sims, axis=1)
    per_query_best = sims[np.arange(sims.shape[0]), best_view_idx_per_query]

    object_score = float(np.mean(per_query_best))
    object_score = max(0.0, min(1.0, object_score))

    # Report the view that most often (then most strongly) won across queries.
    winning_view = int(np.bincount(best_view_idx_per_query, minlength=len(cand.views)).argmax())
    best_view = cand.views[winning_view].view_label

    per_query_scores = [max(0.0, min(1.0, float(s))) for s in per_query_best]
    return object_score, best_view, per_query_scores


def rank(
    queries: np.ndarray,
    candidates: list[Candidate],
    threshold: float,
    top_k: int,
) -> dict[str, Any]:
    """Rank candidate objects and derive per-tag confidence.

    Args:
        queries: ``(n_queries, dim)`` array of query embeddings.
        candidates: candidate objects with per-view reference embeddings.
        threshold: minimum top-1 confidence to count as a confident match.
        top_k: how many ranked objects to return.

    Returns:
        A dict with ``matches``, ``tag_confidence``, ``confident``, and
        ``decision`` keys.
    """
    norm_queries = _l2_normalize(np.asarray(queries, dtype=np.float32))

    ranked: list[RankedObject] = []
    for cand in candidates:
        score, best_view, per_query = _score_candidate(norm_queries, cand)
        ranked.append(
            RankedObject(
                object_id=cand.object_id,
                confidence=score,
                best_view=best_view,
                per_query_scores=per_query,
            )
        )

    ranked.sort(key=lambda r: r.confidence, reverse=True)

    # Tag confidence: for each tag, the highest confidence among candidate
    # objects that carry it. Interpreted as "how confident we are the item has
    # this tag," driven by the best-matching object bearing the tag.
    tag_scores: dict[str, float] = {}
    conf_by_object = {r.object_id: r.confidence for r in ranked}
    for cand in candidates:
        obj_conf = conf_by_object.get(cand.object_id, 0.0)
        for tag in cand.tags:
            if obj_conf > tag_scores.get(tag, -1.0):
                tag_scores[tag] = obj_conf

    tag_confidence = [
        {"tag": tag, "confidence": round(conf, 6)}
        for tag, conf in sorted(tag_scores.items(), key=lambda kv: kv[1], reverse=True)
    ]

    limited = ranked[:top_k] if top_k > 0 else ranked
    top_confidence = ranked[0].confidence if ranked else 0.0
    confident = bool(ranked) and top_confidence >= threshold

    matches = [
        {
            "object_id": r.object_id,
            "confidence": round(r.confidence, 6),
            "best_view": r.best_view,
            "per_query_scores": [round(s, 6) for s in r.per_query_scores],
        }
        for r in limited
    ]

    return {
        "matches": matches,
        "tag_confidence": tag_confidence,
        "confident": confident,
        "decision": "match" if confident else "no confident match",
    }
