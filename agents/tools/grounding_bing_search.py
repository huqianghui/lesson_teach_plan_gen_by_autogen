from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import asyncio
import json
import os
from typing import Dict, List, Optional
from urllib.parse import urljoin
import chainlit as cl

import html2text
import httpx
from autogen_core.tools import FunctionTool
from bs4 import BeautifulSoup


async def fetch_page_content(url: str, max_length: Optional[int] = 50000) -> str:
    """Helper function to fetch and convert webpage content to markdown"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Convert relative URLs to absolute
            for tag in soup.find_all(["a", "img"]):
                if tag.get("href"):
                    tag["href"] = urljoin(url, tag["href"])
                if tag.get("src"):
                    tag["src"] = urljoin(url, tag["src"])

            h2t = html2text.HTML2Text()
            h2t.body_width = 0
            h2t.ignore_images = False
            h2t.ignore_emphasis = False
            h2t.ignore_links = False
            h2t.ignore_tables = False

            markdown = h2t.handle(str(soup))

            if max_length and len(markdown) > max_length:
                markdown = markdown[:max_length] + "\n...(truncated)"

            return markdown.strip()

    except Exception as e:
        return f"Error fetching content: {str(e)}"


@cl.step(type="tool", name="grounding_bing_search")
async def grounding_bing_search(
    query: str,
    include_content: bool = True,
    content_max_length: Optional[int] = 10000,
) -> List[Dict[str, str]]:
    """
    Perform a grounded search using Azure AI Project Client.

    Args:
        query: Search query string
        include_content: Include full webpage content in markdown format
        content_max_length: Maximum length of webpage content (if included)

    Returns:
        List[Dict[str, str]]: List of search results with citations

    Raises:
        ValueError: If API credentials are invalid or request fails
    """
    try:
        # Set up Azure credential and client
        credential = DefaultAzureCredential(
            exclude_workload_identity_credential=True,
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True,
            exclude_shared_token_cache_credential=True,
            exclude_visual_studio_code_credential=True,
            exclude_developer_cli_credential=True,
            exclude_cli_credential=False,
            exclude_interactive_browser_credential=True,
            exclude_powershell_credential=True
        )

        project_client = AIProjectClient.from_connection_string(
            credential=credential,
            conn_str="eastus.api.azureml.ms;7a03e9b8-18d6-48e7-b186-0ec68da9e86f;ai-hub-rg;azure-ai-agent-east-us-prj"
        )

        agent = project_client.agents.get_agent("asst_a0xGpCD356KyMv0KmP4pGEWZ")
        
        # Create a new thread for each search request
        thread = project_client.agents.create_thread()
        print(f"Created new thread: {thread.id} for query: {query}")

        # Create message with user's query
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # Process the query
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Get all messages in the thread
        messages = project_client.agents.list_messages(thread_id=thread.id)
        
        # Process citations from AI response
        url_citations = {}
        for text_message in messages.text_messages:
            message_data = text_message.as_dict()
            if message_data['type'] == 'text' and 'annotations' in message_data['text']:
                annotations = message_data['text'].get('annotations', [])
                # Extract URL citations
                for annotation in annotations:
                    if annotation['type'] == 'url_citation' and 'url_citation' in annotation:
                        summary = message_data['text'].get("value")
                        url = annotation['url_citation']['url']
                        title = annotation['url_citation']['title']
                        
                        # Store unique citations
                        if url not in url_citations:
                            url_citations[url] = {
                                "title": title,
                                "summary": summary
                            }

        # Format results similar to bing_search
        results = []
        for url, data in url_citations.items():
            print("grounding_bing_search***********\n")
            print("url:" + url)
            print("summary:" + data["summary"])
            print("title:" + data["title"])

            result = {
                "summary": data["summary"],
                "title": data["title"],
                "link": url
            }
            
            if include_content:
                result["content"] = await fetch_page_content(
                    url, max_length=content_max_length
                )
                
            results.append(result)
            
        # Optional: Delete the thread to clean up resources
        # Uncomment if you want to delete threads after use
        # try:
        #     project_client.agents.delete_thread(thread_id=thread.id)
        #     print(f"Deleted thread: {thread.id}")
        # except Exception as del_err:
        #     print(f"Could not delete thread {thread.id}: {str(del_err)}")

        return results

    except Exception as e:
        raise ValueError(f"Grounding search request failed: {str(e)}")


grounding_bing_search_tool = FunctionTool(
    grounding_bing_search,
    name="grounding_bing_search",
    description="\n    Perform grounded searches using Azure AI Project Client.\n    Retrieves search results with citations from AI responses.\n    Requires Azure authentication.\n    ",
    global_imports=[
        {"module": "typing", "imports": ["List", "Dict", "Optional"]},
        "os",
        "httpx",
        "html2text",
        {"module": "bs4", "imports": ["BeautifulSoup"]},
        {"module": "urllib.parse", "imports": ["urljoin"]},
        {"module": "azure.ai.projects", "imports": ["AIProjectClient"]},
        {"module": "azure.identity", "imports": ["DefaultAzureCredential"]},
        "functools",
    ],
)


async def main():
    result = await grounding_bing_search("2025年NBA季后赛，掘金和森林狼G4的比赛情况？")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())