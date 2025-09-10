import json
import os
import sys
import time
from pathlib import Path

import requests


def read_prompt(value):
    p = Path(value)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return value  # treat as raw prompt text


def api_session(api_key, base_url):
    s = requests.Session()
    s.headers.update(
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    )
    return s, base_url.rstrip("/")


def create_conversation(session, base_url, initial_user_msg, repository, selected_branch):
    body = {"initial_user_msg": initial_user_msg}
    if repository:
        body["repository"] = repository
    if selected_branch:
        body["selected_branch"] = selected_branch
    r = session.post(f"{base_url}/api/conversations", json=body)
    r.raise_for_status()
    return r.json()


def get_conversation(session, base_url, conversation_id):
    r = session.get(f"{base_url}/api/conversations/{conversation_id}")
    r.raise_for_status()
    return r.json()


def write_outputs(conversation_id, status):
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"conversation-id={conversation_id}\n")
            f.write(f"status={status}\n")


def main():
    api_key = os.getenv("OPENHANDS_API_KEY")
    if not api_key:
        print("OPENHANDS_API_KEY is required", file=sys.stderr)
        sys.exit(2)

    prompt_input = os.getenv("INPUT_PROMPT", "").strip()
    if not prompt_input:
        print("inputs.prompt is required", file=sys.stderr)
        sys.exit(2)

    initial_user_msg = read_prompt(prompt_input)
    repository = os.getenv("INPUT_REPOSITORY", "").strip() or os.getenv("GITHUB_REPOSITORY", "")
    selected_branch = os.getenv("INPUT_SELECTED_BRANCH", "").strip()
    base_url = os.getenv("INPUT_BASE_URL", "https://app.all-hands.dev").strip()

    poll = (os.getenv("INPUT_POLL", "true").lower() == "true")
    timeout = int(os.getenv("INPUT_TIMEOUT", "1200"))
    interval = int(os.getenv("INPUT_INTERVAL", "30"))

    session, base_url = api_session(api_key, base_url)

    try:
        created = create_conversation(session, base_url, initial_user_msg, repository, selected_branch)
    except requests.HTTPError as e:
        print(f"Create conversation failed: {e} - {getattr(e.response, 'text', '')}", file=sys.stderr)
        sys.exit(1)

    conversation_id = created.get("conversation_id") or created.get("id") or ""
    status = str(created.get("status", "")).upper()

    if not conversation_id:
        print(f"Unexpected response: {json.dumps(created, indent=2)}", file=sys.stderr)
        sys.exit(1)

    print(f"Conversation created: {conversation_id} (status={status})")

    if not poll:
        write_outputs(conversation_id, status or "UNKNOWN")
        return

    start = time.time()
    last_status = status or "UNKNOWN"

    while time.time() - start < timeout:
        try:
            convo = get_conversation(session, base_url, conversation_id)
        except requests.HTTPError as e:
            print(f"Polling error: {e} - {getattr(e.response, 'text', '')}", file=sys.stderr)
            time.sleep(interval)
            continue

        last_status = str(convo.get("status", "")).upper()
        print(f"Status: {last_status}")
        if last_status in {"STOPPED", "FAILED", "ERROR", "CANCELLED"}:
            break

        time.sleep(interval)

    write_outputs(conversation_id, last_status)

    if last_status in {"FAILED", "ERROR", "CANCELLED"}:
        # Fail the step if terminal error state
        sys.exit(1)


if __name__ == "__main__":
    main()