from pathlib import Path

from views import CLI


def main():
    cli = CLI()
    cli.start()


if __name__ == '__main__':
    (Path.cwd() / 'output').mkdir(exist_ok=True)
    main()
