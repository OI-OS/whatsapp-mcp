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
8. [Creating Intent Mappings](#creating-intent-mappings)
9. [End User Setup](#end-user-setup)
10. [Verification & Testing](#verification--testing)
11. [Troubleshooting](#troubleshooting)

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
```

**Note:** The first time you run the bridge, you'll need to scan a QR code with your WhatsApp mobile app. After authentication, the bridge runs in the background.

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

Run these SQL INSERT statements to create intent mappings for all WhatsApp tools:

```sql
-- Contact search and discovery
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('whatsapp search contacts', 'whatsapp-mcp', 'search_contacts', 10);

-- Message retrieval
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('whatsapp list messages', 'whatsapp-mcp', 'list_messages', 10);

-- Chat management
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('whatsapp list chats', 'whatsapp-mcp', 'list_chats', 10),
('whatsapp get chat', 'whatsapp-mcp', 'get_chat', 10),
('whatsapp get direct chat', 'whatsapp-mcp', 'get_direct_chat_by_contact', 10),
('whatsapp get contact chats', 'whatsapp-mcp', 'get_contact_chats', 10);

-- Message context and history
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('whatsapp get last interaction', 'whatsapp-mcp', 'get_last_interaction', 10),
('whatsapp get message context', 'whatsapp-mcp', 'get_message_context', 10);

-- Sending messages
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('whatsapp send message', 'whatsapp-mcp', 'send_message', 10),
('whatsapp send file', 'whatsapp-mcp', 'send_file', 10),
('whatsapp send audio', 'whatsapp-mcp', 'send_audio_message', 10);

-- Media download
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('whatsapp download media', 'whatsapp-mcp', 'download_media', 10);
```

### Alternative: Single SQL Statement

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

**Last Updated:** 2025-11-03  
**Compatible With:** OI OS / Brain Trust 4, Claude Desktop, Cursor  
**Server Version:** 1.6.0

