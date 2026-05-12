"""Modal deployment for WanderWise embedding functions."""

import os

import modal

app = modal.App("wanderwise-embeddings")

embedding_image = modal.Image.debian_slim().pip_install(
    "sentence-transformers", "torch"
)

hf_secret = modal.Secret.from_name("huggingface-secret")


@app.function(
    image=embedding_image,
    timeout=120,
    scaledown_window=300,
    secrets=[hf_secret],
)
def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate normalized embeddings for a batch of texts."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(
        "all-MiniLM-L6-v2", token=os.environ.get("HF_TOKEN")
    )
    embeddings = model.encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return embeddings.tolist()


@app.function(
    image=embedding_image,
    timeout=60,
    scaledown_window=300,
    secrets=[hf_secret],
)
def embed_query(query: str) -> list[float]:
    """Generate a normalized embedding for a single query."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(
        "all-MiniLM-L6-v2", token=os.environ.get("HF_TOKEN")
    )
    embedding = model.encode([query], normalize_embeddings=True)
    return embedding[0].tolist()
