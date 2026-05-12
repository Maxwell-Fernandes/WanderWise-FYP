"""Pre-compute embeddings for Description_data/ place files.

Usage:
    cd backend

    # Full rebuild (delete all, re-insert everything)
    python -m app.scripts.precompute_embeddings

    # Add/update a single place
    python -m app.scripts.precompute_embeddings --place-name "Colva Beach"

    # Sync all new places (skip existing)
    python -m app.scripts.precompute_embeddings --incremental

    # Force full rebuild
    python -m app.scripts.precompute_embeddings --rebuild
"""

import argparse
import json
import sys
from pathlib import Path

import psycopg2

# Ensure backend root is on path
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import DESCRIPTION_DATA_DIR, SUPABASE_DB_URL
from app.services.embedding_service import _chunk_place
from app.services.supabase_embedding_store import (
    get_existing_place_names,
    upsert_place_embeddings,
)
from app.services.modal_embedding_client import embed_texts


def load_all_descriptions() -> list[tuple[str, str, str, dict]]:
    """Load all JSON description files from Description_data/.

    Returns:
        List of (stem_name, category, display_name, data) tuples.
    """
    results: list[tuple[str, str, str, dict]] = []
    for path in DESCRIPTION_DATA_DIR.rglob("*.json"):
        if path.parent.name == "plans":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("error"):
                continue
            category = path.parent.name
            metadata = data.get("metadata") or {}
            display_name = (
                metadata.get("main_heading")
                or metadata.get("page_title")
                or path.stem.replace("-", " ").title()
            )
            results.append((path.stem, category, display_name, data))
        except Exception as exc:
            print(f"  Skipping {path}: {exc}")
    return results


def find_place_file(place_name: str) -> tuple[str, str, str, dict] | None:
    """Find a place JSON file by fuzzy-matching its display name.

    Args:
        place_name: The place name to search for.

    Returns:
        (stem_name, category, display_name, data) or None if not found.
    """
    target = place_name.lower().strip()
    best_match = None
    best_score = 0.0

    for path in DESCRIPTION_DATA_DIR.rglob("*.json"):
        if path.parent.name == "plans":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("error"):
                continue
            metadata = data.get("metadata") or {}
            display_name = (
                metadata.get("main_heading")
                or metadata.get("page_title")
                or path.stem.replace("-", " ").title()
            )
            # Exact match wins
            if display_name.lower() == target:
                return (path.stem, path.parent.name, display_name, data)

            # Substring match
            if target in display_name.lower() or display_name.lower() in target:
                score = min(len(target), len(display_name.lower())) / max(
                    len(target), len(display_name.lower())
                )
                if score > best_score:
                    best_score = score
                    best_match = (path.stem, path.parent.name, display_name, data)

            # Stem match
            stem_normalized = path.stem.replace("-", " ").lower()
            if target in stem_normalized:
                score = 0.8
                if score > best_score:
                    best_score = score
                    best_match = (path.stem, path.parent.name, display_name, data)
        except Exception:
            continue

    if best_match and best_score >= 0.5:
        return best_match
    return None


def embed_and_upsert(
    display_name: str,
    category: str,
    data: dict,
) -> int:
    """Chunk, embed, and upsert embeddings for a single place.

    Args:
        display_name: Display name of the place.
        category: Category directory name.
        data: Full description JSON data.

    Returns:
        Number of chunks inserted.
    """
    raw_chunks = _chunk_place(display_name, data)
    if not raw_chunks:
        print(f"  No chunks generated for {display_name}")
        return 0

    chunk_texts = [c[0] for c in raw_chunks]
    chunk_types = [c[2] for c in raw_chunks]
    chunks = list(zip(chunk_texts, chunk_types))

    embeddings = embed_texts(chunk_texts)
    count = upsert_place_embeddings(display_name, category, chunks, embeddings)
    return count


