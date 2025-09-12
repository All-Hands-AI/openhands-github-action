import json
import os
import sys
import time
from pathlib import Path

import requests


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


def get_conversation(session, base_url, conversation_id):
    """Get conversation details via the OpenHands API."""
    r = session.get(f"{base_url}/api/conversations/{conversation_id}")
    r.raise_for_status()
    return r.json()


def get_trajectory(session, base_url, conversation_id):
    """Get the trajectory (event history) for a conversation."""
    response = session.get(
        f'{base_url}/api/conversations/{conversation_id}/trajectory'
    )
    response.raise_for_status()
    return response.json()


def get_conversation_url(base_url, conversation_id):
    """Construct the conversation URL for the web interface."""
    return f"{base_url}/conversations/{conversation_id}"


def extract_last_agent_message(trajectory_data):
    """Extract the last agent message with action 'message' or 'finish' from trajectory."""
    try:
        # Look for events in the trajectory
        events = trajectory_data.get("events", [])
        if not events:
            return None
        
        # Search backwards through events for the last agent message/finish action
        for event in reversed(events):
            if (event.get("source") == "agent" and 
                event.get("action") in ["message", "finish"]):
                return {
                    "action": event.get("action"),
                    "message": event.get("message", ""),
                    "timestamp": event.get("timestamp"),
                    "args": event.get("args", {}),
                    "extras": event.get("extras", {})
                }
        
        return None
    except Exception as e:
        print(f"Warning: Failed to extract last agent message: {e}")
        return None


def save_trajectory(trajectory_data, conversation_id):
    """Save trajectory data to a JSON file and extract last agent message."""
    filename = f"trajectory_{conversation_id}.json"
    filepath = Path(filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trajectory_data, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Trajectory saved to: {filepath.absolute()}")
    
    # Extract and save the last agent message
    last_message = extract_last_agent_message(trajectory_data)
    if last_message:
        message_filename = f"last_agent_message_{conversation_id}.json"
        message_filepath = Path(message_filename)
        
        with open(message_filepath, "w", encoding="utf-8") as f:
            json.dump(last_message, f, indent=2, ensure_ascii=False)
        
        print(f"💬 Last agent message saved to: {message_filepath.absolute()}")
        print(f"📝 Action: {last_message.get('action')}")
        if last_message.get('message'):
            # Show first 100 characters of the message
            message_preview = last_message['message'][:100]
            if len(last_message['message']) > 100:
                message_preview += "..."
            print(f"📄 Message preview: {message_preview}")
        
        return str(filepath.absolute()), str(message_filepath.absolute())
    
    return str(filepath.absolute()), None


def write_outputs(status, conversation_url, trajectory_file=None, last_message_file=None):
    """Write outputs to GitHub Actions output file."""
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"status={status}\n")
            f.write(f"conversation-url={conversation_url}\n")
            if trajectory_file:
                f.write(f"trajectory-file={trajectory_file}\n")
            if last_message_file:
                f.write(f"last-message-file={last_message_file}\n")


def main():
    # Get required inputs
    api_key = os.getenv("OPENHANDS_API_KEY")
    if not api_key:
        print("OPENHANDS_API_KEY is required", file=sys.stderr)
        sys.exit(2)

    conversation_id = os.getenv("INPUT_CONVERSATION_ID", "").strip()
    if not conversation_id:
        print("inputs.conversation-id is required", file=sys.stderr)
        sys.exit(2)

    # Get optional inputs
    base_url = os.getenv("INPUT_BASE_URL", "https://app.all-hands.dev").strip()
    timeout = int(os.getenv("INPUT_TIMEOUT", "1200"))
    interval = int(os.getenv("INPUT_INTERVAL", "30"))
    download_trajectory = (os.getenv("INPUT_DOWNLOAD_TRAJECTORY", "true").lower() == "true")

    # Create API session
    session, base_url = api_session(api_key, base_url)
    conversation_url = get_conversation_url(base_url, conversation_id)

    print(f"Polling conversation: {conversation_id}")
    print(f"🔗 View conversation: {conversation_url}")
    print("=" * 60)

    # Poll conversation until completion
    start = time.time()
    last_status = "UNKNOWN"

    while time.time() - start < timeout:
        try:
            convo = get_conversation(session, base_url, conversation_id)
        except requests.HTTPError as e:
            print(f"Polling error: {e} - {getattr(e.response, 'text', '')}", file=sys.stderr)
            time.sleep(interval)
            continue

        last_status = str(convo.get("status", "")).upper()
        elapsed = int(time.time() - start)
        print(f"[{elapsed:4d}s] Status: {last_status}")
        
        if last_status in {"STOPPED", "FAILED", "ERROR", "CANCELLED"}:
            print(f"Conversation completed with status: {last_status}")
            break

        time.sleep(interval)
    else:
        print(f"Polling timed out after {timeout} seconds")

    # Download trajectory if requested and conversation is complete
    trajectory_file = None
    last_message_file = None
    if download_trajectory and last_status in {"STOPPED", "FAILED", "ERROR", "CANCELLED"}:
        try:
            print("📥 Downloading trajectory...")
            trajectory_data = get_trajectory(session, base_url, conversation_id)
            trajectory_file, last_message_file = save_trajectory(trajectory_data, conversation_id)
            print("✅ Trajectory downloaded successfully")
        except requests.HTTPError as e:
            print(f"Failed to download trajectory: {e} - {getattr(e.response, 'text', '')}", file=sys.stderr)
            # Don't fail the action if trajectory download fails
        except Exception as e:
            print(f"Error saving trajectory: {e}", file=sys.stderr)

    # Write GitHub Actions outputs
    write_outputs(last_status, conversation_url, trajectory_file, last_message_file)

    # Exit with appropriate code
    if last_status in {"FAILED", "ERROR", "CANCELLED"}:
        print(f"❌ Conversation ended with error status: {last_status}")
        sys.exit(1)
    elif last_status == "STOPPED":
        print("✅ Conversation completed successfully")
    else:
        print(f"⚠️  Conversation status: {last_status}")


if __name__ == "__main__":
    main()