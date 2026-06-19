import math
from collections import Counter


class TFIDFEmbedder:
    """Pure-stdlib TF-IDF embedder — no numpy, no sklearn."""

    def __init__(self):
        self._idf: dict[str, float] = {}
        self._doc_count: int = 0

    def fit(self, documents: list[str]) -> None:
        self._doc_count = len(documents)
        # Count how many docs each term appears in
        doc_freq: Counter = Counter()
        for doc in documents:
            terms = set(self._tokenize(doc))
            for term in terms:
                doc_freq[term] += 1
        # IDF = log((N + 1) / (df + 1)) + 1  (smoothed)
        self._idf = {
            term: math.log((self._doc_count + 1) / (df + 1)) + 1
            for term, df in doc_freq.items()
        }

    def transform(self, text: str) -> dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        tf: Counter = Counter(tokens)
        total = len(tokens)
        vector: dict[str, float] = {}
        for term, count in tf.items():
            tf_val = count / total
            idf_val = self._idf.get(term, math.log((self._doc_count + 1) / 1) + 1)
            vector[term] = tf_val * idf_val
        return vector

    def cosine_similarity(self, vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        dot = sum(vec_a.get(t, 0.0) * vec_b.get(t, 0.0) for t in vec_b)
        mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
        mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [
            w.lower().strip(".,!?;:\"'()")
            for w in text.split()
            if len(w) > 2
        ]
