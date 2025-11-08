# WhatsApp MCP Server - AI Agent Installation Guide

This guide provides comprehensive installation instructions for AI agents installing the WhatsApp MCP server in OI OS (Brain Trust 4) environments, as well as end-user setup instructions.

## Table of Contents

1. [AI Agent Quick Installation](#ai-agent-quick-installation)
2. [Prerequisites](#prerequisites)
3. [Full Installation Steps](#full-installation-steps)
4. [Building the Go Bridge](#building-the-go-bridge)
5. [Setting Up the Python MCP Server](#setting-up-the-python-mcp-server)
6. [Connecting to OI OS](#connecting-to-oi-os)
7. [Configuring Parameter Extractors](#configuring-parameter-extractors)
8. [Creating Parameter Rules](#creating-parameter-rules)
9. [Creating Intent Mappings](#creating-intent-mappings)
10. [End User Setup](#end-user-setup)
11. [Verification & Testing](#verification--testing)
12. [Troubleshooting](#troubleshooting)
13. [Known Issues & Fixes](#known-issues--fixes)

---

## AI Agent Quick Installation

For AI agents using OI OS, execute the following commands:

```bash
# 1. Install the server
./oi install https://github.com/lharries/whatsapp-mcp.git

# 2. Build the Go bridge
cd MCP-servers/whatsapp-mcp/whatsapp-bridge
go mod download
go build -o whatsapp-bridge main.go

# 3. Connect the server (using custom implementation for OI OS compatibility)
cd ../../
./brain-trust4 connect whatsapp-mcp /Library/Frameworks/Python.framework/Versions/3.13/bin/uv -- --directory "$(pwd)/MCP-servers/whatsapp-mcp/whatsapp-mcp-server" run main_custom.py

# 4. Run the bridge in the background (first-time QR code authentication required)
cd MCP-servers/whatsapp-mcp/whatsapp-bridge
./whatsapp-bridge &

# 5. Create intent mappings and parameter rules (single optimized transaction)
sqlite3 brain-trust4.db << 'SQL'
BEGIN TRANSACTION;

-- Intent mappings (all 12 tools)
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('whatsapp search contacts', 'whatsapp-mcp', 'search_contacts', 10),
('whatsapp list messages', 'whatsapp-mcp', 'list_messages', 10),
('whatsapp list chats', 'whatsapp-mcp', 'list_chats', 10),
('whatsapp get chat', 'whatsapp-mcp', 'get_chat', 10),
('whatsapp get direct chat', 'whatsapp-mcp', 'get_direct_chat_by_contact', 10),
('whatsapp get contact chats', 'whatsapp-mcp', 'get_contact_chats', 10),
('whatsapp get last interaction', 'whatsapp-mcp', 'get_last_interaction', 10),
('whatsapp get message context', 'whatsapp-mcp', 'get_message_context', 10),
('whatsapp send message', 'whatsapp-mcp', 'send_message', 10),
('whatsapp send file', 'whatsapp-mcp', 'send_file', 10),
('whatsapp send audio', 'whatsapp-mcp', 'send_audio_message', 10),
('whatsapp download media', 'whatsapp-mcp', 'download_media', 10);

-- Parameter rules (all 12 tools)
-- search_contacts: query is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'search_contacts', 'whatsapp-mcp::search_contacts', '["query"]',
'{"query": {"FromQuery": "whatsapp-mcp::search_contacts.query"}}', '[]');

-- list_messages: no required fields (all optional)
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'list_messages', 'whatsapp-mcp::list_messages', '[]',
'{"chat_jid": {"FromQuery": "whatsapp-mcp::list_messages.chat_jid"}, "sender_phone_number": {"FromQuery": "whatsapp-mcp::list_messages.sender_phone_number"}, "query": {"FromQuery": "whatsapp-mcp::list_messages.query"}, "after": {"FromQuery": "whatsapp-mcp::list_messages.after"}, "before": {"FromQuery": "whatsapp-mcp::list_messages.before"}, "limit": {"FromQuery": "limit"}, "page": {"FromQuery": "page"}, "include_context": {"FromQuery": "include_context"}, "context_before": {"FromQuery": "context_before"}, "context_after": {"FromQuery": "context_after"}}', '[]');

-- list_chats: no required fields (all optional)
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'list_chats', 'whatsapp-mcp::list_chats', '[]',
'{"query": {"FromQuery": "whatsapp-mcp::list_chats.query"}, "limit": {"FromQuery": "limit"}, "page": {"FromQuery": "page"}, "include_last_message": {"FromQuery": "include_last_message"}, "sort_by": {"FromQuery": "sort_by"}}', '[]');

-- get_chat: chat_jid is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_chat', 'whatsapp-mcp::get_chat', '["chat_jid"]',
'{"chat_jid": {"FromQuery": "whatsapp-mcp::get_chat.chat_jid"}, "include_last_message": {"FromQuery": "include_last_message"}}', '[]');

-- get_direct_chat_by_contact: sender_phone_number is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_direct_chat_by_contact', 'whatsapp-mcp::get_direct_chat_by_contact', '["sender_phone_number"]',
'{"sender_phone_number": {"FromQuery": "whatsapp-mcp::get_direct_chat_by_contact.sender_phone_number"}}', '[]');

-- get_contact_chats: jid is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_contact_chats', 'whatsapp-mcp::get_contact_chats', '["jid"]',
'{"jid": {"FromQuery": "whatsapp-mcp::get_contact_chats.jid"}, "limit": {"FromQuery": "limit"}, "page": {"FromQuery": "page"}}', '[]');

-- get_last_interaction: jid is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_last_interaction', 'whatsapp-mcp::get_last_interaction', '["jid"]',
'{"jid": {"FromQuery": "whatsapp-mcp::get_last_interaction.jid"}}', '[]');

-- get_message_context: message_id is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_message_context', 'whatsapp-mcp::get_message_context', '["message_id"]',
'{"message_id": {"FromQuery": "whatsapp-mcp::get_message_context.message_id"}, "before": {"FromQuery": "context_before"}, "after": {"FromQuery": "context_after"}}', '[]');

-- send_message: recipient and message are REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'send_message', 'whatsapp-mcp::send_message', '["recipient", "message"]',
'{"recipient": {"FromQuery": "whatsapp-mcp::send_message.recipient"}, "message": {"FromQuery": "whatsapp-mcp::send_message.message"}}', '[]');

-- send_file: recipient and media_path are REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'send_file', 'whatsapp-mcp::send_file', '["recipient", "media_path"]',
'{"recipient": {"FromQuery": "whatsapp-mcp::send_file.recipient"}, "media_path": {"FromQuery": "whatsapp-mcp::send_file.media_path"}}', '[]');

-- send_audio_message: recipient and media_path are REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'send_audio_message', 'whatsapp-mcp::send_audio_message', '["recipient", "media_path"]',
'{"recipient": {"FromQuery": "whatsapp-mcp::send_audio_message.recipient"}, "media_path": {"FromQuery": "whatsapp-mcp::send_audio_message.media_path"}}', '[]');

-- download_media: message_id and chat_jid are REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'download_media', 'whatsapp-mcp::download_media', '["message_id", "chat_jid"]',
'{"message_id": {"FromQuery": "whatsapp-mcp::download_media.message_id"}, "chat_jid": {"FromQuery": "whatsapp-mcp::download_media.chat_jid"}}', '[]');

COMMIT;
SQL

# NOTE: Parameter extraction is fragile - direct calls are more reliable
```

**Important Notes:**
- **Bridge must be running**: The WhatsApp bridge must be running in the background for the MCP server to access WhatsApp data
- **First-time authentication**: You'll need to scan a QR code with your WhatsApp mobile app on first run
- **Parameter extraction is fragile**: Natural language queries with intent mapping may fail parameter extraction - direct calls are recommended
- **Direct calls work reliably**: Use `./brain-trust4 call whatsapp-mcp tool-name '{"param": "value"}'` for reliable execution

---

## Prerequisites

### Required Software

- **Go** (1.24+ recommended)
- **Python** (3.6+)
- **UV** (Python package manager) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **OI OS / Brain Trust 4** installed and running
- **WhatsApp mobile app** for QR code authentication

### Optional Software

- **FFmpeg** - Required for audio message conversion. Install via your system package manager:
  - macOS: `brew install ffmpeg`
  - Linux: `apt-get install ffmpeg` or `yum install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

**Note:** Without FFmpeg, you can still send raw audio files using `send_file`, but they won't appear as playable WhatsApp voice messages.

---

## Full Installation Steps

### Step 1: Clone the Repository

```bash
./oi install https://github.com/lharries/whatsapp-mcp.git
```

This will clone the repository to `MCP-servers/whatsapp-mcp/` in your OI OS project directory.

**Alternative (manual):**
```bash
git clone https://github.com/lharries/whatsapp-mcp.git MCP-servers/whatsapp-mcp
cd MCP-servers/whatsapp-mcp
```

---

## Building the Go Bridge

The Go bridge connects to WhatsApp's web API and stores messages in a local SQLite database.

### Step 1: Navigate to Bridge Directory

```bash
cd MCP-servers/whatsapp-mcp/whatsapp-bridge
```

### Step 2: Install Go Dependencies

```bash
go mod download
```

### Step 3: Build the Bridge

```bash
go build -o whatsapp-bridge main.go
```

This creates the `whatsapp-bridge` executable.

### Step 4: First-Time Authentication

Run the bridge for the first time:

```bash
./whatsapp-bridge
```

You'll see a QR code in your terminal. **Scan it with your WhatsApp mobile app:**
1. Open WhatsApp on your phone
2. Go to Settings > Linked Devices
3. Tap "Link a Device"
4. Scan the QR code displayed in your terminal

After successful authentication, the bridge will:
- Store authentication tokens in `store/whatsapp.db`
- Begin syncing your message history
- Continue running to maintain connection

### Step 5: Run Bridge in Background

Once authenticated, you can run the bridge in the background:

```bash
# Option 1: Background process
./whatsapp-bridge &

# Option 2: Using nohup (survives terminal closure)
nohup ./whatsapp-bridge > bridge.log 2>&1 &

# Option 3: Using systemd (Linux) or launchd (macOS)
# See your system documentation for service setup
```

**Important:** The bridge must be running for the MCP server to access WhatsApp data.

---

## Setting Up the Python MCP Server

### Step 1: Navigate to Server Directory

```bash
cd MCP-servers/whatsapp-mcp/whatsapp-mcp-server
```

### Step 2: Install Python Dependencies

The server uses `uv` for dependency management:

```bash
# If using uv (recommended)
uv sync

# Alternative: If using pip
pip install -e .
```

### Step 3: Verify Installation

Test that the server can be imported:

```bash
python3 -c "from whatsapp import search_contacts; print('Import successful')"
```

**Note for OI OS:** This server uses `main_custom.py` instead of `main.py` because FastMCP's stdio implementation has timeout issues in OI OS. The custom implementation directly handles the MCP stdio protocol for better compatibility.

---

## Connecting to OI OS

### Step 1: Find UV Path

```bash
which uv
# Example output: /Library/Frameworks/Python.framework/Versions/3.13/bin/uv
```

### Step 2: Find Project Root Path

```bash
pwd
# Example output: /Users/chad/Desktop/_CLIENTS/OI/product/Release Test /OI-v1.0.4
```

### Step 3: Connect the Server

```bash
./brain-trust4 connect whatsapp-mcp /Library/Frameworks/Python.framework/Versions/3.13/bin/uv -- --directory "$(pwd)/MCP-servers/whatsapp-mcp/whatsapp-mcp-server" run main_custom.py
```

**Replace paths as needed:**
- `/Library/Frameworks/Python.framework/Versions/3.13/bin/uv` → Your `uv` path
- `$(pwd)/MCP-servers/whatsapp-mcp/whatsapp-mcp-server` → Your project-relative path (or use absolute path)

### Step 4: Verify Connection

```bash
./oi list
# Should show "whatsapp-mcp" in the server list

./oi status whatsapp-mcp
# Should show server status and capabilities
```

---

## Configuring Parameter Extractors

Parameter extractors allow OI OS to automatically extract tool parameters from natural language queries. Add these patterns to your `parameter_extractors.toml` file:

### Location

Add to: `parameter_extractors.toml` in your OI OS project root (or `~/.oi/parameter_extractors.toml`).

### WhatsApp Parameter Extractors

```toml
# ============================================================================
# WHATSAPP MCP SERVER EXTRACTION PATTERNS
# ============================================================================

# JID (Jabber ID) - WhatsApp chat/contact identifier
"chat_jid" = "regex:[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)"
"jid" = "regex:[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)"
"Extract chat JID from query" = "regex:[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)"

# Phone number - Extract phone numbers (with or without country code)
"sender_phone_number" = "regex:\\b\\d{10,15}\\b"
"recipient" = "conditional:if_contains:@(s\\.whatsapp\\.net|g\\.us)|then:regex:[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)|else:regex:\\b\\d{10,15}\\b"
"Extract recipient from query" = "conditional:if_contains:@(s\\.whatsapp\\.net|g\\.us)|then:regex:[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)|else:regex:\\b\\d{10,15}\\b"
"Extract phone number from query" = "regex:\\b\\d{10,15}\\b"

# WhatsApp send_message recipient - Prioritize JID extraction (more specific), then phone
"whatsapp-mcp::send_message.recipient" = "regex:[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)|\\b\\d{10,15}\\b"
"whatsapp-mcp::send_message.Extract recipient" = "regex:[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)|(?<=to\\s+|group\\s+|the\\s+group\\s+)[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)|\\b\\d{10,15}\\b"

# Message text/content
"message" = "keyword:after_message"
"Extract message text from query" = "remove:send,whatsapp,message,to"

# WhatsApp send_message message text - Extract everything after recipient (JID or phone)
"whatsapp-mcp::send_message.message" = "transform:regex:(?:[\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us)|\\d{10,15})\\s+(.+)$|trim"
"whatsapp-mcp::send_message.Extract message text" = "transform:regex:(?:[\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us)|\\d{10,15})\\s+(.+)$|trim"

# WhatsApp search_contacts - Extract search query
"whatsapp-mcp::search_contacts.query" = "remove:search,find,whatsapp,contacts,contact"
"whatsapp-mcp::search_contacts.Extract query" = "remove:search,find,whatsapp,contacts,contact"

# WhatsApp list_messages - Extract parameters (all optional, but provide extractors)
"whatsapp-mcp::list_messages.chat_jid" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"
"whatsapp-mcp::list_messages.sender_phone_number" = "regex:\\b\\d{10,15}\\b"
"whatsapp-mcp::list_messages.query" = "remove:list,show,get,whatsapp,messages,message"
"whatsapp-mcp::list_messages.after" = "regex:(?:after|since|from)(?:\\s+)?(\\d{4}-\\d{2}-\\d{2}(?:T\\d{2}:\\d{2}:\\d{2})?)"
"whatsapp-mcp::list_messages.before" = "regex:(?:before|until|to)(?:\\s+)?(\\d{4}-\\d{2}-\\d{2}(?:T\\d{2}:\\d{2}:\\d{2})?)"

# WhatsApp list_chats - Extract parameters (all optional)
"whatsapp-mcp::list_chats.query" = "remove:list,show,get,whatsapp,chats,chat"

# WhatsApp get_chat - Extract chat_jid (required)
"whatsapp-mcp::get_chat.chat_jid" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"
"whatsapp-mcp::get_chat.Extract chat JID" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"

# WhatsApp get_direct_chat_by_contact - Extract sender_phone_number (required)
"whatsapp-mcp::get_direct_chat_by_contact.sender_phone_number" = "regex:\\b\\d{10,15}\\b"
"whatsapp-mcp::get_direct_chat_by_contact.Extract phone number" = "regex:\\b\\d{10,15}\\b"

# WhatsApp get_contact_chats - Extract jid (required)
"whatsapp-mcp::get_contact_chats.jid" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"
"whatsapp-mcp::get_contact_chats.Extract JID" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"

# WhatsApp get_last_interaction - Extract jid (required)
"whatsapp-mcp::get_last_interaction.jid" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"
"whatsapp-mcp::get_last_interaction.Extract JID" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"

# WhatsApp get_message_context - Extract message_id (required)
"whatsapp-mcp::get_message_context.message_id" = "regex:\\b([A-Za-z0-9]{20,})\\b"
"whatsapp-mcp::get_message_context.Extract message ID" = "regex:\\b([A-Za-z0-9]{20,})\\b"

# WhatsApp send_file - Extract recipient and media_path (both required)
"whatsapp-mcp::send_file.recipient" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us)|\\b\\d{10,15}\\b)"
"whatsapp-mcp::send_file.media_path" = "keyword:after_file"
"whatsapp-mcp::send_file.Extract recipient" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us)|\\b\\d{10,15}\\b)"
"whatsapp-mcp::send_file.Extract file path" = "keyword:after_file"

# WhatsApp send_audio_message - Extract recipient and media_path (both required)
"whatsapp-mcp::send_audio_message.recipient" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us)|\\b\\d{10,15}\\b)"
"whatsapp-mcp::send_audio_message.media_path" = "keyword:after_file"
"whatsapp-mcp::send_audio_message.Extract recipient" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us)|\\b\\d{10,15}\\b)"
"whatsapp-mcp::send_audio_message.Extract audio file path" = "keyword:after_file"

# WhatsApp download_media - Extract message_id and chat_jid (both required)
"whatsapp-mcp::download_media.message_id" = "regex:\\b([A-Za-z0-9]{20,})\\b"
"whatsapp-mcp::download_media.chat_jid" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"
"whatsapp-mcp::download_media.Extract message ID" = "regex:\\b([A-Za-z0-9]{20,})\\b"
"whatsapp-mcp::download_media.Extract chat JID" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us))"

# Search/query terms
"query" = "remove:search,find,show,list,get,whatsapp"
"Extract search query from query" = "remove:search,find,show,list,get,whatsapp"

# Date fields (ISO-8601 format) - for list_messages tool
"after_date" = "regex:\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2})?"
"before_date" = "regex:\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2})?"
"Extract date from query" = "regex:\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2})?"

# Numeric fields (limit, page, context counts)
"limit" = "conditional:if_matches:\\d+|then:regex:\\b\\d+\\b|else:default:20"
"page" = "conditional:if_matches:\\d+|then:regex:\\b\\d+\\b|else:default:0"
"context_before" = "conditional:if_matches:\\d+|then:regex:\\b\\d+\\b|else:default:5"
"context_after" = "conditional:if_matches:\\d+|then:regex:\\b\\d+\\b|else:default:5"

# Message ID
"message_id" = "regex:\\b[A-Za-z0-9]{20,}\\b"
"Extract message ID from query" = "regex:\\b[A-Za-z0-9]{20,}\\b"

# File path
"media_path" = "keyword:after_file"
"Extract file path from query" = "keyword:after_file"

# Boolean fields
"include_context" = "default:true"
"include_last_message" = "default:true"

# Sort field (enum: "last_active" or "name")
"sort_by" = "conditional:if_contains:name|then:default:name|else:default:last_active"
```

### Adding to parameter_extractors.toml

You can either:
1. **Manual Edit**: Open `parameter_extractors.toml` and add the patterns above
2. **Append Script** (for AI agents):
   ```bash
   cat >> parameter_extractors.toml << 'WHATSAPP_EXTRACTORS'
   # WhatsApp patterns (paste patterns above)
   WHATSAPP_EXTRACTORS
   ```

---

## Creating Parameter Rules

**⚠️ CRITICAL: Parameter rules must be created in the database for parameter extraction to work.**

Parameter rules define which fields are required and how to extract them from natural language queries. The OI OS parameter engine **only extracts required fields** - optional fields are skipped even if extractors exist in `parameter_extractors.toml`.

### Why Parameter Rules Are Needed

- **Required fields are extracted**: The parameter engine processes required fields and invokes their extractors
- **Optional fields are skipped**: Optional fields are ignored during parameter extraction, even if extractors exist
- **Database-driven**: Parameter rules are stored in the `parameter_rules` table in `brain-trust4.db`

### Creating Parameter Rules

Run this optimized SQL transaction to create all parameter rules in a single operation:

```sql
BEGIN TRANSACTION;
-- search_contacts: query is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'search_contacts', 'whatsapp-mcp::search_contacts', '["query"]',
'{"query": {"FromQuery": "whatsapp-mcp::search_contacts.query"}}', '[]');

-- list_messages: no required fields (all optional)
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'list_messages', 'whatsapp-mcp::list_messages', '[]',
'{"chat_jid": {"FromQuery": "whatsapp-mcp::list_messages.chat_jid"}, "sender_phone_number": {"FromQuery": "whatsapp-mcp::list_messages.sender_phone_number"}, "query": {"FromQuery": "whatsapp-mcp::list_messages.query"}, "after": {"FromQuery": "whatsapp-mcp::list_messages.after"}, "before": {"FromQuery": "whatsapp-mcp::list_messages.before"}, "limit": {"FromQuery": "limit"}, "page": {"FromQuery": "page"}, "include_context": {"FromQuery": "include_context"}, "context_before": {"FromQuery": "context_before"}, "context_after": {"FromQuery": "context_after"}}', '[]');

-- list_chats: no required fields (all optional)
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'list_chats', 'whatsapp-mcp::list_chats', '[]',
'{"query": {"FromQuery": "whatsapp-mcp::list_chats.query"}, "limit": {"FromQuery": "limit"}, "page": {"FromQuery": "page"}, "include_last_message": {"FromQuery": "include_last_message"}, "sort_by": {"FromQuery": "sort_by"}}', '[]');

