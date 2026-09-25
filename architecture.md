# Object Matcher Architecture

## Overview

Run three independent services:

1. **Gradio UI** — upload reference views, submit query images, and display results.
2. **App backend (FastAPI)** — own object records, image management, tags, fuzzy text search, and visual match ranking.
3. **AI inference service (Flask)** — load the image encoder once and expose an embedding endpoint. It does not access the app database or implement product logic.

```text
Gradio UI → App backend → Flask inference service
           ↳ database          ↳ image encoder
           ↳ image storage
           ↳ stored embeddings
```

## Repository layout

```text
object-matcher/
├── ui/
│   ├── app.py              # Gradio screens
│   └── api_client.py       # Calls app backend only
├── app_backend/
│   ├── main.py             # HTTP routes
│   ├── images.py           # Validate, store, replace, delete images
│   ├── search.py           # Name/tag filtering and fuzzy text search
│   ├── matching.py         # Visual similarity and object-level ranking
│   ├── inference_client.py # Calls Flask /embed
│   ├── db.py               # Object, tag, image, and embedding records
│   └── schemas.py          # API request/response types
├── ai_service/
│   ├── app.py              # Flask POST /embed, GET /health
│   ├── model.py            # Load encoder once; produce embeddings
│   └── preprocess.py       # Decode and prepare images
├── data/
│   └── images/             # Reference image files
└── tests/
```

## Ownership

- **UI:** presentation and user input. Never calls the inference service directly.
- **App backend:** validates uploads; assigns object IDs and view labels (top, side, bottom, right); stores image files, metadata, and embeddings; handles tags and fuzzy name search; ranks matches.
- **AI service:** accepts images and returns vectors. No object IDs, tags, database access, or ranking logic. This keeps the model replaceable.

## API contracts

| Service | Endpoint | Purpose |
|---|---|---|
| App backend | `POST /objects` | Register object, views, and tags; request embeddings and save them. |
| App backend | `POST /match` | Accept one or more query images; request embeddings and return ranked object matches. |
| App backend | `GET /search?q=...` | Search object names and tags, including typo-tolerant text matching. |
| App backend | `DELETE /objects/{id}` | Delete object metadata, images, and embeddings. |
| AI service | `POST /embed` | Accept one or more image files; return an ordered embedding per image. |
| AI service | `GET /health` | Report service readiness. |

## Data flow

**Register:** Gradio → `POST /objects` → app backend saves reference views → Flask `/embed` → app backend stores each embedding with its object ID and view label.

**Match:** Gradio → `POST /match` → Flask `/embed` for query images → app backend compares against stored view embeddings → combines evidence by object ID → returns ranked matches or “no confident match.”

**Text search:** Gradio → `GET /search` → app backend filters names/tags. Fuzzy text matching is separate from visual similarity.

## MVP rules

- Start with SQLite for metadata and stored embeddings; use a separate vector index only if lookup performance requires it.
- Keep original image files outside the database; store their paths and metadata in SQLite.
- Keep the AI service private to the app backend. Configure its address through an environment variable rather than hardcoding it.
- Do not present cosine similarity as a calibrated probability. Set the unknown-object rejection threshold using held-out images.
