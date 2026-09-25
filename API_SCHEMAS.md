# JSON Schema

API request/response schemas for the two services. Schemas use
[JSON Schema 2020-12](https://json-schema.org/).

- **backend** — the app backend (owns objects, tags, storage, and search).
  These reflect the contracts in `architecture.md`; the backend is still a
  stub, so treat them as the intended contract.
- **ai_service** — the Flask inference service. These match the implemented
  code in `ai_service/`.

> Note on confidence: `confidence`/`tag_confidence` are raw cosine similarities
> clamped to `[0, 1]`, not calibrated probabilities. Calibrate `threshold`
> from held-out known/unknown images.

---

## backend

Base: the app backend HTTP API. Endpoints that accept images use
`multipart/form-data`; the JSON schemas below describe the non-file fields and
the JSON responses.

### `POST /objects` — register an object

Request (`multipart/form-data`): `metadata` JSON part + repeated `images` file
parts. The `metadata` part:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "backend/objects.request.json",
  "title": "RegisterObjectRequest",
  "type": "object",
  "required": ["name", "views"],
  "properties": {
    "name": { "type": "string", "minLength": 1 },
    "tags": {
      "type": "array",
      "items": { "type": "string", "minLength": 1 },
      "default": []
    },
    "views": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["view_label", "image_field"],
        "properties": {
          "view_label": { "enum": ["top", "side", "bottom", "right"] },
          "image_field": {
            "type": "string",
            "description": "Name of the multipart file part carrying this view."
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

Response `201`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "backend/objects.response.json",
  "title": "RegisterObjectResponse",
  "type": "object",
  "required": ["object_id", "views", "embedding_version"],
  "properties": {
    "object_id": { "type": "string" },
    "name": { "type": "string" },
    "tags": { "type": "array", "items": { "type": "string" } },
    "views": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["image_id", "view_label"],
        "properties": {
          "image_id": { "type": "string" },
          "view_label": { "enum": ["top", "side", "bottom", "right"] }
        },
        "additionalProperties": false
      }
    },
    "embedding_version": { "type": "string" }
  },
  "additionalProperties": false
}
```

### `POST /match` — rank objects for query image(s)

Request (`multipart/form-data`): repeated `images` file parts, optional
`options` JSON part:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "backend/match.options.json",
  "title": "MatchOptions",
  "type": "object",
  "properties": {
    "top_k": { "type": "integer", "minimum": 1, "default": 5 },
    "threshold": { "type": "number", "minimum": 0, "maximum": 1 }
  },
  "additionalProperties": false
}
```

Response `200`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "backend/match.response.json",
  "title": "MatchResponse",
  "type": "object",
  "required": ["decision", "matches"],
  "properties": {
    "decision": { "enum": ["match", "no confident match"] },
    "matches": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["object_id", "confidence"],
        "properties": {
          "object_id": { "type": "string" },
          "name": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "best_view": { "type": ["string", "null"] },
          "supporting_image_ids": {
            "type": "array",
            "items": { "type": "string" }
          }
        },
        "additionalProperties": false
      }
    },
    "tag_confidence": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["tag", "confidence"],
        "properties": {
          "tag": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

### `GET /search?q=...` — fuzzy name/tag search

Query parameter `q` (string, required). Response `200`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "backend/search.response.json",
  "title": "SearchResponse",
  "type": "object",
  "required": ["query", "results"],
  "properties": {
    "query": { "type": "string" },
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["object_id", "name", "score"],
        "properties": {
          "object_id": { "type": "string" },
          "name": { "type": "string" },
          "tags": { "type": "array", "items": { "type": "string" } },
          "score": {
            "type": "number",
            "description": "Fuzzy text match score; separate from visual similarity."
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

### `DELETE /objects/{id}` — delete an object

Response `200`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "backend/objects.delete.response.json",
  "title": "DeleteObjectResponse",
  "type": "object",
  "required": ["object_id", "deleted"],
  "properties": {
    "object_id": { "type": "string" },
    "deleted": { "type": "boolean" },
    "removed_images": { "type": "integer", "minimum": 0 },
    "removed_embeddings": { "type": "integer", "minimum": 0 }
  },
  "additionalProperties": false
}
```

### Error (all backend endpoints)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "backend/error.json",
  "title": "Error",
  "type": "object",
  "required": ["error"],
  "properties": { "error": { "type": "string" } },
  "additionalProperties": false
}
```

---

## ai_service

Base: the Flask inference service (`ai_service/`). Stateless: it stores nothing
and the caller supplies candidate embeddings on `/rank`.

### `GET /health`

Response `200`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ai_service/health.response.json",
  "title": "HealthResponse",
  "type": "object",
  "required": ["status", "model_version", "model_loaded"],
  "properties": {
    "status": { "const": "ok" },
    "model_version": { "type": "string" },
    "model_loaded": { "type": "boolean" }
  },
  "additionalProperties": false
}
```

### `POST /embed`

Request: `multipart/form-data` with 1–8 repeated `images` file parts (order is
significant). Response `200`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ai_service/embed.response.json",
  "title": "EmbedResponse",
  "type": "object",
  "required": ["model_version", "embeddings"],
  "properties": {
    "model_version": { "type": "string" },
    "embeddings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["input_index", "vector"],
        "properties": {
          "input_index": { "type": "integer", "minimum": 0 },
          "vector": {
            "type": "array",
            "items": { "type": "number" },
            "minItems": 1,
            "description": "L2-normalized float32 embedding (dinov2-small: 384 dims)."
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

### `POST /rank`

Request (`application/json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ai_service/rank.request.json",
  "title": "RankRequest",
  "type": "object",
  "required": ["queries", "candidates"],
  "properties": {
    "queries": {
      "type": "array",
      "minItems": 1,
      "description": "Query embeddings (from /embed). All vectors share one dimension.",
      "items": {
        "type": "array",
        "minItems": 1,
        "items": { "type": "number" }
      }
    },
    "candidates": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["object_id", "views"],
        "properties": {
          "object_id": { "type": "string", "minLength": 1 },
          "tags": {
            "type": "array",
            "items": { "type": "string" },
            "default": []
          },
          "views": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": ["vector"],
              "properties": {
                "view_label": { "type": ["string", "null"] },
                "vector": {
                  "type": "array",
                  "minItems": 1,
                  "items": { "type": "number" }
                }
              },
              "additionalProperties": false
            }
          }
        },
        "additionalProperties": false
      }
    },
    "threshold": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Min top-1 confidence for a confident match. Defaults to service config."
    },
    "top_k": {
      "type": "integer",
      "minimum": 1,
      "description": "Max ranked objects to return. Defaults to service config."
    }
  },
  "additionalProperties": false
}
```

Response `200`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ai_service/rank.response.json",
  "title": "RankResponse",
  "type": "object",
  "required": [
    "model_version",
    "threshold",
    "confident",
    "decision",
    "matches",
    "tag_confidence"
  ],
  "properties": {
    "model_version": { "type": "string" },
    "threshold": { "type": "number", "minimum": 0, "maximum": 1 },
    "confident": { "type": "boolean" },
    "decision": { "enum": ["match", "no confident match"] },
    "matches": {
      "type": "array",
      "description": "Ranked by confidence, highest first (up to top_k).",
      "items": {
        "type": "object",
        "required": ["object_id", "confidence", "best_view", "per_query_scores"],
        "properties": {
          "object_id": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "best_view": { "type": ["string", "null"] },
          "per_query_scores": {
            "type": "array",
            "items": { "type": "number", "minimum": 0, "maximum": 1 }
          }
        },
        "additionalProperties": false
      }
    },
    "tag_confidence": {
      "type": "array",
      "description": "Per-tag confidence, highest first.",
      "items": {
        "type": "object",
        "required": ["tag", "confidence"],
        "properties": {
          "tag": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

### Error (`/embed`, `/rank`)

`400` (bad input), `413` (file/body too large), or `500` (inference failure):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ai_service/error.json",
  "title": "Error",
  "type": "object",
  "required": ["error"],
  "properties": { "error": { "type": "string" } },
  "additionalProperties": false
}
```
