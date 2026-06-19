import sys
from zipfile import ZipFile


def main() -> int:
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "-Z1":
        with ZipFile(args[1]) as archive:
            for name in archive.namelist():
                print(name)
        return 0
    print("unzip_compat.py supports only: unzip -Z1 <zipfile>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
