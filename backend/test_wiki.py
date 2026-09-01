import httpx

query = "artificial intelligence in manufacturing"
url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&utf8=&format=json"
headers = {"User-Agent": "EnterpriseResearchAgent/1.0 (enterprise-research-bot@example.com)"}
r = httpx.get(url, headers=headers, timeout=5)
print("Wikipedia text search status:", r.status_code)
data = r.json()
for item in data.get("query", {}).get("search", [])[:3]:
    print(" - Title:", item["title"])
    print("   Snippet:", item["snippet"][:100])
