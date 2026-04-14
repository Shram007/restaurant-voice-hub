"""
Smoke tests for the MCP server's JSON-RPC handler.
Run with: python backend/mcp_server_test.py
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.mcp_server import handle_request, TOOLS

def test_initialize():
    resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["result"]["serverInfo"]["name"] == "restaurant-voice-hub"
    print("[PASS] initialize handshake")

def test_tools_list():
    resp = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    names = [t["name"] for t in resp["result"]["tools"]]
    for expected in ["menu_search", "order_create_or_update", "get_eta", "order_confirm", "handoff_to_human"]:
        assert expected in names, f"Missing tool: {expected}"
    print(f"[PASS] tools/list — {len(names)} tools registered")

def test_unknown_method():
    resp = handle_request({"jsonrpc": "2.0", "id": 3, "method": "unknown/method", "params": {}})
    assert "error" in resp
    print("[PASS] unknown method returns error")

if __name__ == "__main__":
    test_initialize()
    test_tools_list()
    test_unknown_method()
    print("All MCP smoke tests passed.")
