# OpenHands GitHub Action

A reusable composite GitHub Action that starts OpenHands conversations from prompts or files. Now available in two modes: single-stage (legacy) and two-stage workflow for better control and artifact management.

## Features

- 🚀 **Simple Integration**: Start OpenHands conversations directly from your GitHub workflows
- 📝 **Flexible Prompts**: Use literal text or file paths for prompts
- 🔄 **Two-Stage Workflow**: Create conversations first, then poll and download trajectories separately
- 🎯 **Repository Targeting**: Specify which repository OpenHands should work with
- 🔐 **Secure**: Uses GitHub secrets for API keys
- 📊 **Rich Outputs**: Returns conversation ID, status, URLs, and trajectory files
- 📁 **Trajectory Download**: Automatically download conversation trajectories as artifacts

## 🎯 Available Actions

This repository provides **three separate GitHub Actions** that can be used independently or together:

| Action | Path | Description |
|--------|------|-------------|
| **Create Conversation** | `All-Hands-AI/openhands-github-action/create-conversation@v2` | Creates conversations and returns ID/URL immediately |
| **Poll Conversation** | `All-Hands-AI/openhands-github-action/poll-conversation@v2` | Polls conversations and downloads trajectories |
| **Extract Message** | `All-Hands-AI/openhands-github-action/extract-message@v2` | Extracts last agent message from trajectory files |

## Quick Start

### Two-Stage Workflow
```yaml
# Stage 1: Create conversation
- name: Create OpenHands conversation
  id: create
  uses: All-Hands-AI/openhands-github-action/create-conversation@v1
  with:
    prompt: "Please review the code and suggest improvements"
    openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}

# Stage 2: Poll and download trajectory
- name: Poll conversation and download trajectory
  uses: All-Hands-AI/openhands-github-action/poll-conversation@v1
  with:
    conversation-id: ${{ steps.create.outputs.conversation-id }}
    openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}

# Optional: Upload trajectory as artifact
- name: Upload trajectory
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: openhands-trajectory
    path: trajectory_*.json
```

## Inputs

### Single-Stage Action (action.yml)

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `prompt` | Prompt text or path to a prompt file | ✅ | - |
| `repository` | Repo to pass to OpenHands | ❌ | Current repository |
| `selected-branch` | Branch to pass to OpenHands | ❌ | - |
| `base-url` | OpenHands API base URL | ❌ | `https://app.all-hands.dev` |
| `poll` | Poll conversation until it stops (true/false) | ❌ | `true` |
| `timeout-seconds` | Polling timeout in seconds | ❌ | `1200` |
| `poll-interval-seconds` | Polling interval in seconds | ❌ | `30` |
| `github-token` | GitHub token (reserved for future features) | ❌ | - |
| `openhands-api-key` | OpenHands API key | ✅ | - |

### Create Conversation Action (create-conversation.yml)

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `prompt` | Prompt text or path to a prompt file | ✅ | - |
| `repository` | Repo to pass to OpenHands | ❌ | Current repository |
| `selected-branch` | Branch to pass to OpenHands | ❌ | - |
| `base-url` | OpenHands API base URL | ❌ | `https://app.all-hands.dev` |
| `openhands-api-key` | OpenHands API key | ✅ | - |

### Poll Conversation Action (poll-conversation.yml)

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `conversation-id` | Conversation ID to poll | ✅ | - |
| `base-url` | OpenHands API base URL | ❌ | `https://app.all-hands.dev` |
| `timeout-seconds` | Polling timeout in seconds | ❌ | `1200` |
| `poll-interval-seconds` | Polling interval in seconds | ❌ | `30` |
| `download-trajectory` | Download trajectory when complete (true/false) | ❌ | `true` |
| `openhands-api-key` | OpenHands API key | ✅ | - |

## Outputs

### Single-Stage Action

| Output | Description |
|--------|-------------|
| `conversation-id` | Created conversation ID |
| `status` | Final (or last-seen) conversation status |
| `conversation-url` | URL to view the conversation in the web interface |

### Create Conversation Action

| Output | Description |
|--------|-------------|
| `conversation-id` | Created conversation ID |
| `conversation-url` | URL to view the conversation in the web interface |
| `status` | Initial conversation status |

