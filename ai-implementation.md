# AI Inference Service — Implementation Details

## Scope

The AI service is a standalone **Flask HTTP server**. Its only job is to convert one or more images into embedding vectors. It does **not** store objects, tags, image files, or embeddings; perform fuzzy text search; or decide which object matched. Those jobs belong to the app backend.

```text
Gradio → app backend → Flask AI service → embedding vectors
                     ↘ database + image storage + match ranking
```

## Model and embedding

- MVP encoder: `facebook/dinov2-small` via `transformers` + PyTorch. Start with pretrained weights; do not train a classifier for each new object.
- Load the image processor and model **once at service startup**, not once per request. Call `model.eval()` and run inference under `torch.inference_mode()`.
- Decode each upload with Pillow, apply EXIF orientation, convert to RGB, and pass it through the model's image processor. Use identical preprocessing for reference and query images.
- Use the model output's global CLS token (`last_hidden_state[:, 0, :]`) as the first embedding baseline. L2-normalize each vector and return `float32` values. Do not concatenate top/side/bottom/right views into one vector; embed each image separately.
- Return a fixed `model_version`/`embedding_version` with each response. On any model, preprocessing, or embedding-method change, regenerate **all** stored reference embeddings before comparing new queries.
- Test crop sensitivity: a large background can dominate similarity. Require the object to fill most of the reference/query frame for v1. Add cropping or detection only if real photos show a need.

## API contract

### `POST /embed`

- Request: `multipart/form-data` with repeated `images` file fields. Order is significant.
- Validate: 1–8 images per request, supported decodable image formats, per-file size and request-body limits. Reject empty, corrupt, or unsupported images with a clear 4xx response.
- Response: ordered embeddings, one per input image, plus model/version metadata. Never return a class label or a claimed match probability.

```json
{
  "model_version": "facebook/dinov2-small:cls-l2-v1",
  "embeddings": [
    {"input_index": 0, "vector": [0.012, -0.034]},
    {"input_index": 1, "vector": [0.056, 0.078]}
  ]
}
```

The sample vectors above are truncated to illustrate the response shape; real vectors contain the model's full embedding dimension. Include a `GET /health` endpoint that returns readiness and `model_version`.

## Suggested files

```text
ai_service/
├── app.py             # Flask routes, limits, validation, error responses
├── model.py           # One-time processor/model load and batched inference
├── preprocess.py      # Decode, EXIF orientation, RGB conversion
├── config.py          # Model ID, device, request limits
└── tests/
    ├── test_api.py
    └── test_embeddings.py
```

## Matching stays in app backend

1. On registration, store each reference embedding with `object_id`, `image_id`, and `view_label` (`top`, `side`, `bottom`, `right`).
2. On search, send each query image to `/embed`. Compare its normalized vector with saved reference vectors using dot product (cosine similarity after normalization).
3. Aggregate view-level hits into **object-level** results. For an MVP with multiple queries, find each query's best reference view per object, then average those per-query scores; avoid letting duplicate photos of one view drown out other views.
4. Return the top object IDs and supporting reference images. If the best score falls below a threshold established from held-out known and unknown objects, return `no confident match`.
5. Keep name/tag fuzzy search in the app backend, separate from vector matching.

## Runtime and checks

- Run the Flask AI service as a separate process/container; the app backend calls it through a private configurable URL, with timeouts and a clear `inference unavailable` error.
- Set Flask's request-body size limit; decode files in memory for v1 instead of saving query images on the inference server. Avoid exposing this service directly to the public internet.
- Test: single and batch requests preserve order; identical images yield near-identical vectors; returned vectors have finite values and norm ≈ 1; invalid/oversized files fail cleanly; reference and query pipelines yield compatible versions.
- Evaluate with newly photographed images, not the same files used as references. Measure top-1 accuracy and unknown-object false matches before selecting a threshold or fine-tuning.

## Build order

1. Implement `/health` and `/embed` with one image.
2. Add batch uploads, validation, and unit tests.
3. Wire the app backend's inference client to `/embed`.
4. Save reference embeddings, implement object-level ranking, and calibrate unknown-object rejection.
