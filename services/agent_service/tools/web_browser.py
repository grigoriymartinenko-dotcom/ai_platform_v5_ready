import httpx
from bs4 import BeautifulSoup
# Правильно для всех инструментов
from services.agent_service.tools.tool_registry import register_tool

SEARCH_URL = "https://duckduckgo.com/html/"


async def search_web(query, max_results=3):
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            SEARCH_URL,
            data={"q": query}
        )

        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.select(".result__a")

        for link in links[:max_results]:
            results.append({
                "title": link.text,
                "url": link.get("href")
            })

    return results


async def read_page(url):
    try:

        async with httpx.AsyncClient(timeout=30) as client:

            r = await client.get(url)

            soup = BeautifulSoup(r.text, "html.parser")

            for tag in soup(["script", "style"]):
                tag.decompose()

            text = soup.get_text(separator=" ")

            return text[:6000]

    except Exception as e:

        return f"Ошибка чтения страницы: {str(e)}"


async def browse(query):
    register_tool("browse_web", "Search and read web pages", browse)
    results = await search_web(query)

    pages = []

    for r in results:
        content = await read_page(r["url"])

        pages.append(
            f"""
TITLE: {r['title']}
URL: {r['url']}
CONTENT:
{content}
"""
        )

    return "\n\n".join(pages)


def fetch_page():
    return None