-- get_chat: chat_jid is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_chat', 'whatsapp-mcp::get_chat', '["chat_jid"]',
'{"chat_jid": {"FromQuery": "whatsapp-mcp::get_chat.chat_jid"}, "include_last_message": {"FromQuery": "include_last_message"}}', '[]');

-- get_direct_chat_by_contact: sender_phone_number is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_direct_chat_by_contact', 'whatsapp-mcp::get_direct_chat_by_contact', '["sender_phone_number"]',
'{"sender_phone_number": {"FromQuery": "whatsapp-mcp::get_direct_chat_by_contact.sender_phone_number"}}', '[]');

-- get_contact_chats: jid is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_contact_chats', 'whatsapp-mcp::get_contact_chats', '["jid"]',
'{"jid": {"FromQuery": "whatsapp-mcp::get_contact_chats.jid"}, "limit": {"FromQuery": "limit"}, "page": {"FromQuery": "page"}}', '[]');

-- get_last_interaction: jid is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_last_interaction', 'whatsapp-mcp::get_last_interaction', '["jid"]',
'{"jid": {"FromQuery": "whatsapp-mcp::get_last_interaction.jid"}}', '[]');

-- get_message_context: message_id is REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'get_message_context', 'whatsapp-mcp::get_message_context', '["message_id"]',
'{"message_id": {"FromQuery": "whatsapp-mcp::get_message_context.message_id"}, "before": {"FromQuery": "context_before"}, "after": {"FromQuery": "context_after"}}', '[]');

