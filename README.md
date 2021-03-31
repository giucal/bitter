# Bitter

Bitter is a command-line interface for the [fernet] authenticated encryption
scheme.

[fernet]: https://github.com/fernet/spec/blob/master/Spec.md

### Usage

To generate a random fernet key:

    python3 bitter.py generate > bitter-key

Encryption and decryption require a key and an input. Bitter expects you
to provide either the `-k` or `-i` option. The two are mutually exclusive:

  - `-k <file>` sets bitter to read the key from the first line of `<file>`
    and the input from stdin.

  - `-i <file>` sets bitter to read the input from `<file>` and
    the key from the first line of stdin.

To encrypt and decrypt with a key file:

    python3 bitter.py encrypt -k bitter-key < secrets.txt > secrets.txt.bitter
    python3 bitter.py decrypt -k bitter-key < secrets.txt.bitter > secrets.txt

I don't envision any practical use of the `-k-` and `-i-` forms, which have
the same effect of conflating the key and the input; anyway, the key is always
read first.

Upon encryption, bitter can append an explanatory annotation for you. Just
provide the `-x` option:

    $ python3 bitter.py encrypt -x -k bitter-key < secrets.txt
    gAAAAABbbdhfYLHI4ETHr6tqKRbf0hhoN68-gA-8d2FlBClV9E79MpbENXK5sKrUrq_GjXVetcSIJLk3cp5pW-puq0gwBz8R-11rfvhxPnjV3Mxulmy21w8=
    This is a bitter token file. The above line contains a fernet token.
    Bitter: https://github.com/giucal/bitter
    Fernet: https://github.com/fernet/spec/blob/master/Spec.md

Using bitter in a pipeline is fine for small messages, but consider that bitter
processes the input as a whole, not incrementally!

    source | python3 bitter.py encrypt -k bitter-key | destination
    source | python3 bitter.py decrypt -k bitter-key | destination

### How it works

Fernet (and so bitter) can encrypt a message as a *token*, an authenticated and
self-contained ciphertext encoded as a [base64url] string. To do so, it takes
a secret key.

[base64url]: https://tools.ietf.org/html/rfc4648

To turn fernet's high-level interface into an I/O command, bitter introduces
some format conventions.

A **key file** is a file starting with a [fernet key]. When reading a key (from
stdin or from a file) bitter ignores everything following the first line feed.

    $ cat examples/bitter-key
    uTnXlfGfvd0RyuphRkDgb0gqXMqRzjni-Rdi86YGk8g=
    You can write any annotation after a key. This can be useful
    if you want to store keys long-term or share them, in that you
    can note down what they're for without relying on file names.

    An annotation is not strictly part of the key, but rather of
    the storage format.

[fernet key]: https://github.com/fernet/spec/blob/master/Spec.md#key-format

A **token file** is a file starting with a [fernet token]. When reading a
token, bitter ignores everything following the first line feed.

    $ cat examples/secrets.txt.bitter
    gAAAAABbbdhfYLHI4ETHr6tqKRbf0hhoN68-gA-8d2FlBClV9E79MpbENXK5sKrUrq_GjXVetcSIJLk3cp5pW-puq0gwBz8R-11rfvhxPnjV3Mxulmy21w8=
    This line, too, is an annotation. As such, it's NOT authenticated!

A token file annotation is **not authenticated**, thus you should either
fill it with information useful for decryption, or else leave it out!

[fernet token]: https://github.com/fernet/spec/blob/master/Spec.md#token-format

### Cryptographic properties of fernet tokens

A *fernet token* has the following properties:

  - It's self-contained.
    All we need to know in order to decrypt it, is the key.

  - It's authenticated.
    No one who doesn't know the key can modify it without us noticing.

    **N.B.** This is true of *fernet tokens*; any annotation included in
    *bitter token files* is *not* part of the fernet token, and its
    integrity is not guaranteed *at all!*

  - It's timestamped.
    Everyone can see when it was created; and that time is
    authenticated, so we can reject tokens we deem expired.
