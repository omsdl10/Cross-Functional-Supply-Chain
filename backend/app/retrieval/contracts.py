from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.db.mock_data import DATA_ROOT


CONTRACTS_DIR = DATA_ROOT / "sample_contracts"
DEFAULT_CHROMA_PATH = DATA_ROOT.parent / "chroma"
COLLECTION_NAME = "supplier_contracts"


@dataclass(frozen=True)
class ContractChunk:
    chunk_id: str
    document_id: str
    supplier_id: str
    text: str
    source_path: str


class DeterministicEmbeddingFunction:
    """Small local embedding function for deterministic demo retrieval."""

    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in input]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            vector[index] += 1.0

        magnitude = sum(value * value for value in vector) ** 0.5
        if magnitude == 0:
            return vector

        return [value / magnitude for value in vector]


def read_contract_documents(contracts_dir: Path = CONTRACTS_DIR) -> list[Path]:
    return sorted(contracts_dir.glob("*-contract.txt"))


def extract_supplier_id(text: str, fallback: str) -> str:
    match = re.search(r"Supplier ID:\s*(SUP-\d+)", text)
    return match.group(1) if match else fallback


def chunk_text(text: str, chunk_size: int = 650, overlap: int = 120) -> list[str]:
    normalized = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        boundary = normalized.rfind("\n\n", start, end)
        if boundary <= start + overlap:
            boundary = end

        chunks.append(normalized[start:boundary].strip())
        if boundary == len(normalized):
            break
        start = boundary - overlap

    return [chunk for chunk in chunks if chunk]


def build_contract_chunks(contracts_dir: Path = CONTRACTS_DIR) -> list[ContractChunk]:
    chunks: list[ContractChunk] = []

    for path in read_contract_documents(contracts_dir):
        text = path.read_text(encoding="utf-8")
        supplier_id = extract_supplier_id(text, path.stem.split("-contract")[0])
        document_id = f"CONTRACT-{supplier_id}"

        for index, chunk in enumerate(chunk_text(text), start=1):
            chunks.append(
                ContractChunk(
                    chunk_id=f"{document_id}-CHUNK-{index}",
                    document_id=document_id,
                    supplier_id=supplier_id,
                    text=chunk,
                    source_path=str(path.relative_to(DATA_ROOT.parent)),
                )
            )

    return chunks


def get_chroma_client(chroma_path: Path = DEFAULT_CHROMA_PATH) -> Any:
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError as exc:
        raise RuntimeError(
            "ChromaDB is not installed. Run `pip install -r backend/requirements.txt`."
        ) from exc

    return chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False),
    )


def get_contract_collection(chroma_path: Path = DEFAULT_CHROMA_PATH) -> Any:
    client = get_chroma_client(chroma_path)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=DeterministicEmbeddingFunction(),
        metadata={"description": "Supplier contract chunks for retrieval"},
    )


def ingest_supplier_contracts(
    contracts_dir: Path = CONTRACTS_DIR,
    chroma_path: Path = DEFAULT_CHROMA_PATH,
) -> dict[str, int | str]:
    chunks = build_contract_chunks(contracts_dir)
    collection = get_contract_collection(chroma_path)

    if chunks:
        collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "document_id": chunk.document_id,
                    "supplier_id": chunk.supplier_id,
                    "source_path": chunk.source_path,
                }
                for chunk in chunks
            ],
        )

    return {
        "collection": COLLECTION_NAME,
        "documents_indexed": len(read_contract_documents(contracts_dir)),
        "chunks_indexed": len(chunks),
    }


def query_supplier_contracts(
    query: str,
    n_results: int = 3,
    chroma_path: Path = DEFAULT_CHROMA_PATH,
) -> list[dict[str, Any]]:
    collection = get_contract_collection(chroma_path)
    if collection.count() == 0:
        ingest_supplier_contracts(chroma_path=chroma_path)

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return [
        {
            "text": document,
            "metadata": metadata,
            "distance": distance,
        }
        for document, metadata, distance in zip(documents, metadatas, distances)
    ]
