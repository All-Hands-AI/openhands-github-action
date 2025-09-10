# OpenHands GitHub Action

A reusable composite GitHub Action that starts OpenHands conversations from prompts or files, with optional polling until completion.

## Features

- 🚀 **Simple Integration**: Start OpenHands conversations directly from your GitHub workflows
- 📝 **Flexible Prompts**: Use literal text or file paths for prompts
- 🔄 **Automatic Polling**: Optionally poll conversations until they complete
- 🎯 **Repository Targeting**: Specify which repository OpenHands should work with
- 🔐 **Secure**: Uses GitHub secrets for API keys
- 📊 **Outputs**: Returns conversation ID and status for downstream steps

## Quick Start

```yaml
- name: Run OpenHands conversation
  uses: All-Hands-AI/openhands-github-action@v1
  with:
    prompt: "Please review the code and suggest improvements"
    openhands-api-key: ${{ secrets.OPENHANDS_API_KEY }}
```

## Inputs

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

## Outputs

| Output | Description |
|--------|-------------|
| `conversation-id` | Created conversation ID |
| `status` | Final (or last-seen) conversation status |

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

### Advanced Configuration

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

## Limitations

- Maximum polling timeout: configurable (default 20 minutes)
- Requires valid OpenHands API key
- Conversation status polling may have slight delays
- File prompts must be accessible in the workflow workspace

## Future Features

Planned enhancements include:
- Automatic PR/issue commenting with results
- Trajectory output saving as artifacts
- Enhanced error reporting and retry logic
- Integration with GitHub Apps for better permissions

## Contributing

This action is maintained by All Hands AI. For issues, feature requests, or contributions, please visit the [repository](https://github.com/All-Hands-AI/openhands-github-action).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📖 [OpenHands Documentation](https://docs.all-hands.dev)
- 💬 [Community Discord](https://discord.gg/ESHStjSjD4)
- 🐛 [Report Issues](https://github.com/All-Hands-AI/openhands-github-action/issues)