### Poll Conversation Action

| Output | Description |
|--------|-------------|
| `status` | Final conversation status |
| `conversation-url` | URL to view the conversation in the web interface |
| `trajectory-file` | Path to downloaded trajectory file (if download-trajectory is true) |
| `last-message-file` | Path to extracted last agent message file (if download-trajectory is true) |

## Two-Stage Workflow

The two-stage workflow provides better control and flexibility:

1. **Stage 1 (Create Conversation)**: Creates the conversation and returns the ID/URL immediately
2. **Stage 2 (Poll & Download)**: Polls the conversation until completion and downloads the trajectory

### Benefits of Two-Stage Workflow

- 🔗 **Early URL Access**: Get the conversation URL immediately to comment on PRs
- 📁 **Trajectory Artifacts**: Download conversation trajectories as GitHub artifacts
- 💬 **Last Message Extraction**: Automatically extract the final agent message or finish action
- 🎛️ **Better Control**: Separate creation from polling for more flexible workflows
- 🔄 **Retry Logic**: Retry polling without recreating conversations
- 📊 **Monitoring**: Better visibility into conversation status

### Stage 1: Create Conversation

```yaml
- name: Create OpenHands conversation
  id: create
  uses: All-Hands-AI/openhands-github-action/create-conversation@v1
  with:
    prompt: "Please review the code and suggest improvements"
    repository: ${{ github.repository }}
    selected-branch: ${{ github.ref_name }}
    openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}

# Comment the URL on a PR (optional)
- name: Comment conversation URL on PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '🤖 OpenHands conversation started: ${{ steps.create.outputs.conversation-url }}'
      })
```

### Stage 2: Poll and Download Trajectory

```yaml
- name: Poll conversation and download trajectory
  id: poll
  uses: All-Hands-AI/openhands-github-action/poll-conversation@v1
  with:
    conversation-id: ${{ steps.create.outputs.conversation-id }}
    timeout-seconds: "1800"
    poll-interval-seconds: "30"
    download-trajectory: "true"
    openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}

# Upload trajectory and last message as GitHub artifacts
- name: Upload trajectory artifacts
  uses: actions/upload-artifact@v4
  if: always() && steps.poll.outputs.trajectory-file
  with:
    name: openhands-trajectory-${{ steps.create.outputs.conversation-id }}
    path: |
      ${{ steps.poll.outputs.trajectory-file }}
      ${{ steps.poll.outputs.last-message-file }}
    retention-days: 30

# Optional: Display the last agent message
- name: Show last agent message
  if: steps.poll.outputs.last-message-file
  run: |
    echo "=== Last Agent Message ==="
    cat "${{ steps.poll.outputs.last-message-file }}"
```

## Usage Examples

### Basic Usage with Text Prompt

```yaml
name: Code Review
on: [push]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run code review
        uses: All-Hands-AI/openhands-github-action@v1
        with:
          prompt: "Please review the recent changes and provide feedback"
          openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}
```

### Using a Prompt File

```yaml
name: Documentation Update
on:
  schedule:
    - cron: "0 9 * * 1"  # Weekly on Mondays

jobs:
  update-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Update documentation
        uses: All-Hands-AI/openhands-github-action@v1
        with:
          prompt: scripts/prompts/update_docs.md
          repository: ${{ github.repository }}
          selected-branch: main
          openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}
```

### Two-Stage Workflow with PR Comments and Artifacts

