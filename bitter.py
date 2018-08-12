"""
bitter -- command-line interface to the fernet AE scheme

Fernet (and so this command) is meant for small pieces of data that can
fit in memory.

For the full specification of the fernet scheme, see:
    https://github.com/fernet/spec/blob/master/Spec.md
"""

from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
from sys import argv, stdin, stdout, stderr

from cryptography.fernet import Fernet, InvalidToken

stdin = stdin.buffer
stdout = stdout.buffer

# Patch FileType's treatment of '-'.
class FileType(FileType):
    def __call__(self, name):
        if name == '-' and 'b' in self._mode:
            if 'r' in self._mode:
                return stdin
            if 'w' in self._mode:
                return stdout
        return super().__call__(name)

def exit_error(message):
    print("%s: %s" % (argv[0], message), file=stderr)
    exit(1)

def encrypt(args):
    key = args.key_file.readline()
    ptxt = args.input.read(-1)

    try:
        cipher = Fernet(key)
    except ValueError:
        exit_error("bad key")

    ctxt = cipher.encrypt(ptxt)
    stdout.write(ctxt)
    stdout.write(b'\n')

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
    stdout.write(b'\n')

def main():
    parser = ArgumentParser(
        description=__doc__, formatter_class=RawDescriptionHelpFormatter)

    data = ArgumentParser(add_help=False)
    data = data.add_mutually_exclusive_group(required=True)
    data.add_argument(
        '-k',
        metavar='<file>',
        dest='key_file',
        type=FileType('rb'),
        default=stdin,
        help="read key from <file>")
    data.add_argument(
        '-i',
        metavar='<file>',
        dest='input',
        type=FileType('rb'),
        default=stdin,
        help="read input from <file> (and key from stdin)")

    commands = parser.add_subparsers(
        title="commands",
        required=True,
        metavar='<command>',
        description=
        "Commands supported by bitter. See '<command> --help' for details.")

    enc_mode = commands.add_parser(
        'encrypt',
        parents=[data],
        help="encrypt data into a token",
        description="Encrypt stdin (or <file>) into a fernet token.")
    enc_mode.set_defaults(func=encrypt)

    dec_mode = commands.add_parser(
        'decrypt',
        parents=[data],
        help="decrypt a token",
        description="Decrypt the first line of stdin (or <file>).")
    dec_mode.add_argument(
        '--ttl',
        metavar='<n>',
        type=int,
        default=None,
        help="reject tokens older than <n> seconds")
    dec_mode.set_defaults(func=decrypt)

    gen_mode = commands.add_parser(
        'generate', help="generate a random fernet key")
    gen_mode.set_defaults(func=generate_key)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(1)
