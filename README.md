# ShellClaw

OpenShell based OpenClaw agent orchestration CLI. A drop-in replacement for NemoClaw that removes NVIDIA hardware dependency while preserving OpenShell's security isolation.

## Features

* **Hardware-agnostic** -- runs on any Docker-capable machine (macOS, Linux, WSL2)
* **Dynamic inference routing** -- route to Ollama, OpenAI, Anthropic, Apple Metal, or any custom endpoint
* **State migration** -- seamlessly migrate existing `~/.openclaw` state into sandboxes
* **Secure by default** -- Landlock filesystem isolation + OPA network egress control
* **Credential injection** -- API keys never land on sandbox filesystem

## Quick Start

```Shell
# One-click setup
./setup.sh

# Or manual installation
uv sync
shellclaw onboard

# Connect to your sandbox
shellclaw connect
```

## Commands

| Command             | Description                                                    |
| ------------------- | -------------------------------------------------------------- |
| `shellclaw onboard` | Initialize: start gateway, configure inference, create sandbox |
| `shellclaw start`   | Start a sandbox (auto-starts gateway if needed)                |
| `shellclaw stop`    | Stop a sandbox (optionally stop gateway with `--gateway`)      |
| `shellclaw connect` | Attach terminal to a running sandbox                           |
| `shellclaw status`  | Show system-wide status                                        |
| `shellclaw migrate` | Migrate existing OpenClaw state into a sandbox                 |

## Inference Routing

Route the `inference.local` virtual endpoint to any backend:

```Shell
# Local Ollama
shellclaw onboard --inference-provider ollama --inference-model llama3

# Anthropic API
shellclaw onboard --inference-provider anthropic --inference-model claude-sonnet --inference-url https://api.anthropic.com

# OpenAI API
shellclaw onboard --inference-provider openai --inference-model gpt-4o --inference-url https://api.openai.com
```

## Architecture

```
+------------------+     +------------------+     +------------------+
|  ShellClaw CLI   | --> |  OpenShell       | --> |  Sandbox         |
|  (Control Plane) |     |  Gateway         |     |  (OpenClaw)      |
+------------------+     +------------------+     +------------------+
       |                        |                        |
  Python Typer            Landlock/OPA              inference.local
  lifecycle mgmt          isolation                 -> any backend
```

See [docs/architecture.md](docs/architecture.md) for details.

## Development

```Shell
uv sync
uv run pytest                          # Run tests
uv run pytest --cov=shellclaw          # With coverage
uv run ruff check src/ tests/          # Lint
```

## License

MIT
