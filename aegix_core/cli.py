from __future__ import annotations

from pathlib import Path
import typer

from aegix_core.router import ToolRouter

app = typer.Typer(help="Aegix - Command Line Interface")

@app.command()
def run(
    cmd: str = typer.Option(..., "--cmd", help="Command to run inside docker sandbox"),
    image: str = typer.Option("python:3.11-slim", "--image", help="Docker image"),
    run_dir: Path = typer.Option(Path("runs"), "--run-dir", help="Runs output directory"),
) -> None:
    """
    Run a single command in an isolated docker container and persist artifacts + events
    """
    router = ToolRouter(run_dir=run_dir)
    cfg = RunConfig(cmd=cmd, image=image)
    result = router.handle(cfg)

    typer.echo(f"run_id: {result.run_id}")
    typer.echo(f"run_dir: {result.run_dir}")
    typer.echo(f"exit_code: {result.exit_code}")
    if result.exit_code != 0:
        typer.echo(f"stderr (tail): {result.stderr_tail}")

if __name__ == "__main__":
    app()