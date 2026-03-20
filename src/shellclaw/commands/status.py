from __future__ import annotations

from shellclaw.core.gateway import get_gateway_status
from shellclaw.core.inference import get_inference_config
from shellclaw.core.provider import list_providers
from shellclaw.core.sandbox import list_sandboxes
from shellclaw.utils.console import console, create_status_table


def status() -> None:
    """Show system-wide status of gateway, sandboxes, inference, and providers."""
    # Gateway
    gw = get_gateway_status()
    gw_state = "[green]running[/green]" if gw.running else "[red]stopped[/red]"
    gw_table = create_status_table(
        "Gateway",
        ["Status", "Host", "Version"],
        [[gw_state, gw.host, gw.version]],
    )
    console.print(gw_table)

    # Sandboxes
    sandboxes = list_sandboxes()
    if sandboxes:
        sb_rows = [[s.name, s.state] for s in sandboxes]
        sb_table = create_status_table("Sandboxes", ["Name", "State"], sb_rows)
        console.print(sb_table)
    else:
        console.print("[dim]No sandboxes found[/dim]")

    # Inference
    inf = get_inference_config()
    if inf:
        inf_table = create_status_table(
            "Inference",
            ["Provider", "Model", "Version"],
            [[inf.provider, inf.model, inf.version]],
        )
        console.print(inf_table)
    else:
        console.print("[dim]Inference not configured[/dim]")

    # Providers
    providers = list_providers()
    if providers:
        p_rows = [[p.name] for p in providers]
        p_table = create_status_table("Providers", ["Name"], p_rows)
        console.print(p_table)
    else:
        console.print("[dim]No providers registered[/dim]")
