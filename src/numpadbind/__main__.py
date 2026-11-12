"""Entry point: `numpadbind [--background]` or `python -m numpadbind`."""
import argparse, sys

from . import __version__


def main(argv=None):
    p = argparse.ArgumentParser(prog="numpadbind", description="Bind apps and scripts to your numpad.")
    p.add_argument("--background", action="store_true", help="start in the tray without opening the window")
    p.add_argument("--debug", action="store_true", help="print what happens on every numpad keypress")
    p.add_argument("--diagnose", action="store_true", help="print how NumLock is detected, then exit")
    p.add_argument("--version", action="version", version=f"numpadbind {__version__}")
    args = p.parse_args(argv)
    if args.diagnose:
        from . import diagnose
        return diagnose.run()
    from .app import App          # imported late so --help/--version work without GTK
    return App(args.background, args.debug).run([sys.argv[0]])


if __name__ == "__main__":
    sys.exit(main())
