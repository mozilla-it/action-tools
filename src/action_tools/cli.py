import click

from .gendocs import gendocs


@click.group()
def main():
    """Action Tools CLI"""
    pass


main.add_command(gendocs)


if __name__ == "__main__":
    main()