-- send_message: recipient and message are REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'send_message', 'whatsapp-mcp::send_message', '["recipient", "message"]',
'{"recipient": {"FromQuery": "whatsapp-mcp::send_message.recipient"}, "message": {"FromQuery": "whatsapp-mcp::send_message.message"}}', '[]');

-- send_file: recipient and media_path are REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'send_file', 'whatsapp-mcp::send_file', '["recipient", "media_path"]',
'{"recipient": {"FromQuery": "whatsapp-mcp::send_file.recipient"}, "media_path": {"FromQuery": "whatsapp-mcp::send_file.media_path"}}', '[]');

-- send_audio_message: recipient and media_path are REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'send_audio_message', 'whatsapp-mcp::send_audio_message', '["recipient", "media_path"]',
'{"recipient": {"FromQuery": "whatsapp-mcp::send_audio_message.recipient"}, "media_path": {"FromQuery": "whatsapp-mcp::send_audio_message.media_path"}}', '[]');

-- download_media: message_id and chat_jid are REQUIRED
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('whatsapp-mcp', 'download_media', 'whatsapp-mcp::download_media', '["message_id", "chat_jid"]',
'{"message_id": {"FromQuery": "whatsapp-mcp::download_media.message_id"}, "chat_jid": {"FromQuery": "whatsapp-mcp::download_media.chat_jid"}}', '[]');

