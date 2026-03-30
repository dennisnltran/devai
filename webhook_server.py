#!/usr/bin/env python3
"""
Simple webhook server for GitHub Actions events.
Stores events in a JSON file that the MCP server can read.
"""

import json
from datetime import datetime, timezone 
from pathlib import Path
from aiohttp import web

# File to store events
GITHUB_EVENTS_FILE = Path(__file__).parent / "github_events.json"
GITHUB_ISSUES_EVENTS_FILE = Path(__file__).parent / "github_issues.json"
GITHUB_WORKFLOWS_EVENTS_FILE = Path(__file__).parent / "github_workflows.json"

EVENT_FILES = [GITHUB_EVENTS_FILE, GITHUB_ISSUES_EVENTS_FILE, GITHUB_WORKFLOWS_EVENTS_FILE]

EVENT_TYPES_MAPPING = {
    "issues": GITHUB_ISSUES_EVENTS_FILE,
    "workflow_run": GITHUB_WORKFLOWS_EVENTS_FILE
}

def clean(event_files):
    """
    Clean the specified file by deleting it if it exists.
    
    Args:
        event_files (list): A list of file paths to clean.
    """
    for fp in event_files:
        file_path = Path(fp)
        if file_path.is_file():
            file_path.unlink()  # 'unlink()' is the pathlib equivalent of 'os.remove()'
            print(f"File '{fp}' Cleaned!")

def store_gh_event(event, event_type):
    """
    Store GitHub events in a JSON file.

    Args:
        events (list): A list of GitHub event dictionaries to store.
        event_type (str): The type of the GitHub event (e.g., "issues", "workflow_run").
    """
    
    # Save all Github events
    # Load existing events
    gh_events = []
    if GITHUB_EVENTS_FILE.exists():
        with open(GITHUB_EVENTS_FILE, 'r') as f:
            gh_events = json.load(f)
    
    # Add new event and keep last 100
    gh_events.append(event)
    events = gh_events[-100:]
    
    # Save events
    with open(GITHUB_EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)

    # Save all events of the specific type (e.g. issues, workflow_run)
    if event_type in EVENT_TYPES_MAPPING:
        event_file = EVENT_TYPES_MAPPING[event_type]
        # Load existing events of this type
        type_events = []
        if event_file.exists():
            with open(event_file, 'r') as f:
                type_events = json.load(f)
        
        # Add new event and keep last 100
        type_events.append(event)
        type_events = type_events[-100:]
        
        # Save events of this type
        with open(event_file, 'w') as f:
            json.dump(type_events, f, indent=2)

async def handle_webhook(request):
    """Handle incoming GitHub webhook"""
    try:
        # Store event in the appropriate file based on event type
        data = await request.json()
        event_type = request.headers.get("X-GitHub-Event", "unknown")
        store_gh_event(data, event_type)
        
        return web.json_response({"status": "received"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

# Clean existing events file on startup
#clean(EVENT_FILES)

# Create app and add route
app = web.Application()
app.router.add_post('/webhook/github', handle_webhook)

if __name__ == '__main__':
    print("🚀 Starting webhook server on http://localhost:8080")
    print("🔗 Webhook URL: http://localhost:8080/webhook/github")
    web.run_app(app, host='localhost', port=8080)