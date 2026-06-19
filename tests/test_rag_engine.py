import unittest
from rag.embedder import TFIDFEmbedder
from rag.retriever import RAGRetriever


DOCS = [
    "Fixed Deposit is a safe savings product with guaranteed interest rate and capital protection.",
    "Equity investing involves buying company shares with high risk and high long-term return potential.",
    "Mutual Funds pool investor money into diversified portfolios managed by professionals.",
    "Bonds are debt instruments with fixed coupon payments and lower risk than equity.",
    "Recurring Deposit lets you invest monthly for disciplined saving with guaranteed returns.",
]


class TestRAGEngine(unittest.TestCase):
    def setUp(self):
        embedder = TFIDFEmbedder()
        self.retriever = RAGRetriever(embedder=embedder, documents=DOCS)

    def test_known_query_returns_relevant_document(self):
        results = self.retriever.retrieve("equity risk long-term shares")
        self.assertTrue(len(results) > 0)
        # The equity document should be in the results
        self.assertTrue(any("equity" in r.lower() or "shares" in r.lower() for r in results))

    def test_top_k_1_returns_exactly_one(self):
        results = self.retriever.retrieve("fixed deposit savings guaranteed", top_k=1)
        self.assertEqual(len(results), 1)

    def test_unrelated_query_below_threshold_returns_empty(self):
        # A query with no overlap with any document term
        from config.settings import config
        original = config.rag_similarity_threshold
        config.rag_similarity_threshold = 0.99  # impossibly high threshold
        try:
            results = self.retriever.retrieve("xyzzy foobar quux", top_k=3)
            self.assertEqual(results, [])
        finally:
            config.rag_similarity_threshold = original

    def test_top_k_respects_limit(self):
        results = self.retriever.retrieve("investment savings risk return", top_k=2)
        self.assertLessEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
