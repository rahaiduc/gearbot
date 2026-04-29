# GearBot

**A lightweight, Grok-powered web agent that lives in your terminal.**

GearBot lets you control a real browser using natural language. You talk to Grok, and it navigates, clicks, fills forms, extracts information all while showing you exactly what's happening in real time.

Built for developers who want a fast, controllable, and transparent web agent without the complexity of heavy frameworks.

## Demo

### Web Registration

<video src="https://github.com/user-attachments/assets/54957651-f65e-4262-9614-f68a53ff9fec" controls width="100%"></video>


## Features

- Full browser automation with **Playwright**
- Powered by **Grok** (xAI) — currently using `grok-4-1-fast`
- Real-time state visualization (current URL, title, last action)
- Beautiful terminal UI with [Rich](https://github.com/Textualize/rich)
- Supports both visible and headless browser modes
- Smart tool calling with proper state management

## Tech Stack
- LLM: Grok (xAI) — grok-4-1-fast
- Agent Framework: LangGraph + LangChain
- Browser Automation: Playwright (async)
- UI: Rich
- Python: 3.12+

## Quick Start

```bash
# Clone the repo
git clone https://github.com/rahaiduc/gearbot.git
cd gearbot

# Install with uv (recommended)
uv sync

# Copy environment template
cp .env.example .env
```
**Then edit .env:**
- GROK_API_KEY=your_xai_api_key_here
- GROK_MODEL=grok-4-1-fast
- BROWSER_HEADLESS=false

```bash
uv run gearbot
# Use web tools
navigate to google
go to https://www.demoblaze.com
search facebook
extract the body of the page
click the login button
# Exit
Type exit, quit or press Ctrl+C to stop.
```

## Project Structure

```bash
gearbot/
├── src/
│   └── gearbot/
│       ├── __main__.py
│       ├── graph.py                 
│       ├── core/
│       │   ├── browser.py           
│       │   ├── nodes.py
│       │   └── state.py             
│       ├── tools/
│       │   └── web.py
│       └── config/  
│           └── config.py
├── .env.example
└── pyproject.toml
```
## Contributing
Feel free to open issues or PRs. This is a personal/project tool that I'm actively using and improving.
## License
MIT
