import importlib
import pkgutil
from types import ModuleType

import click
import yaml
from tabulate import tabulate

import nu.plugins
from alembic import command
from alembic.config import Config
from nu.core.config import settings


@click.group()
def cli() -> None:
    pass


@cli.group()
def plugins() -> None:
    pass


@plugins.command()
def list() -> None:
    table = []
    for _, name, is_pkg in pkgutil.iter_modules(
        nu.plugins.__path__, nu.plugins.__name__ + "."
    ):
        plugin_module = importlib.import_module(name)
        plugin = plugin_module.Plugin
        table.append(
            {
                "name": plugin.NAME,
                "version": plugin.VERSION,
                "status": "Installed"
                if (plugin.NAME in settings.plugins)
                else "Available",
            }
        )

    click.echo(tabulate(table, headers="keys", tablefmt="pretty"))


@plugins.command()
@click.argument("plugin")
def install(plugin: str) -> None:

    if plugin in settings.plugins:
        raise click.ClickException(f"Plugin {plugin} is already installed")

    for _, name, is_pkg in pkgutil.iter_modules(
        nu.plugins.__path__, nu.plugins.__name__ + "."
    ):
        mod = importlib.import_module(name)
        plugin_obj = mod.Plugin
        if plugin_obj.NAME == plugin:
            break
    else:
        raise click.ClickException(f"Plugin {plugin} not found")

    alembic_cfg = get_alembic_cfg_for_module(mod)
    command.upgrade(alembic_cfg, "head")

    with open("nu.yaml") as f:
        config = yaml.safe_load(f)
    config["plugins"].append(plugin)
    with open("nu.yaml", "w") as f:
        yaml.dump(config, f)

    click.echo(f"Plugin {plugin} successfully installed")


@plugins.command()
@click.argument("plugin")
def uninstall(plugin: str) -> None:
    if plugin not in settings.plugins:
        raise click.ClickException(f"Plugin {plugin} is not installed")

    for _, name, is_pkg in pkgutil.iter_modules(
        nu.plugins.__path__, nu.plugins.__name__ + "."
    ):
        mod = importlib.import_module(name)
        plugin_obj = mod.Plugin
        if plugin_obj.NAME == plugin:
            break
    else:
        raise click.ClickException(f"Plugin {plugin} not found")

    alembic_cfg = get_alembic_cfg_for_module(mod)
    command.downgrade(alembic_cfg, "base")

    with open("nu.yaml") as f:
        config = yaml.safe_load(f)
    config["plugins"].remove(plugin)
    with open("nu.yaml", "w") as f:
        yaml.dump(config, f)

    click.echo(f"Plugin {plugin} successfully uninstalled")


def get_alembic_cfg_for_module(module: ModuleType) -> Config:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", f"{module.__name__}:revisions")
    return alembic_cfg
