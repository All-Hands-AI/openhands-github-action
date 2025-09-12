import json
import os
import sys
from pathlib import Path

import requests


def read_prompt(value):
    """Read prompt from file if it's a file path, otherwise return as-is."""
    p = Path(value)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return value  # treat as raw prompt text


def api_session(api_key, base_url):
    """Create a requests session with API authentication."""
    s = requests.Session()
    s.headers.update(
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    )
    return s, base_url.rstrip("/")


def create_conversation(session, base_url, initial_user_msg, repository, selected_branch):
    """Create a new conversation via the OpenHands API."""
    body = {"initial_user_msg": initial_user_msg}
    if repository:
        body["repository"] = repository
    if selected_branch:
        body["selected_branch"] = selected_branch
    r = session.post(f"{base_url}/api/conversations", json=body)
    r.raise_for_status()
    return r.json()


def get_conversation_url(base_url, conversation_id):
    """Construct the conversation URL for the web interface."""
    return f"{base_url}/conversations/{conversation_id}"


def write_outputs(conversation_id, status, conversation_url):
    """Write outputs to GitHub Actions output file."""
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"conversation-id={conversation_id}\n")
            f.write(f"status={status}\n")
            f.write(f"conversation-url={conversation_url}\n")


def main():
    # Get required inputs
    api_key = os.getenv("OPENHANDS_API_KEY")
    if not api_key:
        print("OPENHANDS_API_KEY is required", file=sys.stderr)
        sys.exit(2)

    prompt_input = os.getenv("INPUT_PROMPT", "").strip()
    if not prompt_input:
        print("inputs.prompt is required", file=sys.stderr)
        sys.exit(2)

    # Get optional inputs
    initial_user_msg = read_prompt(prompt_input)
    repository = os.getenv("INPUT_REPOSITORY", "").strip() or os.getenv("GITHUB_REPOSITORY", "")
    selected_branch = os.getenv("INPUT_SELECTED_BRANCH", "").strip()
    base_url = os.getenv("INPUT_BASE_URL", "https://app.all-hands.dev").strip()

    # Create API session
    session, base_url = api_session(api_key, base_url)

    # Create conversation
    try:
        created = create_conversation(session, base_url, initial_user_msg, repository, selected_branch)
    except requests.HTTPError as e:
        print(f"Create conversation failed: {e} - {getattr(e.response, 'text', '')}", file=sys.stderr)
        sys.exit(1)

    # Extract conversation details
    conversation_id = created.get("conversation_id") or created.get("id") or ""
    status = str(created.get("status", "")).upper()

    if not conversation_id:
        print(f"Unexpected response: {json.dumps(created, indent=2)}", file=sys.stderr)
        sys.exit(1)

    conversation_url = get_conversation_url(base_url, conversation_id)
    
    # Output results
    print(f"Conversation created: {conversation_id} (status={status})")
    print("=" * 60)
    print(f"🔗 View conversation: {conversation_url}")
    print("=" * 60)
    print(f"💡 You can comment this URL in a PR for easy access:")
    print(f"   {conversation_url}")
    print("=" * 60)

    # Write GitHub Actions outputs
    write_outputs(conversation_id, status or "UNKNOWN", conversation_url)


if __name__ == "__main__":
    main()