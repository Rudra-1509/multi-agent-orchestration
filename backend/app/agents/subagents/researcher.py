from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

from app.tools.scrape.web_scraper_tool import scrape_tool
from app.tools.search.tavily_tool import search_tool
from app.tools.memory.chroma_tool import store_memory_tool
from app.graph.state import AgentState

def search_node(state: AgentState) -> AgentState:
    """Search using Tavily"""
    query = state["query"]

    results = search_tool.invoke({"query": query})

    return {
        "search_results": results
    }


def clean_node(state: AgentState) -> AgentState:
    """Clean and extract URLs from search results"""
    results = state["search_results"]

    cleaned = []
    urls = []

    for r in results:
        url = r.get("url", "").strip().lower()
        title = r.get("title", "").strip()

        if url:
            cleaned.append({
                "url": url,
                "title": title
            })
            urls.append(url)

    return {
        "search_results": cleaned,   
        "urls": urls
    }


def scrape_node(state: AgentState) -> AgentState:
    """Scrape top URLs"""
    urls = state.get("urls", [])[:3]   

    data = []

    for url in urls:
        try:
            text = scrape_tool.invoke({"url": url})
            data.append(text)
        except Exception as e:
            data.append(f"Error scraping {url}: {str(e)}")

    return {
        "scraped_data": data
    }


def store_node(state: AgentState) -> AgentState:
    """Store scraped data into Chroma"""
    scraped_data_list = state.get("scraped_data", [])

    combined_text = "\n\n".join([str(x) for x in scraped_data_list])

    try:
        store_memory_tool.invoke({"text": combined_text})
        status = "stored"
    except Exception as e:
        status = f"error: {str(e)}"

    return {
        "processed_data": combined_text,
        "status": status
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("search", search_node)
    graph.add_node("clean", clean_node)
    graph.add_node("scrape", scrape_node)
    graph.add_node("store", store_node)

    graph.add_edge(START, "search")
    graph.add_edge("search", "clean")
    graph.add_edge("clean", "scrape")
    graph.add_edge("scrape", "store")
    graph.add_edge("store", END)

    return graph.compile()
