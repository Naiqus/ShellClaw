from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Optional

import typer

from shellclaw.config.paths import DEFAULT_SANDBOX_NAME, OPENCLAW_HOME
from shellclaw.core.sandbox import exec_in_sandbox, upload_to_sandbox
from shellclaw.utils.console import log_error, log_info, log_step, log_success
from shellclaw.utils.validators import validate_openclaw_state_exists


def migrate(
    source: Optional[Path] = typer.Option(None, help="Path to OpenClaw state directory"),
    sandbox_name: str = typer.Option(DEFAULT_SANDBOX_NAME, help="Target sandbox name"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be migrated without executing"
    ),
) -> None:
    """Migrate existing OpenClaw state into a sandbox."""
    source_path = source or OPENCLAW_HOME
    total = 4

    # Step 1: Validate source
    log_step(1, total, "Validating source directory...")
    ok, err = validate_openclaw_state_exists(source_path)
    if not ok:
        log_error(err or "Source validation failed")
        raise typer.Exit(1)
    log_success(f"Source validated: {source_path}")

    # Step 2: Inventory
    log_step(2, total, "Scanning state directory...")
    items = list(source_path.rglob("*"))
    file_count = sum(1 for i in items if i.is_file())
    dir_count = sum(1 for i in items if i.is_dir())
    log_info(f"Found {file_count} files in {dir_count} directories")

    if dry_run:
        log_info("Dry run mode - no changes will be made")
        for item in items:
            if item.is_file():
                rel = item.relative_to(source_path)
                log_info(f"  Would migrate: {rel}")
        log_success("Dry run complete")
        return

    # Step 3: Package and upload
    log_step(3, total, "Packaging and uploading state...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / "openclaw-state"
        archive_file = Path(shutil.make_archive(
            str(archive_path), "gztar",
            root_dir=str(source_path.parent),
            base_dir=source_path.name,
        ))

        if not upload_to_sandbox(sandbox_name, archive_file, "/sandbox/.openclaw-migration.tar.gz"):
            log_error("Failed to upload state to sandbox")
            raise typer.Exit(1)
    log_success("State uploaded to sandbox")

    # Step 4: Extract and verify
    log_step(4, total, "Extracting and verifying in sandbox...")
    result = exec_in_sandbox(
        sandbox_name,
        "tar -xzf /sandbox/.openclaw-migration.tar.gz -C /sandbox && openclaw doctor",
    )
    if result.returncode != 0:
        log_error(f"Migration verification failed: {result.stderr}")
        raise typer.Exit(1)

    log_success("Migration complete! OpenClaw state has been transferred to the sandbox.")