COMMIT;
```

### Critical Fix: Making Required Fields Actually Required

**Problem**: If a field is marked as optional in the parameter rule, the parameter engine will skip it entirely, even if:
- An extractor pattern exists in `parameter_extractors.toml`
- The extractor pattern is correctly configured
- The query contains the parameter value

**Solution**: Make all fields that need to be extracted from natural language queries required in the parameter rule, even if they're technically optional in the tool's API signature.

**Example for send_message:**
```sql
-- WRONG: message is optional, so it won't be extracted
required_fields: '["recipient"]'

-- CORRECT: message is required, so it will be extracted
required_fields: '["recipient", "message"]'
```

**Why This Works**: The OI OS parameter engine only processes fields listed in `required_fields`. Optional fields are completely skipped during parameter extraction, regardless of whether extractors exist.

### Verifying Parameter Rules

```bash
# List all WhatsApp parameter rules
sqlite3 brain-trust4.db "SELECT tool_signature, required_fields FROM parameter_rules WHERE server_name = 'whatsapp-mcp';"

# Check specific tool rule
sqlite3 brain-trust4.db "SELECT * FROM parameter_rules WHERE tool_signature = 'whatsapp-mcp::send_message';"
```

### Updating Parameter Rules

To update a parameter rule (e.g., to make a field required):

```bash
sqlite3 brain-trust4.db << 'SQL'
-- Make message required for send_message
UPDATE parameter_rules 
SET required_fields = '["recipient", "message"]' 
WHERE tool_signature = 'whatsapp-mcp::send_message';
SQL
```

### Testing Parameter Extraction

After creating parameter rules, test with debug output:

```bash
# Test with debug output
DEBUG=1 ./oi brain "whatsapp send message to 15862013686 Hello from OI!" --test-params 2>&1 | grep -A 15 "Parameter Generation"
```

You should see both `recipient` and `message` in the generated parameters if the rule is correct.

---

## Creating Intent Mappings

Intent mappings connect natural language queries to specific WhatsApp MCP tools. Create them using SQL INSERT statements.

### Database Location

```bash
sqlite3 brain-trust4.db
```

### Intent Mappings Schema

```sql
CREATE TABLE intent_mappings (
    keyword TEXT PRIMARY KEY,
    server_name TEXT NOT NULL,
    tool_name TEXT,
    priority INTEGER DEFAULT 1
);
```

### All WhatsApp Intent Mappings

Run this optimized single SQL statement to create all intent mappings:

```sql
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('whatsapp search contacts', 'whatsapp-mcp', 'search_contacts', 10),
('whatsapp list messages', 'whatsapp-mcp', 'list_messages', 10),
('whatsapp list chats', 'whatsapp-mcp', 'list_chats', 10),
('whatsapp get chat', 'whatsapp-mcp', 'get_chat', 10),
('whatsapp get direct chat', 'whatsapp-mcp', 'get_direct_chat_by_contact', 10),
('whatsapp get contact chats', 'whatsapp-mcp', 'get_contact_chats', 10),
('whatsapp get last interaction', 'whatsapp-mcp', 'get_last_interaction', 10),
('whatsapp get message context', 'whatsapp-mcp', 'get_message_context', 10),
('whatsapp send message', 'whatsapp-mcp', 'send_message', 10),
('whatsapp send file', 'whatsapp-mcp', 'send_file', 10),
('whatsapp send audio', 'whatsapp-mcp', 'send_audio_message', 10),
('whatsapp download media', 'whatsapp-mcp', 'download_media', 10);
```

### Verifying Intent Mappings

```bash
# List all WhatsApp intent mappings
sqlite3 brain-trust4.db "SELECT * FROM intent_mappings WHERE server_name = 'whatsapp-mcp' ORDER BY priority DESC;"

