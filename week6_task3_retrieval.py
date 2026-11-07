import csv, json, time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from task2_chunks import make_chunks
def evaluate(score_rows, chunks, items):
    hits, reciprocal = [], []
    for row, query in zip(score_rows, items):
        if query["doc"] is None:
            continue
        top = np.argsort(-row, kind="stable")[:3]
        relevant_ranks = [
            rank for rank, index in enumerate(top, 1)
            if chunks[index]["doc"] == query["doc"]
            and query["evidence"] in chunks[index]["text"]
        ]
        hits.append(bool(relevant_ranks))
        reciprocal.append(1 / relevant_ranks[0] if relevant_ranks else 0)
    if not hits:
        return None, None
    return float(np.mean(hits)), float(np.mean(reciprocal))
def main():
    with open("corpus.json", encoding="utf-8") as f:
        docs = json.load(f)
    with open("queries.json", encoding="utf-8") as f:
        items = json.load(f)
    assert len(docs) >= 5
    assert sum(q["doc"] is not None for q in items) >= 8
    for q in items:
        assert q["split"] in {"dev", "test"}
        if q["doc"] is not None:
            assert q["evidence"] in docs[q["doc"]]
    model = None
    model_load_seconds = None
    try:
        from sentence_transformers import SentenceTransformer
        start = time.perf_counter()
        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2", device="cpu"
        )
        model_load_seconds = time.perf_counter() - start
        print(f"Model load seconds: {model_load_seconds:.6f}")
    except Exception as error:
        print("Embedding backend unavailable:", repr(error))
        print("Continuing with TF-IDF only; install/download the model to complete embeddings.")
    query_texts = [q["query"] for q in items]
    logs = []
    summary = []
    for strategy in ["0", "10", "sentence"]:
        chunks = make_chunks(docs, strategy)
        texts = [c["text"] for c in chunks]
        print(f"\nStrategy={strategy}; chunk_count={len(chunks)}")
        if model is not None:
            lengths = [
                len(model.tokenizer(t, truncation=False)["input_ids"])
                for t in texts + query_texts
            ]
            print("Maximum model token length:", max(lengths),
                  "encoder limit:", model.max_seq_length)
            if max(lengths) > model.max_seq_length:
                raise ValueError("Model input limit exceeded; rechunk or shorten input.")
        for method in ["tfidf", "embedding"]:
            if method == "embedding" and model is None:
                continue
            start = time.perf_counter()
            if method == "tfidf":
                vectorizer = TfidfVectorizer()
                C = vectorizer.fit_transform(texts)
                Q = vectorizer.transform(query_texts)
            else:
                C = model.encode(texts, normalize_embeddings=True)
                Q = model.encode(query_texts, normalize_embeddings=True)
            encode_seconds = time.perf_counter() - start
            start = time.perf_counter()
            scores = (Q @ C.T).toarray() if method == "tfidf" else Q @ C.T
            search_seconds = time.perf_counter() - start
            for split in ["dev", "test"]:
                indices = [i for i, q in enumerate(items) if q["split"] == split]
                metrics = evaluate(scores[indices], chunks, [items[i] for i in indices])
                row = {
                    "strategy": strategy, "method": method, "split": split,
                    "hit_at_3": metrics[0], "mrr_at_3": metrics[1],
                    "chunks": len(chunks), "encoding_seconds": encode_seconds,
                    "search_seconds": search_seconds
                }
                summary.append(row)
                print(row)
            for score_row, q in zip(scores, items):
                top_indices = np.argsort(-score_row, kind="stable")[:3]
                for rank, index in enumerate(top_indices, 1):
                    c = chunks[index]
                    record = {
                        "strategy": strategy, "method": method,
                        "query": q["query"], "split": q["split"], "rank": rank,
                        "score": float(score_row[index]), "chunk_id": c["id"],
                        "doc": c["doc"], "start": c["start"], "end": c["end"],
                        "text": c["text"], "answerable": q["doc"] is not None
                    }
                    logs.append(record)
                    print("TOP", record)
    if logs:
        with open("retrieval_log.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(logs[0]))
            writer.writeheader()
            writer.writerows(logs)
    with open("metrics_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    print("\nSaved retrieval_log.csv and metrics_summary.csv")
    print("Unanswerable queries are logged but excluded from Hit@3/MRR@3.")
if __name__ == "__main__":
    main()
