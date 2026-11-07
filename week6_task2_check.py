from week6_task2_chunks import make_chunks
from lab6_search import Retriever
docs = {
    "it": "A forgotten password can be reset using the recovery link. Keep recovery codes private.",
    "assessment": "Assignments are uploaded through the learning portal. Submit the final file as a PDF.",
    "printer": "For blank printer pages, check ink levels and run the cleaning utility."
}
queries = [
    "How can I regain access to my account?",
    "Where should I hand in my coursework?",
    "My printer is producing empty pages. What should I check?"
]
records = make_chunks(docs, "sentence")

for backend in ["tfidf", "embedding"]:
    try:
        engine = Retriever(records, backend)
    except Exception as error:
        print(f"{backend} backend unavailable:", error)
        continue
    print("\\nBackend:", backend)
    for query in queries:
        print("\\nQuery:", query)
        hits = engine.search(query, k=3)
        if not hits:
            print("No lexical match.")
        for record, score in hits:
            print(record["id"], f"{score:.3f}", record["text"])