```yaml
name: OpenHands Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  openhands-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
      
      # Stage 1: Create conversation
      - name: Create OpenHands conversation
        id: create
        uses: All-Hands-AI/openhands-github-action/create-conversation@v1
        with:
          prompt: |
            Please review this pull request and:
            1. Identify potential issues or bugs
            2. Suggest improvements for code quality
            3. Check for security vulnerabilities
            4. Verify test coverage is adequate
          repository: ${{ github.repository }}
          selected-branch: ${{ github.head_ref }}
          openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}
      
      # Comment the conversation URL on the PR
      - name: Comment conversation URL on PR
        uses: actions/github-script@v7
        with:
          script: |
            const conversationUrl = '${{ steps.create.outputs.conversation-url }}';
            const body = `🤖 **OpenHands Code Review Started**
            
            I'm analyzing this pull request. You can follow the progress here:
            
            🔗 [View Conversation](${conversationUrl})
            
            The review will be completed automatically and the results will be available as an artifact when finished.`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
      
      # Stage 2: Poll and download trajectory
      - name: Poll conversation and download trajectory
        id: poll
        uses: All-Hands-AI/openhands-github-action/poll-conversation@v1
        with:
          conversation-id: ${{ steps.create.outputs.conversation-id }}
          timeout-seconds: "1800"
          poll-interval-seconds: "30"
          download-trajectory: "true"
          openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}
      
      # Upload trajectory as artifact
      - name: Upload trajectory artifacts
        uses: actions/upload-artifact@v4
        if: always() && steps.poll.outputs.trajectory-file
        with:
          name: openhands-review-trajectory-${{ github.event.number }}
          path: |
            ${{ steps.poll.outputs.trajectory-file }}
            ${{ steps.poll.outputs.last-message-file }}
          retention-days: 30
      
      # Update PR with final status and extracted message
      - name: Update PR with completion status
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const status = '${{ steps.poll.outputs.status }}';
            const conversationUrl = '${{ steps.create.outputs.conversation-url }}';
            const trajectoryFile = '${{ steps.poll.outputs.trajectory-file }}';
            const lastMessageFile = '${{ steps.poll.outputs.last-message-file }}';
            
            let statusEmoji = '✅';
            let statusText = 'completed successfully';
            
            if (status === 'FAILED' || status === 'ERROR') {
              statusEmoji = '❌';
              statusText = 'encountered an error';
            } else if (status === 'CANCELLED') {
              statusEmoji = '⚠️';
              statusText = 'was cancelled';
            }
            
            // Read the extracted last message if available
            let lastMessage = '';
            if (lastMessageFile) {
              try {
                const fs = require('fs');
                const messageData = JSON.parse(fs.readFileSync(lastMessageFile, 'utf8'));
                lastMessage = messageData.message || '';
              } catch (e) {
                console.log('Could not read last message file:', e);
              }
            }
            
            const body = `🤖 **OpenHands Code Review ${statusEmoji}**
            
            The code review ${statusText}.
            
            🔗 [View Full Conversation](${conversationUrl})
            ${trajectoryFile ? '📁 Review trajectory has been saved as a workflow artifact.' : ''}
            
            ${lastMessage ? `
            ## Summary
            
            ${lastMessage}
            ` : ''}
            
            **Status:** \`${status}\``;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

### Advanced Configuration (Legacy Single-Stage)

```yaml
name: Complex Task
on: workflow_dispatch

jobs:
  complex-task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run complex OpenHands task
        id: openhands
        uses: All-Hands-AI/openhands-github-action@v1
        with:
          prompt: |
            Please analyze the codebase and:
            1. Identify potential security vulnerabilities
            2. Suggest performance improvements
            3. Update the README with your findings
          repository: ${{ github.repository }}
          selected-branch: ${{ github.ref_name }}
          base-url: https://app.all-hands.dev
          poll: "true"
          timeout-seconds: "1800"
          poll-interval-seconds: "45"
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}
      
      - name: Use outputs
        run: |
          echo "Conversation ID: ${{ steps.openhands.outputs.conversation-id }}"
          echo "Final Status: ${{ steps.openhands.outputs.status }}"
          echo "View conversation: ${{ steps.openhands.outputs.conversation-url }}"
```

### Without Polling

```yaml
name: Fire and Forget
on: workflow_dispatch

jobs:
  start-task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Start OpenHands task
        uses: All-Hands-AI/openhands-github-action@v1
        with:
          prompt: "Start working on the feature request in issue #123"
          poll: "false"  # Don't wait for completion
          openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}
```

## Setup

### 1. Get OpenHands API Key

