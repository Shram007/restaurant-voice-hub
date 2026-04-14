"""
MCP server for Restaurant Voice Hub.

Exposes the existing tool endpoints as Model Context Protocol (MCP) callable tools:
  - menu_search
  - order_create_or_update
  - get_eta
  - order_confirm
  - handoff_to_human

Run with:  python backend/mcp_server.py
"""
from __future__ import annotations

import json
import sys
import os

# ── Inline MCP transport (stdio) ─────────────────────────────────────────────
# We implement a minimal JSON-RPC 2.0 / MCP stdio server without requiring
# the `mcp` SDK so no new install is needed.  The server reads one JSON line
# per request from stdin and writes one JSON line per response to stdout.

# ── Import existing services ──────────────────────────────────────────────────
# Add project root to path so imports resolve from any working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Services and models are imported lazily inside dispatch_tool so that importing
# this module (e.g. in tests) does not require a live Supabase connection.
from backend.config import settings


# ── Tool registry ─────────────────────────────────────────────────────────────

TOOLS = {
    "menu_search": {
        "name": "menu_search",
        "description": "Search the restaurant menu by keyword. Returns matching items with name, category, price, and description.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "string",
                    "description": "The restaurant identifier (defaults to the configured default).",
                },
                "query": {
                    "type": "string",
                    "description": "Optional keyword to filter menu items.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of items to return (default 20).",
                    "default": 20,
                },
            },
            "required": [],
        },
    },
    "order_create_or_update": {
        "name": "order_create_or_update",
        "description": "Create a new order or update an existing pending order with additional items.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "string"},
                "call_id": {
                    "type": "string",
                    "description": "ElevenLabs call identifier for the current session.",
                },
                "customer_name": {"type": "string"},
                "phone": {"type": "string"},
                "fulfillment": {
                    "type": "string",
                    "enum": ["pickup", "delivery"],
                    "description": "Fulfillment type (default: pickup).",
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_id": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "modifier_selections": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "modifier_name": {"type": "string"},
                                        "option": {"type": "string"},
                                    },
                                    "required": ["modifier_name", "option"],
                                },
                            },
                            "special_instructions": {"type": "string"},
                        },
                        "required": ["item_id", "quantity"],
                    },
                },
                "order_id": {
                    "type": "string",
                    "description": "Existing order ID to update (omit to create new).",
                },
                "notes": {"type": "string"},
            },
            "required": ["restaurant_id", "call_id"],
        },
    },
    "get_eta": {
        "name": "get_eta",
        "description": "Get the estimated preparation time for a restaurant order.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "string"},
                "order_id": {"type": "string"},
            },
            "required": ["restaurant_id", "order_id"],
        },
    },
    "order_confirm": {
        "name": "order_confirm",
        "description": "Confirm a pending order and mark it as accepted.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "string"},
                "order_id": {"type": "string"},
                "payment_mode": {
                    "type": "string",
                    "enum": ["pay_at_pickup", "payment_link"],
                    "description": "Payment mode (default: pay_at_pickup).",
                },
            },
            "required": ["restaurant_id", "order_id"],
        },
    },
    "handoff_to_human": {
        "name": "handoff_to_human",
        "description": "Escalate the call to a human agent when the AI cannot handle the request.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "string"},
                "call_id": {"type": "string"},
                "reason": {"type": "string", "description": "Reason for escalation."},
                "order_id": {"type": "string"},
                "summary_for_human": {"type": "string"},
            },
            "required": ["restaurant_id", "call_id", "reason"],
        },
    },
}


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def dispatch_tool(name: str, arguments: dict) -> str:
    """Call the underlying service and return the result as a JSON string."""
    # Lazy imports so that loading this module does not require a live DB connection.
    from backend.services.menu_service import MenuService
    from backend.services.order_service import OrderService
    from backend.models import (
        OrderCreateRequest,
        EtaRequest,
        OrderConfirmRequest,
        HandoffRequest,
    )

    if name == "menu_search":
        result = MenuService.search_menu(
            restaurant_id=arguments.get("restaurant_id", settings.DEFAULT_RESTAURANT_ID),
            query=arguments.get("query"),
            limit=arguments.get("limit", 20),
        )
        return json.dumps(result.dict() if hasattr(result, "dict") else result)

    elif name == "order_create_or_update":
        req = OrderCreateRequest(**arguments)
        result = OrderService.create_or_update_order(req)
        return json.dumps(result.dict() if hasattr(result, "dict") else result)

    elif name == "get_eta":
        req = EtaRequest(**arguments)
        result = OrderService.get_eta(req.restaurant_id)
        return json.dumps(result.dict() if hasattr(result, "dict") else result)

    elif name == "order_confirm":
        req = OrderConfirmRequest(**arguments)
        result = OrderService.confirm_order(req)
        return json.dumps(result.dict() if hasattr(result, "dict") else result)

    elif name == "handoff_to_human":
        req = HandoffRequest(**arguments)
        result = OrderService.handoff_to_human(req)
        return json.dumps(result.dict() if hasattr(result, "dict") else result)

    else:
        raise ValueError(f"Unknown tool: {name}")


# ── JSON-RPC / MCP handler ────────────────────────────────────────────────────

def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    # MCP initialize handshake
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "restaurant-voice-hub", "version": "1.0.0"},
            },
        }

    # List available tools
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": list(TOOLS.values())},
        }

    # Call a tool
    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        try:
            content = dispatch_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": content}],
                    "isError": False,
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": str(exc)}],
                    "isError": True,
                },
            }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


# ── stdio transport loop ──────────────────────────────────────────────────────

def run_stdio():
    """Read JSON-RPC requests from stdin, write responses to stdout."""
    print("[mcp_server] Restaurant Voice Hub MCP server started (stdio)", file=sys.stderr, flush=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
        else:
            response = handle_request(request)
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    run_stdio()