# Or use OI command
./oi intent list | grep whatsapp
```

### Removing Intent Mappings

```sql
-- Remove a specific mapping
DELETE FROM intent_mappings WHERE keyword = 'whatsapp search contacts';

-- Remove all WhatsApp mappings
DELETE FROM intent_mappings WHERE server_name = 'whatsapp-mcp';
```

---

## End User Setup

### Quick Start for End Users

1. **Install Prerequisites**
   ```bash
   # Install Go (if not installed)
   brew install go  # macOS
   # or visit: https://go.dev/dl/
   
   # Install UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/lharries/whatsapp-mcp.git
   cd whatsapp-mcp
   ```

3. **Build Go Bridge**
   ```bash
   cd whatsapp-bridge
   go mod download
   go build -o whatsapp-bridge main.go
   ```

4. **Authenticate with WhatsApp**
   ```bash
   ./whatsapp-bridge
   # Scan QR code with WhatsApp mobile app
   # Keep bridge running or start in background: ./whatsapp-bridge &
   ```

5. **Install Python Dependencies**
   ```bash
   cd ../whatsapp-mcp-server
   uv sync
   ```

6. **Configure Claude Desktop / Cursor**

   **For Claude Desktop:**
   - Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`
   ```json
   {
     "mcpServers": {
       "whatsapp": {
         "command": "/path/to/uv",
         "args": [
           "--directory",
           "/full/path/to/whatsapp-mcp/whatsapp-mcp-server",
           "run",
           "main.py"
         ]
       }
     }
   }
   ```

   **For Cursor:**
   - Edit: `~/.cursor/mcp.json`
   ```json
   {
     "mcpServers": {
       "whatsapp": {
         "command": "/path/to/uv",
         "args": [
           "--directory",
           "/full/path/to/whatsapp-mcp/whatsapp-mcp-server",
           "run",
           "main.py"
         ]
       }
     }
   }
   ```

