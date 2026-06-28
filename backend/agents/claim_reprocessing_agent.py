import os
import re
import json
import requests as http_requests
from db_operations import get_all_claims, get_claim_by_id
from reprocessing import start_reprocessing, ClaimNotFound, ClaimNotReprocessable
from config import (
    CONFLUENCE_BASE_URL, CONFLUENCE_USERNAME,
    CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY,
)

try:
    import anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

try:
    from ddgs import DDGS
    _HAS_DDG = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        _HAS_DDG = True
    except ImportError:
        _HAS_DDG = False

try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False

SYSTEM_PROMPT = """You are a Claims Management Agent for an insurance company. You help users with a wide range of questions including:

- **Claims management**: query, reprocess, and report on insurance claims in the database
- **Policy & insurance questions**: use web search to find accurate, up-to-date answers
- **Internal documentation**: search Confluence pages for company policies and procedures
- **General knowledge**: answer any question by searching the web when needed

Guidelines:
- Always use tools to get real, current information — never make up details
- Use markdown formatting (bold, bullet points, tables) for clarity
- For claims questions, query the database tools first
- For policy or procedure questions, search Confluence first, then the web
- For general questions, search the web directly
- Cite sources when referencing web content or Confluence pages
- Claims have exactly 4 statuses: **UI Draft**, **EDI Processing**, **EDI Complete**, **EDI Accepted**
- **UI Draft**: provider has not yet submitted the claim on the portal
- **EDI Processing**: claim is actively being processed through the EDI system (transient, ~10 seconds)
- **EDI Complete**: claim submitted successfully for the first time
- **EDI Accepted**: adjusted claim accepted through the EDI system
- Only **EDI Processing** claims can be reprocessed (takes ~10 seconds → EDI Complete)
- **UI Draft** claims are view-only and cannot be reprocessed"""

TOOLS = [
    {
        "name": "get_all_claims",
        "description": "Retrieve all insurance claims from the database with their current status, amounts, and descriptions.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_claim_details",
        "description": "Get detailed information about a specific claim by its ID or claim number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim_id": {"type": "string", "description": "The claim ID (e.g. '1', '13') or claim number (e.g. 'ZX02FL1111')"}
            },
            "required": ["claim_id"]
        }
    },
    {
        "name": "reprocess_claim",
        "description": "Reprocess a claim. Only works on claims with status 'EDI Processing'. Schedules the claim to become EDI Complete after 10 seconds.",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim_id": {"type": "string", "description": "The ID of the claim to reprocess"}
            },
            "required": ["claim_id"]
        }
    },
    {
        "name": "get_dashboard_stats",
        "description": "Get aggregate statistics about all claims: total count, total amount, and status breakdown.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "web_search",
        "description": "Search the web for any topic — insurance policies, medical terminology, regulatory information, general knowledge, or anything else. Returns titles, URLs, and snippets from top results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "max_results": {"type": "integer", "description": "Number of results to return (default 5, max 10)", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_webpage",
        "description": "Fetch and read the text content of any webpage or URL — useful for reading specific articles, documentation pages, or Confluence pages directly.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The full URL to fetch"},
                "max_chars": {"type": "integer", "description": "Maximum characters to return (default 4000)", "default": 4000}
            },
            "required": ["url"]
        }
    },
    {
        "name": "search_confluence",
        "description": "Search your company's Confluence knowledge base for internal policies, procedures, and documentation. Requires Confluence credentials to be configured.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query for Confluence"},
                "space_key": {"type": "string", "description": "Optional Confluence space key to limit the search scope"}
            },
            "required": ["query"]
        }
    },
]


class ClaimReprocessingAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        self.client = anthropic.Anthropic(api_key=api_key) if (_HAS_ANTHROPIC and api_key) else None

    def process_message(self, message, history=None):
        if self.client:
            return self._process_with_llm(message, history or [])
        return self._process_with_keywords(message)

    # ── LLM path ──────────────────────────────────────────────────────────────

    def _process_with_llm(self, message, history):
        api_messages = []
        for msg in history[-20:]:
            role = "user" if msg.get("sender") == "user" else "assistant"
            text = str(msg.get("text", "")).strip()
            if not text:
                continue
            if api_messages and api_messages[-1]["role"] == role:
                continue
            api_messages.append({"role": role, "content": text})

        while api_messages and api_messages[-1]["role"] == "assistant":
            api_messages.pop()

        api_messages.append({"role": "user", "content": message})

        for _ in range(15):
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=4096,
                system=[{
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }],
                tools=TOOLS,
                messages=api_messages,
            )

            if response.stop_reason == "end_turn":
                text = next((b.text for b in response.content if hasattr(b, "text")), "")
                return {"response": text, "details": None}

            if response.stop_reason == "tool_use":
                api_messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        })
                api_messages.append({"role": "user", "content": tool_results})
            else:
                break

        return {"response": "I encountered an issue processing your request. Please try again.", "details": None}

    def _execute_tool(self, tool_name, tool_input):
        if tool_name == "get_all_claims":
            return {"claims": [dict(c) for c in get_all_claims()]}

        if tool_name == "get_claim_details":
            claim = get_claim_by_id(tool_input.get("claim_id", ""))
            return {"claim": dict(claim)} if claim else {"error": f"Claim '{tool_input.get('claim_id')}' not found"}

        if tool_name == "reprocess_claim":
            return self._tool_reprocess(tool_input.get("claim_id", ""))

        if tool_name == "get_dashboard_stats":
            return self._tool_stats()

        if tool_name == "web_search":
            return self._tool_web_search(tool_input.get("query", ""), tool_input.get("max_results", 5))

        if tool_name == "fetch_webpage":
            return self._tool_fetch_webpage(tool_input.get("url", ""), tool_input.get("max_chars", 4000))

        if tool_name == "search_confluence":
            return self._tool_search_confluence(tool_input.get("query", ""), tool_input.get("space_key", ""))

        return {"error": f"Unknown tool: {tool_name}"}

    def _tool_reprocess(self, claim_id):
        try:
            start_reprocessing(claim_id, 'agent')
        except ClaimNotFound:
            return {"error": f"Claim '{claim_id}' not found"}
        except ClaimNotReprocessable as e:
            return {"error": f"Cannot reprocess claim {claim_id}: status is '{e.current_status}'. Only EDI Processing claims can be reprocessed."}
        return {"success": True, "claim_id": claim_id, "message": "Reprocessing started — will become EDI Complete in 10 seconds"}

    def _tool_stats(self):
        claims = get_all_claims()
        total = len(claims)
        total_amount = sum(c["amount"] for c in claims)
        status_counts = {}
        for c in claims:
            status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1
        return {
            "total_claims": total,
            "total_amount": round(total_amount, 2),
            "avg_amount": round(total_amount / total, 2) if total else 0,
            "status_breakdown": status_counts,
        }

    def _tool_web_search(self, query, max_results=5):
        if not _HAS_DDG:
            return {"error": "Web search unavailable — install duckduckgo-search: pip install duckduckgo-search"}
        try:
            max_results = min(int(max_results), 10)
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return {"results": [], "message": "No results found"}
            return {
                "results": [
                    {"title": r.get("title"), "url": r.get("href"), "snippet": r.get("body")}
                    for r in results
                ]
            }
        except Exception as e:
            return {"error": f"Web search failed: {str(e)}"}

    def _tool_fetch_webpage(self, url, max_chars=4000):
        if not url:
            return {"error": "URL is required"}
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; ClaimsAgent/1.0)"}
            resp = http_requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            if _HAS_BS4:
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)
            else:
                text = resp.text
            text = "\n".join(line for line in text.splitlines() if line.strip())
            return {"url": url, "content": text[:max_chars], "truncated": len(text) > max_chars}
        except Exception as e:
            return {"error": f"Failed to fetch {url}: {str(e)}"}

    def _tool_search_confluence(self, query, space_key=""):
        if not CONFLUENCE_BASE_URL or not CONFLUENCE_API_TOKEN:
            return {
                "error": "Confluence is not configured. Add CONFLUENCE_BASE_URL, CONFLUENCE_USERNAME, and CONFLUENCE_API_TOKEN to backend/.env to enable this feature."
            }
        try:
            space = space_key or CONFLUENCE_SPACE_KEY
            cql = f'text ~ "{query}" AND type = page'
            if space:
                cql += f' AND space = "{space}"'
            resp = http_requests.get(
                f"{CONFLUENCE_BASE_URL.rstrip('/')}/wiki/rest/api/content/search",
                params={"cql": cql, "limit": 5, "expand": "body.storage"},
                auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for page in data.get("results", []):
                body_html = page.get("body", {}).get("storage", {}).get("value", "")
                if _HAS_BS4 and body_html:
                    soup = BeautifulSoup(body_html, "html.parser")
                    body_text = soup.get_text(separator=" ", strip=True)[:1500]
                else:
                    body_text = ""
                results.append({
                    "title": page.get("title"),
                    "url": f"{CONFLUENCE_BASE_URL.rstrip('/')}/wiki{page.get('_links', {}).get('webui', '')}",
                    "excerpt": body_text,
                })
            return {"results": results, "total": data.get("totalSize", 0)}
        except Exception as e:
            return {"error": f"Confluence search failed: {str(e)}"}

    # ── Keyword fallback (no API key) ──────────────────────────────────────────

    def _process_with_keywords(self, message):
        msg = message.lower()
        if any(w in msg for w in ["reprocess", "process again"]):
            return self._handle_reprocess(message)
        if any(w in msg for w in ["status", "check", "pending"]):
            return self._handle_status_check()
        if any(w in msg for w in ["analytics", "report", "summary", "stats"]):
            return self._handle_analytics()
        if any(w in msg for w in ["search", "web", "find", "what is", "how to"]):
            return self._handle_web_fallback(message)
        if any(w in msg for w in ["confluence", "policy", "procedure", "document"]):
            return self._handle_confluence_fallback()
        if any(w in msg for w in ["claim", "clm"]):
            return self._handle_claim_query(message)
        return self._handle_general_inquiry()

    def _handle_reprocess(self, message):
        claim_id = self._extract_claim_id(message)
        if not claim_id:
            return {"response": "Please specify a claim ID to reprocess (e.g., *Reprocess claim 2*).", "details": None}
        claim = get_claim_by_id(claim_id)
        if not claim:
            return {"response": f"Claim {claim_id} was not found.", "details": None}
        if claim['status'] != 'EDI Processing':
            return {
                "response": f"**Cannot reprocess claim {claim_id}.**\n\nCurrent status is **{claim['status']}**. Only **EDI Processing** claims can be reprocessed.",
                "details": None,
            }
        self._tool_reprocess(claim_id)
        return {
            "response": (
                f"**Reprocessing started for claim {claim_id}**\n\n"
                f"- **Amount:** ${claim['amount']:.2f}\n"
                f"- **Description:** {claim['description']}\n"
                f"- **Status:** EDI Processing → **EDI Complete** in 10 seconds"
            ),
            "details": {"action": "reprocess", "claim_id": claim_id},
        }

    def _handle_status_check(self):
        claims = get_all_claims()
        emoji = {"UI Draft": "📝", "EDI Processing": "⚙️", "EDI Complete": "✅", "EDI Accepted": "🔄"}
        lines = [f"{emoji.get(c['status'], '📋')} **{c['id']}**: {c['status']} — {c['description']}" for c in claims]
        ui_draft       = sum(1 for c in claims if c["status"] == "UI Draft")
        edi_processing = sum(1 for c in claims if c["status"] == "EDI Processing")
        edi_complete   = sum(1 for c in claims if c["status"] == "EDI Complete")
        edi_accepted   = sum(1 for c in claims if c["status"] == "EDI Accepted")
        response = "**Current Claims Status**\n\n" + "\n".join(lines)
        response += f"\n\n**Summary:** {ui_draft} UI Draft · {edi_processing} EDI Processing · {edi_complete} EDI Complete · {edi_accepted} EDI Accepted"
        return {"response": response, "details": None}

    def _handle_claim_query(self, message):
        claim_id = self._extract_claim_id(message)
        if claim_id:
            claim = get_claim_by_id(claim_id)
            if claim:
                return {
                    "response": (
                        f"**Claim {claim_id} Details**\n\n"
                        f"- **Status:** {claim['status']}\n"
                        f"- **Amount:** ${claim['amount']:.2f}\n"
                        f"- **Description:** {claim['description']}\n"
                        f"- **Created:** {claim['created_date']}\n"
                        f"- **Notes:** {claim['notes']}"
                    ),
                    "details": dict(claim),
                }
        claims = get_all_claims()
        lines = [f"- **{c['id']}**: {c['description']} (${c['amount']:.2f}) — {c['status']}" for c in claims]
        return {"response": "**Available Claims**\n\n" + "\n".join(lines), "details": None}

    def _handle_analytics(self):
        claims = get_all_claims()
        if not claims:
            return {"response": "No claims data available.", "details": {}}
        total = len(claims)
        total_amount = sum(c["amount"] for c in claims)
        status_counts = {}
        for c in claims:
            status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1
        lines = [f"- **{s}:** {n} ({n/total*100:.1f}%)" for s, n in status_counts.items()]
        response = (
            f"**Claims Analytics Report**\n\n"
            f"- **Total Claims:** {total}\n"
            f"- **Total Amount:** ${total_amount:,.2f}\n"
            f"- **Average Amount:** ${total_amount/total:,.2f}\n\n"
            f"**Status Breakdown:**\n" + "\n".join(lines)
        )
        return {"response": response, "details": {"total": total, "total_amount": total_amount}}

    def _handle_web_fallback(self, message):
        return {
            "response": (
                "I can search the web for you, but that feature requires the **Anthropic API key** to be configured.\n\n"
                "Please add `ANTHROPIC_API_KEY` to `backend/.env` and restart the server to enable web search, Confluence search, and AI-powered responses."
            ),
            "details": None,
        }

    def _handle_confluence_fallback(self):
        return {
            "response": (
                "To search your Confluence knowledge base, two things are needed:\n\n"
                "1. **Anthropic API key** — add `ANTHROPIC_API_KEY` to `backend/.env`\n"
                "2. **Confluence credentials** — add `CONFLUENCE_BASE_URL`, `CONFLUENCE_USERNAME`, and `CONFLUENCE_API_TOKEN` to `backend/.env`\n\n"
                "Restart the server after updating."
            ),
            "details": None,
        }

    def _handle_general_inquiry(self):
        return {
            "response": (
                "I'm your **Claims Management Agent**. Here's what I can help with:\n\n"
                "**Claims**\n"
                "- Show all claims or details for a specific claim\n"
                "- Reprocess a claim (only *Processing* status)\n"
                "- Generate claims analytics and reports\n\n"
                "**Knowledge**\n"
                "- Search the web for insurance policies, medical info, regulations\n"
                "- Search your Confluence knowledge base for internal procedures\n"
                "- Read and summarize any webpage or document URL\n\n"
                "**Examples:** *Reprocess claim 9* · *Show me all rejected claims* · *What is the ICD-10 code for knee replacement?* · *Search Confluence for pre-authorization policy*"
            ),
            "details": None,
        }

    def _extract_claim_id(self, message):
        match = re.search(r"CLM-\d+-\d+", message, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        match = re.search(r"\b(\d+)\b", message)
        return match.group(1) if match else None
