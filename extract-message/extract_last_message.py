#!/usr/bin/env python3
"""
GitHub Action and utility script to extract the last agent message from an OpenHands trajectory JSON file.

GitHub Action Usage:
    Called automatically by the extract-message action

Command Line Usage:
    python extract_last_message.py trajectory.json
    python extract_last_message.py trajectory.json --output last_message.json
    python extract_last_message.py trajectory.json --print-only
"""

import argparse
import json
import os
import sys
from pathlib import Path


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
        print(f"Error: Failed to extract last agent message: {e}", file=sys.stderr)
        return None


def write_github_outputs(message_data, message_file=None):
    """Write outputs to GitHub Actions output file."""
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            if message_file:
                f.write(f"message-file={message_file}\n")
            if message_data:
                f.write(f"action={message_data.get('action', '')}\n")
                f.write(f"message={message_data.get('message', '')}\n")
                f.write(f"timestamp={message_data.get('timestamp', '')}\n")


def main():
    # Check if running as GitHub Action
    is_github_action = bool(os.getenv("GITHUB_ACTIONS"))
    
    if is_github_action:
        # GitHub Action mode - get inputs from environment
        trajectory_file = os.getenv("INPUT_TRAJECTORY_FILE")
        output_file = os.getenv("INPUT_OUTPUT_FILE")
        format_type = os.getenv("INPUT_FORMAT", "json")
        
        if not trajectory_file:
            print("Error: trajectory-file input is required", file=sys.stderr)
            sys.exit(1)
            
        # Convert format to arguments
        print_only = format_type == "message-only"
        pretty = format_type == "pretty"
        
    else:
        # Command line mode - parse arguments
        parser = argparse.ArgumentParser(
            description="Extract the last agent message from an OpenHands trajectory JSON file"
        )
        parser.add_argument(
            "trajectory_file",
            help="Path to the trajectory JSON file"
        )
        parser.add_argument(
            "-o", "--output",
            help="Output file for the extracted message (default: print to stdout)"
        )
        parser.add_argument(
            "--print-only",
            action="store_true",
            help="Only print the message content, not the full JSON"
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Pretty print JSON output"
        )
        
        args = parser.parse_args()
        trajectory_file = args.trajectory_file
        output_file = args.output
        print_only = args.print_only
        pretty = args.pretty
    
    # Read trajectory file
    trajectory_path = Path(trajectory_file)
    if not trajectory_path.exists():
        print(f"Error: Trajectory file not found: {trajectory_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(trajectory_path, "r", encoding="utf-8") as f:
            trajectory_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in trajectory file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read trajectory file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Extract last agent message
    last_message = extract_last_agent_message(trajectory_data)
    if not last_message:
        print("No agent message or finish action found in trajectory", file=sys.stderr)
        if is_github_action:
            write_github_outputs(None)
        sys.exit(1)
    
    # Handle output
    message_file_path = None
    
    if print_only:
        # Just print the message content
        message = last_message.get("message", "")
        if message:
            print(message)
        else:
            print(f"[{last_message.get('action', 'unknown')} action with no message]")
    else:
        # Output full JSON
        if output_file:
            # Save to file
            output_path = Path(output_file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(last_message, f, indent=2 if pretty else None, ensure_ascii=False)
            message_file_path = str(output_path.absolute())
            if not is_github_action:
                print(f"Last agent message saved to: {message_file_path}")
        else:
            # Print to stdout (only in CLI mode)
            if not is_github_action:
                json.dump(last_message, sys.stdout, indent=2 if pretty else None, ensure_ascii=False)
                print()  # Add newline
    
    # Write GitHub Actions outputs
    if is_github_action:
        write_github_outputs(last_message, message_file_path)
    
    # Print summary to stderr (so it doesn't interfere with JSON output)
    if not is_github_action or not print_only:
        print(f"Action: {last_message.get('action')}", file=sys.stderr)
        if last_message.get('timestamp'):
            print(f"Timestamp: {last_message.get('timestamp')}", file=sys.stderr)
        if last_message.get('message'):
            message_len = len(last_message['message'])
            print(f"Message length: {message_len} characters", file=sys.stderr)


if __name__ == "__main__":
    main()