7. **Restart Claude Desktop / Cursor**

---

## Verification & Testing

### Test Server Connection

```bash
# List all servers
./oi list

# Check WhatsApp server status
./oi status whatsapp-mcp

# Test tool discovery
./brain-trust4 call whatsapp-mcp tools/list '{}'
```

### Test Intent Mappings

```bash
# Test contact search
./oi "whatsapp search contacts michael"

# Test listing chats
./oi "whatsapp list chats"

# Test sending a message (replace with real JID and message)
./oi "whatsapp send message to 120363326225382732@g.us Hello from OI OS"
```

### Test Parameter Extraction

```bash
# This should automatically extract recipient and message
./oi "whatsapp send message to 120363326225382732@g.us Live test from OI OS prompt. Hello World."
```

### Direct Tool Calls

```bash
# Direct tool call (bypasses intent mapping)
./brain-trust4 call whatsapp-mcp list_chats '{"limit": 5}'

# Send message directly
./brain-trust4 call whatsapp-mcp send_message '{"recipient": "120363326225382732@g.us", "message": "Test message"}'
```

---

## Troubleshooting

### Bridge Issues

**QR Code Not Displaying**
- Ensure terminal supports QR code display
- Try restarting the bridge: `pkill whatsapp-bridge && cd whatsapp-bridge && ./whatsapp-bridge`
- Check terminal encoding settings

