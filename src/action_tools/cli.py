import click

from .gendocs import gendocs
from .usage import usage


@click.group()
def main():
    """Action Tools CLI"""
    pass


main.add_command(gendocs)
main.add_command(usage)


if __name__ == "__main__":
    main()
