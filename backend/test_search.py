import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.modules.source_search import SourceSearcher

searcher = SourceSearcher()
q = "How is AI transforming manufacturing operations?"
print(f"Testing query: {q}")
keywords = searcher._distill_keywords(q)
print(f"Keywords: '{keywords}'")

print("\n--- Testing Wikipedia ---")
wiki = searcher._search_wikipedia(keywords, max_results=3)
print(f"Wiki results: {wiki}")

print("\n--- Testing ArXiv ---")
arxiv = searcher._search_arxiv(keywords, max_results=3)
print(f"ArXiv results: {arxiv}")

print("\n--- Testing Full Search Query ---")
full = searcher.search_query(q, max_results=4)
print(f"Full results count: {len(full)}")
for r in full:
    print(" ", r["title"], "->", r["url"])