**Bridge Crashes or Disconnects**
- Check logs: `tail -f bridge.log` (if using nohup)
- Verify Go version: `go version` (should be 1.24+)
- Rebuild bridge: `cd whatsapp-bridge && go clean && go build -o whatsapp-bridge main.go`

**WhatsApp Out of Sync**
```bash
# Reset authentication (deletes all local data)
cd whatsapp-bridge/store
rm -f whatsapp.db messages.db
cd ..
./whatsapp-bridge  # Will prompt for new QR code
```

### MCP Server Issues

**Server Timeout Errors**
- **Important for OI OS:** Use `main_custom.py` instead of `main.py` (FastMCP has stdio timeout issues)
- Verify connection command uses `main_custom.py`:
  ```bash
  ./brain-trust4 connect whatsapp-mcp /path/to/uv -- --directory "/path/to/whatsapp-mcp-server" run main_custom.py
  ```

**Module Import Errors**
```bash
cd whatsapp-mcp-server
uv sync  # Reinstall dependencies
# Or
pip install -e .  # If using pip
```

**Tool Discovery Fails**
- Verify bridge is running: `ps aux | grep whatsapp-bridge`
- Check server connection: `./oi status whatsapp-mcp`
- Test direct connection: `./brain-trust4 call whatsapp-mcp tools/list '{}'`

### Parameter Extraction Issues

**Recipient Not Extracted**
- Verify `whatsapp-mcp::send_message.recipient` pattern in `parameter_extractors.toml`
- Check pattern matches your query format (JID vs phone number)
- Test regex manually: `echo "120363326225382732@g.us" | grep -E '[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)'`

**Message Text Not Extracted**
- Verify `whatsapp-mcp::send_message.message` pattern in `parameter_extractors.toml`
- Ensure message comes after recipient in query
- Check for trailing whitespace issues (pattern includes `trim`)
- **Critical**: Verify `message` is marked as required in parameter rule:
  ```sql
  sqlite3 brain-trust4.db "SELECT required_fields FROM parameter_rules WHERE tool_signature = 'whatsapp-mcp::send_message';"
  ```
  Should show: `["recipient", "message"]` (not just `["recipient"]`)

### Intent Mapping Issues

**Intent Not Found**
```bash
# Verify mapping exists
sqlite3 brain-trust4.db "SELECT * FROM intent_mappings WHERE keyword LIKE '%whatsapp%';"

# Re-add mapping if missing
sqlite3 brain-trust4.db "INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES ('whatsapp list chats', 'whatsapp-mcp', 'list_chats', 10);"
```

**Wrong Tool Executed**
- Check priority: Higher priority mappings take precedence
- Verify keyword matches exactly: `SELECT keyword FROM intent_mappings WHERE server_name = 'whatsapp-mcp';`
- Remove conflicting mappings: `DELETE FROM intent_mappings WHERE keyword = 'conflicting_keyword';`

### Windows-Specific Issues

**CGO Not Enabled**
```bash
cd whatsapp-bridge
go env -w CGO_ENABLED=1
go build -o whatsapp-bridge main.go
```

**C Compiler Missing**
- Install MSYS2: https://www.msys2.org/
- Add `ucrt64\bin` to PATH
- See: https://code.visualstudio.com/docs/cpp/config-mingw

### Authentication Issues

