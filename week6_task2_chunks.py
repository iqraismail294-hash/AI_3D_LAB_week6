import re
def word_spans(text):
    """Return character start/end positions for whitespace-separated words."""
    return [(match.start(), match.end()) for match in re.finditer(r"\S+", text)]
def windows(text, size=40, overlap=10, offset=0):
    """Create fixed word windows; offsets point into the original document."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Require size > 0 and 0 <= overlap < size.")
    spans = word_spans(text)
    result = []
    step = size - overlap
    for i in range(0, len(spans), step):
        j = min(i + size, len(spans))
        result.append((offset + spans[i][0], offset + spans[j - 1][1]))
        if j == len(spans):
            break
    return result
def sentence_chunks(text, size=40):
    """Pack complete sentences up to size; split overlong sentences as fallback."""
    if size <= 0:
        raise ValueError("size must be positive.")
    cuts = [0] + [m.end() for m in re.finditer(r"[.!?]\s+", text)] + [len(text)]
    output, pending, count = [], None, 0
    for start, end in zip(cuts, cuts[1:]):
        segment = text[start:end]
        n_words = len(segment.split())
        if n_words == 0:
            continue
        if n_words > size:
            if pending is not None:
                output.append(pending)
                pending, count = None, 0
            output.extend(windows(segment, size=size, overlap=0, offset=start))
        elif pending is not None and count + n_words <= size:
            pending = (pending[0], end)
            count += n_words
        else:
            if pending is not None:
                output.append(pending)
            pending, count = (start, end), n_words
    if pending is not None:
        output.append(pending)
    return output
def make_chunks(docs, strategy):
    """strategy is '0', '10', or 'sentence'."""
    chunks = []
    for doc_id, source_text in docs.items():
        if strategy == "sentence":
            spans = sentence_chunks(source_text, size=40)
        elif strategy in {"0", "10"}:
            spans = windows(source_text, size=40, overlap=int(strategy))
        else:
            raise ValueError("Strategy must be '0', '10', or 'sentence'.")
        for number, (start, end) in enumerate(spans):
            chunks.append({
                "id": f"{doc_id}:{number}",
                "doc": doc_id,
                "source": f"{doc_id}.txt",
                "start": start,
                "end": end,
                "text": source_text[start:end]
            })
    return chunks
if __name__ == "__main__":
    assert windows("") == []
    assert windows("short text") == [(0, 10)]
    try:
        windows("a b", 2, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid overlap was accepted.")
    long_sentence = " ".join(["word"] * 95) + "."
    assert all(len(long_sentence[a:b].split()) <= 40
               for a, b in sentence_chunks(long_sentence))
    docs = {"example": "Reset your password. Keep recovery codes private."}
    for strategy in ["0", "10", "sentence"]:
        for chunk in make_chunks(docs, strategy):
            assert chunk["text"] == docs[chunk["doc"]][chunk["start"]:chunk["end"]]
            print(strategy, chunk)
    print("Task 2 boundary tests passed.")
