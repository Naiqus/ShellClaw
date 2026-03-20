#!/usr/bin/env bash
set -euo pipefail

# ShellClaw One-Click Deployment Script
# Idempotent installer: safe to run multiple times.

SHELLCLAW_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${SHELLCLAW_DIR}/.venv"
WRAPPER_PATH="/usr/local/bin/shellclaw"
OPENCLAW_HOME="${HOME}/.openclaw"
SHELLCLAW_HOME="${HOME}/.shellclaw"
DEFAULT_SANDBOX_NAME="openclaw-sandbox"

# --- Logging helpers ---
log_info()    { printf '\033[34m[INFO]\033[0m %s\n' "$1"; }
log_success() { printf '\033[32m[OK]\033[0m %s\n' "$1"; }
log_warn()    { printf '\033[33m[WARN]\033[0m %s\n' "$1"; }
log_error()   { printf '\033[31m[ERROR]\033[0m %s\n' "$1"; }
log_step()    { printf '\033[36m[%s/%s]\033[0m %s\n' "$1" "$2" "$3"; }

TOTAL_PHASES=5

# ============================================================
# Phase 1: Environment Validation
# ============================================================
log_step 1 "$TOTAL_PHASES" "Validating environment..."

# Detect OS and architecture
OS="$(uname -s)"
ARCH="$(uname -m)"
log_info "Detected: ${OS} / ${ARCH}"

# Check Docker
if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        log_success "Docker is available and running"
    else
        log_error "Docker is installed but the daemon is not running. Please start Docker."
        exit 1
    fi
else
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Python 3.10+
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        version="$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
        major="${version%%.*}"
        minor="${version#*.}"
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    log_error "Python 3.10+ is required but not found."
    exit 1
fi
log_success "Python found: ${PYTHON_CMD} ($(${PYTHON_CMD} --version 2>&1))"

log_success "Environment validated"

# ============================================================
# Phase 2: OpenClaw State Discovery
# ============================================================
log_step 2 "$TOTAL_PHASES" "Discovering existing OpenClaw state..."

MIGRATE_STATE=false
if [ -d "${OPENCLAW_HOME}" ]; then
    if [ -d "${OPENCLAW_HOME}/credentials" ] && [ -d "${OPENCLAW_HOME}/agents" ]; then
        file_count=$(find "${OPENCLAW_HOME}" -type f | wc -l | tr -d ' ')
        log_info "Found existing OpenClaw state: ${OPENCLAW_HOME} (${file_count} files)"
        MIGRATE_STATE=true
    else
        log_warn "OpenClaw directory exists but structure is incomplete. Skipping migration."
    fi
else
    log_info "No existing OpenClaw state found. Fresh installation."
fi

# ============================================================
# Phase 3: Install uv & ShellClaw
# ============================================================
log_step 3 "$TOTAL_PHASES" "Installing ShellClaw..."

# Install uv if not available
if ! command -v uv >/dev/null 2>&1; then
    if [ -x "${HOME}/.local/bin/uv" ]; then
        export PATH="${HOME}/.local/bin:${PATH}"
    else
        log_info "Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="${HOME}/.local/bin:${PATH}"
    fi
fi
log_success "uv is available"

# Install ShellClaw in a virtual environment
cd "${SHELLCLAW_DIR}"
uv sync
log_success "ShellClaw installed"

# ============================================================
# Phase 4: Shell Wrapper
# ============================================================
log_step 4 "$TOTAL_PHASES" "Setting up shell wrapper..."

mkdir -p "${SHELLCLAW_HOME}"

# Create wrapper script that activates venv transparently
WRAPPER_CONTENT="#!/usr/bin/env bash
exec \"${VENV_DIR}/bin/python\" -m shellclaw.main \"\$@\"
"

if [ -w "$(dirname "${WRAPPER_PATH}")" ]; then
    printf '%s' "${WRAPPER_CONTENT}" > "${WRAPPER_PATH}"
    chmod +x "${WRAPPER_PATH}"
    log_success "Shell wrapper installed at ${WRAPPER_PATH}"
else
    LOCAL_WRAPPER="${HOME}/.local/bin/shellclaw"
    mkdir -p "$(dirname "${LOCAL_WRAPPER}")"
    printf '%s' "${WRAPPER_CONTENT}" > "${LOCAL_WRAPPER}"
    chmod +x "${LOCAL_WRAPPER}"
    log_success "Shell wrapper installed at ${LOCAL_WRAPPER}"
    log_warn "Add ${HOME}/.local/bin to your PATH if not already present."
fi

# ============================================================
# Phase 5: Auto-Onboard (optional)
# ============================================================
log_step 5 "$TOTAL_PHASES" "Checking for auto-onboard..."

if command -v openshell >/dev/null 2>&1; then
    log_info "OpenShell detected. Running onboard..."
    "${VENV_DIR}/bin/python" -m shellclaw.main onboard || {
        log_warn "Auto-onboard failed. You can run 'shellclaw onboard' manually later."
    }

    if [ "${MIGRATE_STATE}" = true ]; then
        log_info "Migrating existing OpenClaw state..."
        "${VENV_DIR}/bin/python" -m shellclaw.main migrate || {
            log_warn "Auto-migration failed. You can run 'shellclaw migrate' manually later."
        }
    fi
else
    log_info "OpenShell not detected. Skipping auto-onboard."
    log_info "Install OpenShell, then run: shellclaw onboard"
fi

log_success "ShellClaw deployment complete!"
log_info "Use 'shellclaw status' to check system state, or 'shellclaw connect ${DEFAULT_SANDBOX_NAME}' to enter the sandbox."
