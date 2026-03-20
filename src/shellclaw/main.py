from __future__ import annotations

import typer

from shellclaw import __version__
from shellclaw.commands.connect import connect
from shellclaw.commands.migrate import migrate
from shellclaw.commands.onboard import onboard
from shellclaw.commands.start import start
from shellclaw.commands.status import status
from shellclaw.commands.stop import stop

app = typer.Typer(
    name="shellclaw",
    help="Hardware-agnostic OpenClaw agent orchestration CLI",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"shellclaw {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    pass


app.command()(onboard)
app.command()(start)
app.command()(stop)
app.command()(connect)
app.command()(status)
app.command()(migrate)
