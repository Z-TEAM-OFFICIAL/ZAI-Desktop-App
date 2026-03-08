# Z-AI DESKTOP APP

THIS IS FREE TO USE AND HAS MCP SERVER COMPATABILITY

## Z-AI Desktop Application

A modern AI chat desktop application using OpenRouter API with Nemotron Nano A3B 30B (Free) model and MCP server support.

### Features

- 🤖 **Nemotron Nano A3B 30B** - Free model via OpenRouter
- 🖥️ **Desktop GUI** - Modern dark-themed interface
- 🔌 **MCP Support** - Model Context Protocol server compatibility
- 💾 **Environment-based** - API key via .env file
- 🎨 **Modern UI** - Clean dark design with CustomTkinter

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Edit `.env` and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get a free API key at: https://openrouter.ai/settings/keys

### 3. Run the App

```bash
python main.py
```

## Configuration

### .env File

Copy `.env.example` to `.env` and add your API key:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### MCP Servers (mcp.json)

Edit `mcp.json` to configure MCP servers. The app includes basic MCP server configurations:

- **filesystem** - File system access
- **brave-search** - Web search (requires API key)

## Project Structure

```
ZAI-Desktop-App/
├── main.py          # Main application
├── requirements.txt # Python dependencies
├── .env            # API key (create from .env.example)
├── .env.example    # Environment template
├── mcp.json        # MCP server configuration
└── index.html      # Web version (optional)
```

## Usage

1. Launch the app with `python main.py`
2. Enter your OpenRouter API key in settings (⚙ button)
3. Start chatting with the AI!

## MCP Server Setup

For full MCP functionality, install Node.js and run:

```bash
# Install MCP servers globally
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-brave-search
```