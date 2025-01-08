import click
import os
from workspaces import HyprlandManager#, SwayManager

def get_window_manager(manager_type: str):
    if manager_type == "hyprland":
        return HyprlandManager()
    # elif manager_type == "sway":
    #     return SwayManager()
    else:
        raise ValueError(f"Unsupported manager type: {manager_type}")


@click.group()
@click.option("--manager", required=True, type=click.Choice(["hyprland", "sway"]), help="The window manager to use.")
@click.pass_context
def cli(ctx, manager):
    """Unified CLI for managing workspaces across different window managers."""
    ctx.obj = get_window_manager(manager)  # Pass the manager instance to subcommands


@cli.command()
@click.pass_context
def open_workspaces_list_view(ctx):
    """Open the workspace list view using Eww."""
    wm = ctx.obj  # Get the window manager instance
    wm.set_eww_workspace()
    os.system("eww open workspaces")

@cli.command()
@click.option("--workspace", required=True, help="The workspace to switch to (ID for Hyprland, Name for Sway).")
@click.pass_context
def switch_workspace(ctx, workspace):
    """Switch to a specific workspace."""
    wm = ctx.obj  # Get the window manager instance
    wm.switch_workspace(workspace)


@cli.command()
@click.option("--workspace", required=True, help="The workspace to switch to (ID for Hyprland, Name for Sway).")
@click.option("--name", required=True, help="The new worksace name")
@click.pass_context
def rename_workspace(ctx, workspace: int, name: str):
    """Switch to a specific workspace."""
    wm = ctx.obj  # Get the window manager instance
    wm.rename_workspace(workspace, name)


if __name__ == "__main__":
    cli()
