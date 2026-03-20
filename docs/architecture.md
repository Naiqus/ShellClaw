# Architecture

## Control Plane vs Execution Plane

ShellClaw separates concerns into two planes:

* **Control Plane** (ShellClaw CLI): Lifecycle management, state migration, resource orchestration
* **Execution Plane** (OpenShell): Container isolation, network proxy, policy enforcement

## Module Dependency Graph

```
commands/          CLI layer (user-facing)
  |
  v
core/              Business logic
  |
  v
core/shell.py      Single subprocess integration point
  |
  v
openshell CLI      External process (execution plane)
```

All `openshell` and `docker` subprocess calls are funneled through `core/shell.py`. This provides a single mock point for testing.

## Key Design Decisions

### No GPU Flag

NemoClaw hardcodes `--gpu` in sandbox creation and gateway startup. ShellClaw explicitly omits this flag everywhere. Sandboxes are pure compute/network isolation boundaries.

### Inference Routing via Virtual Endpoint

All model calls inside the sandbox are proxied through `https://inference.local`. The gateway redirects this to the configured backend (Ollama, OpenAI, Anthropic, etc.). The agent inside the sandbox is unaware of the actual backend.

### Credential Injection

Secrets are registered via `openshell provider create` and stored in gateway memory. They are injected as environment variables at sandbox runtime. Credentials never exist as files inside the sandbox filesystem.

### One File Per Command

Each CLI command lives in its own file under `commands/`. This follows Typer's recommended pattern for modular CLI tools.

## Security Model

### Filesystem (Landlock)

| Path                   | Permission  | Purpose           |
| ---------------------- | ----------- | ----------------- |
| `/usr`, `/lib`, `/etc` | read\_only  | System tools      |
| `/sandbox`             | read\_write | Agent workspace   |
| `/tmp`                 | read\_write | Temporary storage |
| Everything else        | blocked     | Default deny      |

### Network (OPA)

* Default deny for all outbound traffic
* Explicit allowlist per endpoint
* TLS termination for HTTP inspection on `rest` protocol endpoints
* Hot-reloadable via `openshell policy set`

## Adding a New Command

1. Create `src/shellclaw/commands/mycommand.py` with a function
2. Register it in `src/shellclaw/main.py` via `app.command()(mycommand)`
3. Add integration tests in `tests/integration/test_mycommand.py`

