"""Visual similarity and object-level match ranking.

Compares query embeddings against stored view embeddings, combines evidence
by object ID, and applies the unknown-object rejection threshold.
"""

# TODO: rank_matches(query_embeddings) -> ranked results or "no confident match"
