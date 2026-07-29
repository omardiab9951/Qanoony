import json
import os
import re
import time
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from langchain_community.document_loaders import PyPDFLoader
except ImportError as exc:
    raise SystemExit(
        "PyPDFLoader is unavailable. Install the PDF loader dependency with: pip install pypdf"
    ) from exc


from qanoony.backend.config import (
    COMPANY_FORMATION_RAW_DIR,
    COMPANY_FORMATION_CLEANED_DIR,
    COMPANY_FORMATION_CHUNKS_DIR,
    COMPANY_FORMATION_CHROMA_DIR,
)

RAW_DIR = COMPANY_FORMATION_RAW_DIR
CLEANED_DIR = COMPANY_FORMATION_CLEANED_DIR
CHUNKS_DIR = COMPANY_FORMATION_CHUNKS_DIR
CHROMA_DIR = COMPANY_FORMATION_CHROMA_DIR
COLLECTION_NAME = "company_formation_db"
BATCH_SIZE = 50


def log(message: str) -> None:
    print(message, flush=True)


def elapsed(start: float) -> str:
    return f"{time.perf_counter() - start:.2f}s"


def format_eta(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def clean_text(text: str) -> str:
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_pdfs() -> list[Document]:
    pdfs = sorted(RAW_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {RAW_DIR}")

    log(f"Detected {len(pdfs)} PDFs:")
    for pdf in pdfs:
        log(f"  - {pdf.name}")

    docs = []
    for pdf in pdfs:
        start = time.perf_counter()
        log(f"Extracting {pdf.name}...")
        before = len(docs)
        for page in PyPDFLoader(str(pdf)).load():
            page.page_content = clean_text(page.page_content)
            page.metadata.update({"source": pdf.name, "domain": "company_formation"})
            if page.page_content:
                docs.append(page)
        log(f"  extracted {len(docs) - before} pages in {elapsed(start)}")
    return docs


def save_cleaned_text(docs: list[Document]) -> None:
    start = time.perf_counter()
    CLEANED_DIR.mkdir(exist_ok=True)
    by_source: dict[str, list[str]] = {}
    for doc in docs:
        by_source.setdefault(doc.metadata["source"], []).append(doc.page_content)

    for source, pages in by_source.items():
        (CLEANED_DIR / f"{Path(source).stem}.txt").write_text(
            "\n\n".join(pages), encoding="utf-8"
        )
    log(f"Wrote {len(by_source)} cleaned files in {elapsed(start)}")


def split_docs(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index
    return chunks


def save_chunks(chunks: list[Document]) -> None:
    start = time.perf_counter()
    CHUNKS_DIR.mkdir(exist_ok=True)
    with (CHUNKS_DIR / "company_formation_chunks.jsonl").open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(
                json.dumps(
                    {"text": chunk.page_content, "metadata": chunk.metadata},
                    ensure_ascii=False,
                )
                + "\n"
            )
    log(f"Wrote {len(chunks)} chunks in {elapsed(start)}")


def build_chroma(chunks: list[Document]) -> None:
    start = time.perf_counter()
    log("Loading BAAI/bge-m3 embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu", "local_files_only": True},
        encode_kwargs={"normalize_embeddings": True},
    )
    log(f"Loaded embedding model in {elapsed(start)}")

    start = time.perf_counter()
    vector = embeddings.embed_query("embedding smoke test")
    log(f"Generated smoke-test vector with {len(vector)} dimensions in {elapsed(start)}")

    start = time.perf_counter()
    db = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
    log(f"Opened Chroma collection in {elapsed(start)}")

    existing_ids = set(db._collection.get(include=[])["ids"])
    pending = [
        (f"company_formation_{index}", chunk)
        for index, chunk in enumerate(chunks)
        if f"company_formation_{index}" not in existing_ids
    ]
    log(f"Existing indexed chunks: {len(existing_ids)}")
    log(f"Remaining chunks to index: {len(pending)}")

    indexed_this_run = 0
    indexing_start = time.perf_counter()
    for offset in range(0, len(chunks), BATCH_SIZE):
        batch_pairs = [
            (f"company_formation_{index}", chunks[index])
            for index in range(offset, min(offset + BATCH_SIZE, len(chunks)))
            if f"company_formation_{index}" not in existing_ids
        ]
        batch_number = offset // BATCH_SIZE + 1
        total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
        if not batch_pairs:
            log(f"Batch {batch_number}/{total_batches}: already indexed, skipping")
            continue

        ids = [item[0] for item in batch_pairs]
        batch = [item[1] for item in batch_pairs]
        texts = [chunk.page_content for chunk in batch]
        metadatas = [chunk.metadata for chunk in batch]

        batch_start = time.perf_counter()
        batch_embeddings = embeddings.embed_documents(texts)
        embed_time = elapsed(batch_start)

        write_start = time.perf_counter()
        db._collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=batch_embeddings,
        )
        write_time = elapsed(write_start)

        existing_ids.update(ids)
        indexed_this_run += len(batch)
        indexed_total = len(existing_ids)
        remaining = len(chunks) - indexed_total
        rate = indexed_this_run / (time.perf_counter() - indexing_start)
        eta = remaining / rate if rate else 0
        log(
            f"Batch {batch_number}/{total_batches}: embedded {len(batch)} chunks in {embed_time}; "
            f"wrote to Chroma in {write_time}; indexed {indexed_total}/{len(chunks)}; "
            f"remaining {remaining}; ETA {format_eta(eta)}"
        )

    log(f"Total indexed chunks: {len(chunks)}")
    log(f"Final Chroma collection count: {db._collection.count()}")


def main() -> None:
    total_start = time.perf_counter()
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    log("Loading PDFs and extracting text...")
    start = time.perf_counter()
    docs = load_pdfs()
    log(f"Loaded {len(docs)} pages in {elapsed(start)}")

    log("Cleaning text...")
    start = time.perf_counter()
    save_cleaned_text(docs)
    log(f"Cleaning phase completed in {elapsed(start)}")

    log("Creating chunks...")
    start = time.perf_counter()
    chunks = split_docs(docs)
    log(f"Chunking created {len(chunks)} chunks in {elapsed(start)}")
    save_chunks(chunks)

    log("Generating embeddings and saving Chroma database...")
    start = time.perf_counter()
    build_chroma(chunks)
    log(f"Embedding and Chroma writing completed in {elapsed(start)}")

    log(f"Done. Indexed {len(chunks)} chunks from {len(docs)} pages in {elapsed(total_start)}")


if __name__ == "__main__":
    main()
