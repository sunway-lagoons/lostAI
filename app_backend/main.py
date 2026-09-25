"""App backend HTTP routes (FastAPI).

Routes:
  POST   /objects       Register object, views, and tags; store embeddings.
  POST   /match         Accept query image(s); return ranked object matches.
  GET    /search?q=...  Fuzzy name/tag search.
  DELETE /objects/{id}  Delete object metadata, images, and embeddings.
"""

# TODO: define FastAPI app and wire routes to images/search/matching modules