def full_rebuild() -> None:
    """Delete all embeddings and re-insert everything."""
    print("=" * 60)
    print("Full Rebuild — Re-embedding all places")
    print("=" * 60)

    print("\n[1/3] Loading description files...")
    descriptions = load_all_descriptions()
    print(f"  Loaded {len(descriptions)} place files")

    all_chunks: list[tuple[str, str, str, str]] = []
    for _stem, category, display_name, data in descriptions:
        for chunk_text, _chunk_id, chunk_type in _chunk_place(display_name, data):
            all_chunks.append((display_name, category, chunk_text, chunk_type))

    print(f"  Generated {len(all_chunks)} chunks")

    print("\n[2/3] Embedding via Modal...")
    BATCH_SIZE = 200
    all_embeddings: list[list[float]] = []
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch_texts = [c[2] for c in all_chunks[i : i + BATCH_SIZE]]
        embs = embed_texts(batch_texts)
        all_embeddings.extend(embs)
        print(
            f"  Embedded {min(i + BATCH_SIZE, len(all_chunks))}/{len(all_chunks)}"
        )

    print("\n[3/3] Inserting into Supabase...")
    conn = psycopg2.connect(SUPABASE_DB_URL)
    cur = conn.cursor()
    cur.execute("DELETE FROM place_embeddings")
    print("  Cleared existing rows")

    insert_sql = (
        "INSERT INTO place_embeddings "
        "(place_name, category, chunk_type, chunk_text, embedding) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    for (name, cat, text, ctype), emb in zip(all_chunks, all_embeddings):
        emb_str = "[" + ",".join(str(x) for x in emb) + "]"
        cur.execute(insert_sql, (name, cat, ctype, text, emb_str))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM place_embeddings")
    count = cur.fetchone()[0]
    cur.execute(
        "SELECT category, COUNT(*) FROM place_embeddings GROUP BY category ORDER BY category"
    )
    cat_counts = cur.fetchall()
    cur.close()
    conn.close()

    print(f"\nDone! Inserted {count} embeddings:")
    for cat, cnt in cat_counts:
        print(f"  {cat}: {cnt}")
    print("=" * 60)


def rebuild_single_place(place_name: str) -> None:
    """Embed and upsert a single place by name."""
    print("=" * 60)
    print(f"Single Place Update: {place_name}")
    print("=" * 60)

    result = find_place_file(place_name)
    if result is None:
        print(f"\nERROR: Could not find a JSON file matching '{place_name}'")
        print("Available files:")
        for path in sorted(DESCRIPTION_DATA_DIR.rglob("*.json")):
            if path.parent.name != "plans":
                print(f"  {path.parent.name}/{path.stem}")
        sys.exit(1)

    stem, category, display_name, data = result
    print(f"\nFound: {display_name} (category: {category}, file: {stem}.json)")

    count = embed_and_upsert(display_name, category, data)
    print(f"Done! Inserted {count} chunks for {display_name}")
    print("=" * 60)


def sync_incremental() -> None:
    """Add embeddings for new places only, skip existing."""
    print("=" * 60)
    print("Incremental Sync — Adding new places only")
    print("=" * 60)

    print("\n[1/3] Checking existing embeddings...")
    existing_names = set(get_existing_place_names())
    print(f"  Found {len(existing_names)} existing places in Supabase")

    print("\n[2/3] Scanning Description_data/...")
    all_descriptions = load_all_descriptions()
    print(f"  Found {len(all_descriptions)} place files on disk")

    # Filter to new places only
    new_places = []
    for stem, category, display_name, data in all_descriptions:
        if display_name not in existing_names:
            new_places.append((stem, category, display_name, data))

    if not new_places:
        print("\n  No new places to add. Everything is up to date.")
        print("=" * 60)
        return

    print(f"  {len(new_places)} new places to embed:")
    for _, _, name, _ in new_places:
        print(f"    + {name}")

    print("\n[3/3] Embedding and inserting new places...")
    total_chunks = 0
    for i, (stem, category, display_name, data) in enumerate(new_places, 1):
        count = embed_and_upsert(display_name, category, data)
        total_chunks += count
        print(f"  [{i}/{len(new_places)}] {display_name}: {count} chunks")

    print(f"\nDone! Added {total_chunks} chunks from {len(new_places)} new places")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-compute place embeddings for Supabase pgvector search"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--place-name",
        type=str,
        help='Embed a single place by name (e.g., "Colva Beach")',
    )
    group.add_argument(
        "--incremental",
        action="store_true",
        help="Add new places only, skip existing",
    )
    group.add_argument(
        "--rebuild",
        action="store_true",
        help="Force full rebuild (delete all, re-insert everything)",
    )
    args = parser.parse_args()

    if not SUPABASE_DB_URL:
        print("ERROR: SUPABASE_DB_URL not set in backend/.env")
        sys.exit(1)

    if args.place_name:
        rebuild_single_place(args.place_name)
    elif args.incremental:
        sync_incremental()
    else:
        full_rebuild()


if __name__ == "__main__":
    main()
