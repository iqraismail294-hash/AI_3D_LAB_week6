import re
samples = [
    "AI, search!",
    "I can't log in.",
    "help@example.com",
    "CS4944 version 2.1",
    "",
    "یہ ایک مثال ہے"
]
def compare_tokens(text):
    whitespace = text.split()
    word_like = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
    print("\nOriginal:", repr(text))
    print("Whitespace tokens:", whitespace, "| count:", len(whitespace))
    print("Word-like tokens:", word_like, "| count:", len(word_like))
if __name__ == "__main__":
    for sample in samples:
        compare_tokens(sample)
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2", device="cpu"
        )
        print("\nModel subword tokenization (two English examples):")
        for sample in samples[:2]:
            print(repr(sample), "->", model.tokenizer.tokenize(sample))
    except Exception as error:
        print("\nModel tokenizer comparison skipped.")
        print("Install sentence-transformers and allow the first model download.")
        print("Reason:", error)
    assert re.findall(r"\b\w+\b", "", flags=re.UNICODE) == []