1. Sign up at [app.all-hands.dev](https://app.all-hands.dev)
2. Generate an API key from your account settings
3. Add it to your repository secrets as `OPENHANDS_API_KEY`

### 2. Configure Repository Secrets

Go to your repository settings → Secrets and variables → Actions, and add:

- `OPENHANDS_API_KEY`: Your OpenHands API key

Optionally, you may also want to ensure `GITHUB_TOKEN` is available for future features.

### 3. Set Permissions

Make sure your workflow has appropriate permissions:

```yaml
permissions:
  contents: write        # If OpenHands needs to modify files
  pull-requests: write   # If OpenHands needs to create/update PRs
```

## Prompt Files

You can use prompt files for complex or reusable prompts. Create a file (e.g., `scripts/prompts/code_review.md`) with your prompt content:

```markdown
# Code Review Prompt

Please review the recent changes in this repository and:

1. Check for potential bugs or issues
2. Suggest improvements for code quality
3. Verify that tests are adequate
4. Update documentation if needed

Focus on:
- Security best practices
- Performance considerations
- Code maintainability
```

Then reference it in your workflow:

```yaml
with:
  prompt: scripts/prompts/code_review.md
  openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}
```

## Trajectory Message Extraction

The two-stage workflow automatically extracts the last agent message from the trajectory. You can also use the standalone utility:

### Standalone Utility

```bash
# Extract last message to a file
python scripts/extract_last_message.py trajectory.json --output last_message.json

# Print just the message content
python scripts/extract_last_message.py trajectory.json --print-only

# Pretty print the full JSON
python scripts/extract_last_message.py trajectory.json --pretty
```

### Message Format

The extracted message includes:
```json
{
  "action": "message",
  "message": "The actual message content from the agent",
  "timestamp": "2024-01-01T12:00:00Z",
  "args": {},
  "extras": {}
}
```

### Use Cases

- **PR Comments**: Extract the final summary to post as a comment
- **Notifications**: Send the conclusion to Slack/email
- **Reports**: Include the final message in automated reports
- **Analysis**: Process agent responses programmatically

## Extract Message Action

The `extract-message` action can be used independently to extract the last agent message from any trajectory file:

```yaml
- name: Extract last agent message
  id: extract
  uses: All-Hands-AI/openhands-github-action/extract-message@v2
  with:
    trajectory-file: "path/to/trajectory.json"
    output-file: "last_message.json"  # Optional
    format: "pretty"  # json (default), message-only, or pretty

- name: Use extracted message
  run: |
    echo "Action: ${{ steps.extract.outputs.action }}"
    echo "Message: ${{ steps.extract.outputs.message }}"
    echo "Timestamp: ${{ steps.extract.outputs.timestamp }}"
    echo "File: ${{ steps.extract.outputs.message-file }}"
```

### Extract Message Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `trajectory-file` | Path to the trajectory JSON file | ✅ | |
| `output-file` | Output file for extracted message | ❌ | (stdout) |
| `format` | Output format: `json`, `message-only`, or `pretty` | ❌ | `json` |

### Extract Message Outputs

| Output | Description |
|--------|-------------|
| `message-file` | Path to extracted message file (if output-file specified) |
| `action` | Action type of extracted message (`message` or `finish`) |
| `message` | The extracted message content |
| `timestamp` | Timestamp of the extracted message |

## Status Values

The action returns these possible status values:

- `RUNNING`: Conversation is still active
- `STOPPED`: Conversation completed successfully
- `FAILED`: Conversation failed due to an error
- `ERROR`: System error occurred
- `CANCELLED`: Conversation was cancelled
- `UNKNOWN`: Status could not be determined

## Error Handling

The action will:
- Exit with code 2 for configuration errors (missing API key, invalid inputs)
- Exit with code 1 for API errors or terminal conversation states (`FAILED`, `ERROR`, `CANCELLED`)
- Exit with code 0 for successful completion

## Contributing

This action is maintained by All Hands AI. For issues, feature requests, or contributions, please visit the [repository](https://github.com/All-Hands-AI/openhands-github-action).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📖 [OpenHands Documentation](https://docs.all-hands.dev)
- 💬 [Community Discord](https://discord.gg/ESHStjSjD4)
- 💬 [Join our Slack](https://dub.sh/openhands)
- 🐛 [Report Issues](https://github.com/All-Hands-AI/openhands-github-action/issues)