**Device Limit Reached**
- Remove old devices: WhatsApp mobile app > Settings > Linked Devices
- Delete local auth: `rm whatsapp-bridge/store/whatsapp.db`
- Re-authenticate: `./whatsapp-bridge`

**Authentication Expired (after ~20 days)**
```bash
# Delete auth and re-authenticate
rm whatsapp-bridge/store/whatsapp.db
./whatsapp-bridge  # Scan new QR code
```

---

## Available Tools Reference

### Contact & Chat Discovery
- `search_contacts(query)` - Search contacts by name or phone
- `list_chats(query, limit, page, include_last_message, sort_by)` - List all chats
- `get_chat(chat_jid, include_last_message)` - Get specific chat info
- `get_direct_chat_by_contact(sender_phone_number)` - Find direct chat by phone
- `get_contact_chats(jid, limit, page)` - Get all chats for a contact

### Message Retrieval
- `list_messages(after, before, sender_phone_number, chat_jid, query, limit, page, include_context, context_before, context_after)` - List messages with filters
- `get_last_interaction(jid)` - Get most recent message with contact
- `get_message_context(message_id, before, after)` - Get context around a message

### Sending Messages
- `send_message(recipient, message)` - Send text message (recipient: JID or phone)
- `send_file(recipient, media_path)` - Send media file (image, video, document)
- `send_audio_message(recipient, media_path)` - Send audio as voice message (requires FFmpeg or .ogg file)

### Media Management
- `download_media(message_id, chat_jid)` - Download media from message and get file path

---

## Additional Resources

- **WhatsApp MCP Repository:** https://github.com/lharries/whatsapp-mcp
- **OI OS Documentation:** See `docs/` directory in your OI OS installation
- **MCP Protocol Specification:** https://modelcontextprotocol.io/
- **WhatsMeow Library:** https://github.com/tulir/whatsmeow

---

## Support

For issues specific to:
- **WhatsApp MCP Server:** Open an issue at https://github.com/lharries/whatsapp-mcp
- **OI OS Integration:** Check OI OS documentation or repository
- **General MCP Issues:** See MCP documentation at https://modelcontextprotocol.io/

---

**Last Updated:** 2025-11-08  
**Compatible With:** OI OS / Brain Trust 4, Claude Desktop, Cursor  
**Server Version:** 1.6.0

---

## Known Issues & Fixes

### Parameter Extraction Not Working

**Issue**: When using WhatsApp tools via natural language queries (e.g., `./oi "whatsapp send message to 15862013686 Hello!"`), required parameters are not extracted, resulting in errors like "Recipient must be provided" or "Message must be provided".

**Root Cause**: The OI OS parameter engine only extracts fields marked as **required** in the `parameter_rules` database table. If a field is marked as optional, it will be skipped entirely, even if:
- An extractor pattern exists in `parameter_extractors.toml`
- The extractor pattern is correctly configured
- The query contains the parameter value

**Fix**: Ensure all fields that need to be extracted from natural language queries are marked as required in the parameter rule:

```sql
sqlite3 brain-trust4.db << 'SQL'
-- Example: Make message required for send_message
UPDATE parameter_rules 
SET required_fields = '["recipient", "message"]' 
WHERE tool_signature = 'whatsapp-mcp::send_message';
SQL
```

**Verification**: After applying the fix, test with debug output:

```bash
DEBUG=1 ./oi brain "whatsapp send message to 15862013686 Hello from OI!" --test-params 2>&1 | grep -A 15 "Parameter Generation"
```

You should see both `recipient` and `message` in the generated parameters.

**Prevention**: When creating parameter rules, ensure all fields that need to be extracted from natural language queries are marked as required, even if they're technically optional in the tool's API signature. The parameter engine only processes required fields.

### Recipient Extraction Issues

**Issue**: Recipient is extracted as partial value (e.g., "s.whatsapp.net" instead of full JID "15862013686@s.whatsapp.net").

**Fix**: Ensure the extractor pattern uses capture groups to extract the full value:

```toml
# CORRECT: Uses capture group to extract full JID or phone
"whatsapp-mcp::send_message.recipient" = "regex:([\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us)|\\b\\d{10,15}\\b)"
```

**Verification**: Test the regex pattern manually:
```bash
echo "15862013686@s.whatsapp.net" | grep -oE '[\\w\\d]+@(s\\.whatsapp\\.net|g\\.us)|\\b\\d{10,15}\\b'
```

### Message Text Includes Recipient

**Issue**: When sending messages, the message text includes the recipient (e.g., `"message": "to 15862013686 Hello"` instead of just `"Hello"`).

**Fix**: Ensure the message extractor pattern captures only text after the recipient:

```toml
# CORRECT: Captures only text after recipient pattern
"whatsapp-mcp::send_message.message" = "transform:regex:(?:[\\w\\d]+@(?:s\\.whatsapp\\.net|g\\.us)|\\d{10,15}(?:@s\\.whatsapp\\.net)?)\\s+(.+)$|trim"
```

The pattern uses a non-capturing group for the recipient and a capture group for the message text.

