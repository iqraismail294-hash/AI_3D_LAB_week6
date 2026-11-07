import json
from task2_chunks import make_chunks
with open("corpus.json", encoding="utf-8") as f:
    docs = json.load(f)
with open("queries.json", encoding="utf-8") as f:
    queries = json.load(f)
evidence_by_doc = {}
for q in queries:
    if q["doc"] is not None:
        evidence_by_doc.setdefault(q["doc"], set()).add(q["evidence"])
original_words = sum(len(text.split()) for text in docs.values())
print("Original document word units:", original_words)
print("strategy, chunks, emitted_word_units, duplicated_word_units")
for strategy in ["0", "10", "sentence"]:
    chunks = make_chunks(docs, strategy)
    emitted = sum(len(c["text"].split()) for c in chunks)
    duplicate = emitted - original_words
    preserved = 0
    total = sum(len(v) for v in evidence_by_doc.values())
    for doc_id, evidences in evidence_by_doc.items():
        own_chunks = [c for c in chunks if c["doc"] == doc_id]
        for evidence in evidences:
            if any(evidence in c["text"] for c in own_chunks):
                preserved += 1
    sizes = [len(c["text"].split()) for c in chunks]
    print(f"{strategy}, {len(chunks)}, {emitted}, {duplicate}")
    print("  chunk word sizes min/max:", min(sizes), max(sizes))
    print(f"  complete labeled evidence in one chunk: {preserved}/{total}")
