"""
bitter -- command-line interface to the fernet AE scheme

Fernet (and so this command) is meant for small pieces of data that can
fit in memory.

For the full specification of the fernet scheme, see:
    https://github.com/fernet/spec/blob/master/Spec.md
"""

from argparse import (
    ArgumentParser,
    FileType,
    RawDescriptionHelpFormatter,
)
from sys import (
    argv,
    stdin,
    stdout,
    stderr,
)

from cryptography.fernet import (
    Fernet,
    InvalidToken,
)

__version__ = "0.1.0"

stdin = stdin.buffer
stdout = stdout.buffer

# Patch FileType's treatment of '-'.
class FileType(FileType):
    def __call__(self, name):
        if name == "-" and "b" in self._mode:
            if "r" in self._mode:
                return stdin
            if "w" in self._mode:
                return stdout
        return super().__call__(name)


def exit_error(message):
    print("%s: %s" % (argv[0], message), file=stderr)
    exit(1)


# An explanatory annotation that can be appended to new tokens.
PREDEFINED_TOKEN_ANNOTATION = (
    b"This is a bitter token file. The above line contains a fernet token.\n"
    b"Bitter: https://github.com/giucal/bitter\n"
    b"Fernet: https://github.com/fernet/spec/blob/master/Spec.md"
)


def encrypt(args):
    key = args.key_file.readline()
    ptxt = args.input.read(-1)

    try:
        cipher = Fernet(key)
    except ValueError:
        exit_error("bad key")

    ctxt = cipher.encrypt(ptxt)
    stdout.write(ctxt)
    stdout.write(b"\n")

    if args.auto_annotate:
        stdout.write(PREDEFINED_TOKEN_ANNOTATION)
        stdout.write(b"\n")


def decrypt(args):
    key = args.key_file.readline()
    ctxt = args.input.readline()

    try:
        cipher = Fernet(key)
    except ValueError:
        exit_error("bad key")

    try:
        ptxt = cipher.decrypt(ctxt, args.ttl)
    except InvalidToken:
        exit_error("authentication error")
    stdout.write(ptxt)


def generate_key(args):
    key = Fernet.generate_key()
    stdout.write(key)
    stdout.write(b"\n")


def version(args):
    from cryptography import __version__ as CRYPTOGRAPHY_VERSION

    print(f"bitter v{ __version__}")
    print(f"cryptography v{CRYPTOGRAPHY_VERSION} (fernet implementation)")


def run():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )

    data = ArgumentParser(add_help=False)
    data = data.add_mutually_exclusive_group(required=True)
    data.add_argument(
        "-k",
        metavar="<file>",
        dest="key_file",
        type=FileType("rb"),
        default=stdin,
        help="read key from <file>",
    )
    data.add_argument(
        "-i",
        metavar="<file>",
        dest="input",
        type=FileType("rb"),
        default=stdin,
        help="read input from <file> (and key from stdin)",
    )

    commands = parser.add_subparsers(
        title="commands",
        required=True,
        metavar="<command>",
        description=(
            "Commands supported by bitter. See '<command> --help' for details."
        ),
    )

    commands.add_parser(
        "version",
        help="print version",
        description="Print version details.",
    ).set_defaults(func=version)

    enc_mode = commands.add_parser(
        "encrypt",
        parents=[data],
        help="encrypt data into a token",
        description="Encrypt stdin (or <file>) into a fernet token.",
    )
    enc_mode.add_argument(
        "-x",
        dest="auto_annotate",
        action="store_true",
        help="append an explanatory annotation",
    )
    enc_mode.set_defaults(func=encrypt)

    dec_mode = commands.add_parser(
        "decrypt",
        parents=[data],
        help="decrypt a token",
        description="Decrypt the first line of stdin (or <file>).",
    )
    dec_mode.add_argument(
        "--ttl",
        metavar="<n>",
        type=int,
        default=None,
        help="reject tokens older than <n> seconds",
    )
    dec_mode.set_defaults(func=decrypt)

    gen_mode = commands.add_parser(
        "generate",
        help="generate a random fernet key",
    )
    gen_mode.set_defaults(func=generate_key)

    args = parser.parse_args()
    args.func(args)


def main():
    try:
        run()
    except KeyboardInterrupt:
        exit(1)


if __name__ == "__main__":
    main()
