#!/usr/bin/env python3
"""WhatsApp MCP Server with custom stdio implementation (replacing FastMCP)."""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from whatsapp import (
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    download_media as whatsapp_download_media
)


def _to_dict(obj):
    """Convert dataclass or object to dictionary."""
    if hasattr(obj, '__dataclass_fields__'):
        return asdict(obj)
    if isinstance(obj, dict):
        return obj
    return obj


class WhatsAppMCPServer:
    """WhatsApp MCP Server with custom stdio implementation."""
    
    def __init__(self):
        self.name = "whatsapp"
        self.version = "1.6.0"
    
    def _send_response(self, response: Dict[str, Any]):
        """Send a JSON response."""
        print(json.dumps(response))
        sys.stdout.flush()
    
    def _send_error(self, request_id: Any, code: int, message: str):
        """Send an error response."""
        self._send_response({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        })
    
    async def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "prompts": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "experimental": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        }
    
    async def handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        tools = [
            {
                "name": "search_contacts",
                "description": "Search WhatsApp contacts by name or phone number.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search term to match against contact names or phone numbers"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "list_messages",
                "description": "Get WhatsApp messages matching specified criteria with optional context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "after": {"type": "string", "description": "Optional ISO-8601 formatted string to only return messages after this date"},
                        "before": {"type": "string", "description": "Optional ISO-8601 formatted string to only return messages before this date"},
                        "sender_phone_number": {"type": "string", "description": "Optional phone number to filter messages by sender"},
                        "chat_jid": {"type": "string", "description": "Optional chat JID to filter messages by chat"},
                        "query": {"type": "string", "description": "Optional search term to filter messages by content"},
                        "limit": {"type": "integer", "description": "Maximum number of messages to return (default 20)", "default": 20},
                        "page": {"type": "integer", "description": "Page number for pagination (default 0)", "default": 0},
                        "include_context": {"type": "boolean", "description": "Whether to include messages before and after matches (default True)", "default": True},
                        "context_before": {"type": "integer", "description": "Number of messages to include before each match (default 1)", "default": 1},
                        "context_after": {"type": "integer", "description": "Number of messages to include after each match (default 1)", "default": 1}
                    },
                    "required": []
                }
            },
            {
                "name": "list_chats",
                "description": "Get WhatsApp chats matching specified criteria.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Optional search term to filter chats by name or JID"},
                        "limit": {"type": "integer", "description": "Maximum number of chats to return (default 20)", "default": 20},
                        "page": {"type": "integer", "description": "Page number for pagination (default 0)", "default": 0},
                        "include_last_message": {"type": "boolean", "description": "Whether to include the last message in each chat (default True)", "default": True},
                        "sort_by": {"type": "string", "description": "Field to sort results by, either \"last_active\" or \"name\" (default \"last_active\")", "default": "last_active"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_chat",
                "description": "Get WhatsApp chat metadata by JID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chat_jid": {"type": "string", "description": "The JID of the chat to retrieve"},
                        "include_last_message": {"type": "boolean", "description": "Whether to include the last message (default True)", "default": True}
                    },
                    "required": ["chat_jid"]
                }
            },
            {
                "name": "get_direct_chat_by_contact",
                "description": "Get WhatsApp chat metadata by sender phone number.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sender_phone_number": {"type": "string", "description": "The phone number to search for"}
                    },
                    "required": ["sender_phone_number"]
                }
            },
            {
                "name": "get_contact_chats",
                "description": "Get all WhatsApp chats involving the contact.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "jid": {"type": "string", "description": "The contact's JID to search for"},
                        "limit": {"type": "integer", "description": "Maximum number of chats to return (default 20)", "default": 20},
                        "page": {"type": "integer", "description": "Page number for pagination (default 0)", "default": 0}
                    },
                    "required": ["jid"]
                }
            },
            {
                "name": "get_last_interaction",
                "description": "Get most recent WhatsApp message involving the contact.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "jid": {"type": "string", "description": "The JID of the contact to search for"}
                    },
                    "required": ["jid"]
                }
            },
            {
                "name": "get_message_context",
                "description": "Get context around a specific WhatsApp message.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string", "description": "The ID of the message to get context for"},
                        "before": {"type": "integer", "description": "Number of messages to include before the target message (default 5)", "default": 5},
                        "after": {"type": "integer", "description": "Number of messages to include after the target message (default 5)", "default": 5}
                    },
                    "required": ["message_id"]
                }
            },
            {
                "name": "send_message",
                "description": "Send a WhatsApp message to a person or group. For group chats use the JID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID (e.g., \"123456789@s.whatsapp.net\" or a group JID like \"123456789@g.us\")"},
                        "message": {"type": "string", "description": "The message text to send"}
                    },
                    "required": ["recipient", "message"]
                }
            },
            {
                "name": "send_file",
                "description": "Send a file such as a picture, raw audio, video or document via WhatsApp to the specified recipient. For group messages use the JID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID (e.g., \"123456789@s.whatsapp.net\" or a group JID like \"123456789@g.us\")"},
                        "media_path": {"type": "string", "description": "The absolute path to the media file to send (image, video, document)"}
                    },
                    "required": ["recipient", "media_path"]
                }
            },
            {
                "name": "send_audio_message",
                "description": "Send any audio file as a WhatsApp audio message to the specified recipient. For group messages use the JID. If it errors due to ffmpeg not being installed, use send_file instead.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID (e.g., \"123456789@s.whatsapp.net\" or a group JID like \"123456789@g.us\")"},
                        "media_path": {"type": "string", "description": "The absolute path to the audio file to send (will be converted to Opus .ogg if it's not a .ogg file)"}
                    },
                    "required": ["recipient", "media_path"]
                }
            },
            {
                "name": "download_media",
                "description": "Download media from a WhatsApp message and get the local file path.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string", "description": "The ID of the message containing the media"},
                        "chat_jid": {"type": "string", "description": "The JID of the chat containing the message"}
                    },
                    "required": ["message_id", "chat_jid"]
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": tools
            }
        }
    
    async def handle_call_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "search_contacts":
                result = whatsapp_search_contacts(arguments.get("query", ""))
                result = [_to_dict(c) for c in result]
            elif tool_name == "list_messages":
                result = whatsapp_list_messages(
                    after=arguments.get("after"),
                    before=arguments.get("before"),
                    sender_phone_number=arguments.get("sender_phone_number"),
                    chat_jid=arguments.get("chat_jid"),
                    query=arguments.get("query"),
                    limit=arguments.get("limit", 20),
                    page=arguments.get("page", 0),
                    include_context=arguments.get("include_context", True),
                    context_before=arguments.get("context_before", 1),
                    context_after=arguments.get("context_after", 1)
                )
                if isinstance(result, str):
                    result = [{"text": result}]
                result = [_to_dict(m) for m in result]
            elif tool_name == "list_chats":
                result = whatsapp_list_chats(
                    query=arguments.get("query"),
                    limit=arguments.get("limit", 20),
                    page=arguments.get("page", 0),
                    include_last_message=arguments.get("include_last_message", True),
                    sort_by=arguments.get("sort_by", "last_active")
                )
                result = [_to_dict(c) for c in result]
            elif tool_name == "get_chat":
                result = whatsapp_get_chat(
                    arguments.get("chat_jid"),
                    arguments.get("include_last_message", True)
                )
                if result is None:
                    result = {}
                else:
                    result = _to_dict(result)
            elif tool_name == "get_direct_chat_by_contact":
                result = whatsapp_get_direct_chat_by_contact(
                    arguments.get("sender_phone_number")
                )
                if result is None:
                    result = {}
                else:
                    result = _to_dict(result)
            elif tool_name == "get_contact_chats":
                result = whatsapp_get_contact_chats(
                    arguments.get("jid"),
                    arguments.get("limit", 20),
                    arguments.get("page", 0)
                )
                result = [_to_dict(c) for c in result]
            elif tool_name == "get_last_interaction":
                result = whatsapp_get_last_interaction(arguments.get("jid"))
                if result is None:
                    result = ""
                elif isinstance(result, str):
                    result = result
                elif hasattr(result, '__dataclass_fields__'):
                    result = json.dumps(asdict(result), default=str)
                else:
                    result = str(result)
            elif tool_name == "get_message_context":
                result = whatsapp_get_message_context(
                    arguments.get("message_id"),
                    arguments.get("before", 5),
                    arguments.get("after", 5)
                )
                if result is None:
                    result = {}
                elif hasattr(result, 'message'):
                    result = {
                        "message": _to_dict(result.message),
                        "before": [_to_dict(m) for m in result.before],
                        "after": [_to_dict(m) for m in result.after]
                    }
                else:
                    result = _to_dict(result)
            elif tool_name == "send_message":
                if not arguments.get("recipient"):
                    result = {
                        "success": False,
                        "message": "Recipient must be provided"
                    }
                else:
                    success, status_message = whatsapp_send_message(
                        arguments.get("recipient"),
                        arguments.get("message", "")
                    )
                    result = {
                        "success": success,
                        "message": status_message
                    }
            elif tool_name == "send_file":
                success, status_message = whatsapp_send_file(
                    arguments.get("recipient"),
                    arguments.get("media_path")
                )
                result = {
                    "success": success,
                    "message": status_message
                }
            elif tool_name == "send_audio_message":
                success, status_message = whatsapp_audio_voice_message(
                    arguments.get("recipient"),
                    arguments.get("media_path")
                )
                result = {
                    "success": success,
                    "message": status_message
                }
            elif tool_name == "download_media":
                file_path = whatsapp_download_media(
                    arguments.get("message_id"),
                    arguments.get("chat_jid")
                )
                if file_path:
                    result = {
                        "success": True,
                        "message": "Media downloaded successfully",
                        "file_path": file_path
                    }
                else:
                    result = {
                        "success": False,
                        "message": "Failed to download media"
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, default=str)
                        }
                    ]
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """Run the MCP server."""
        while True:
            try:
                line = await asyncio.to_thread(sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                method = request.get("method")
                
                if method == "initialize":
                    response = await self.handle_initialize(request)
                elif method == "initialized":
                    continue
                elif method == "tools/list":
                    response = await self.handle_list_tools(request)
                elif method == "tools/call":
                    response = await self.handle_call_tool(request)
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown method: {method}"
                        }
                    }
                
                self._send_response(response)
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                self._send_error(request.get("id"), -32603, f"Server error: {e}")
                break


async def main():
    """Main entry point."""
    server = WhatsAppMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

