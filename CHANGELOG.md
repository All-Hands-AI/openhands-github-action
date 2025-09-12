# Changelog

## [v2.0.0] - Two-Stage Workflow Support

### 🚀 New Features

#### Two-Stage Workflow
- **Stage 1 (Create Conversation)**: New `create-conversation.yml` action that creates a conversation and returns ID/URL immediately
- **Stage 2 (Poll & Download)**: New `poll-conversation.yml` action that polls until completion and downloads trajectory
- **Trajectory Download**: Automatic download of conversation trajectories as JSON files
- **GitHub Artifacts**: Easy integration with `actions/upload-artifact` for trajectory storage

#### Enhanced Outputs
- `trajectory-file`: Path to downloaded trajectory file (Stage 2)
- `last-message-file`: Path to extracted last agent message file (Stage 2)
- Improved conversation URL formatting and display
- Better status reporting and error handling

#### Message Extraction Utility
- **Automatic Extraction**: Last agent message with action "message" or "finish" automatically extracted
- **Standalone Script**: `scripts/extract_last_message.py` for processing any trajectory file
- **Multiple Output Formats**: JSON file, stdout, or message content only
- **Command Line Options**: Pretty printing, custom output paths, message-only mode

### 💡 Benefits of Two-Stage Workflow

1. **Early URL Access**: Get conversation URL immediately to comment on PRs
2. **Trajectory Artifacts**: Download and store conversation trajectories
3. **Message Extraction**: Automatically extract final agent messages for processing
4. **Better Control**: Separate creation from polling for flexible workflows
5. **Retry Logic**: Retry polling without recreating conversations
6. **Monitoring**: Better visibility into conversation progress

### 🎯 **Separate GitHub Actions Structure**

The repository now provides **three independent GitHub Actions**:

1. **Create Conversation** (`All-Hands-AI/openhands-github-action/create-conversation@v2`) - Stage 1 only
2. **Poll Conversation** (`All-Hands-AI/openhands-github-action/poll-conversation@v2`) - Stage 2 only  
3. **Extract Message** (`All-Hands-AI/openhands-github-action/extract-message@v2`) - Message extraction

### 📁 Clean Repository Structure

```
openhands-github-action/
├── create-conversation/
│   ├── action.yml                      # Create conversation action
│   └── create_conversation.py          # Stage 1 implementation
├── poll-conversation/
│   ├── action.yml                      # Poll conversation action
│   └── poll_conversation.py            # Stage 2 implementation
└── extract-message/
    ├── action.yml                      # Extract message action
    └── extract_last_message.py         # Message extraction (CLI + Action)
```

### 🔄 Usage Guide

**Complete Three-Stage Workflow:**
```yaml
# Stage 1: Create conversation
- name: Create OpenHands conversation
  id: create
  uses: All-Hands-AI/openhands-github-action/create-conversation@v2
  with:
    prompt: "Review this code"
    openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}

# Stage 2: Poll and download trajectory
- name: Poll conversation and download trajectory
  id: poll
  uses: All-Hands-AI/openhands-github-action/poll-conversation@v2
  with:
    conversation-id: ${{ steps.create.outputs.conversation-id }}
    openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}

# Stage 3: Extract final message (optional)
- name: Extract final agent message
  uses: All-Hands-AI/openhands-github-action/extract-message@v2
  with:
    trajectory-file: ${{ steps.poll.outputs.trajectory-file }}
    format: "pretty"

# Optional: Upload trajectory as artifact
- name: Upload trajectory
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: openhands-trajectory
    path: trajectory_*.json
```

### 🔧 API Changes

#### New Trajectory Download Function
```python
def get_trajectory(session, base_url, conversation_id):
    """Get the trajectory (event history) for a conversation."""
    response = session.get(
        f'{base_url}/api/conversations/{conversation_id}/trajectory'
    )
    response.raise_for_status()
    return response.json()
```

### 🧪 Testing

Use the provided test workflows to validate the implementation:

```bash
# Test two-stage workflow
gh workflow run test-two-stage.yml

# Compare single-stage vs two-stage
gh workflow run compare-workflows.yml
```

### 📚 Documentation

- Updated README with comprehensive two-stage examples
- Added PR comment integration examples
- Documented all new inputs and outputs
- Added troubleshooting section for trajectory downloads

### 🔒 Backward Compatibility

- **✅ Fully Backward Compatible**: Existing single-stage workflows continue to work unchanged
- **✅ Legacy Support**: Original `action.yml` and `openhands_run.py` remain functional
- **✅ Same API**: No breaking changes to existing inputs/outputs

### 🐛 Bug Fixes

- Improved error handling for API failures
- Better timeout management in polling logic
- Enhanced status reporting and logging

### 📋 Requirements

- Python 3.11+
- `requests` library
- GitHub Actions environment
- Valid OpenHands API key

---

## [v1.0.0] - Initial Release

- Single-stage workflow with conversation creation and polling
- Basic prompt support (text or file)
- Repository and branch targeting
- Configurable polling timeouts and intervals
- GitHub Actions integration