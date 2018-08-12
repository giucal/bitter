# Bitter

Bitter is a command-line interface for the [fernet] authenticated encryption
scheme.

[fernet]: https://github.com/fernet/spec/blob/master/Spec.md

--------------------------------------------------------------------------------

A **key file** is a file starting with a [fernet key]. Bitter ignores
everything following the first line feed.

    $ cat examples/bitter-key
    uTnXlfGfvd0RyuphRkDgb0gqXMqRzjni-Rdi86YGk8g=
    This is ignored by bitter.

[fernet key]: https://github.com/fernet/spec/blob/master/Spec.md#key-format

A **token file** is a file starting with -- guess -- a [fernet token].
Bitter ignores everything following the first line feed.

    $ cat examples/secrets.txt.bitter
    gAAAAABbbdhfYLHI4ETHr6tqKRbf0hhoN68-gA-8d2FlBClV9E79MpbENXK5sKrUrq_GjXVetcSIJLk3cp5pW-puq0gwBz8R-11rfvhxPnjV3Mxulmy21w8=
    This, too, is ignored by bitter.

[fernet token]: https://github.com/fernet/spec/blob/master/Spec.md#token-format

A fernet token has the following properties:

  - It's self-contained.
    All we need to know in order to decrypt it, is the key.

  - It's authenticated.
    No one who doesn't know the key can modify it without us noticing.

  - It's timestamped.
    Everyone can see when it was created; and that time is
    authenticated, so we can reject tokens we deem expired.

### Usage

To generate a random fernet key:

    python3 bitter.py generate > bitter-key

Since encrypting and decrypting requires a key and an input, bitter expects
one to provide either the `-k` or `-i` option. The two are mutually exclusive:

  - `-k <file>` sets bitter to read the key from the first line of `<file>`
    and the input from stdin.

  - `-i <file>` sets bitter to read the input from `<file>` and
    the key from the first line of stdin.

To encrypt and decrypt with a key file, one would:

    python3 bitter.py encrypt -k bitter-key < secrets.txt > secrets.txt.bitter
    python3 bitter.py decrypt -k bitter-key < secrets.txt.bitter > secrets.txt

Piping is fine, but consider that bitter processes the input as a whole,
not incrementally.

    source | python3 bitter.py encrypt -k bitter-key | destination
    source | python3 bitter.py decrypt -k bitter-key | destination

Instead, with an online key, one would:

    key-source | python3 bitter.py encrypt -i secrets.txt > secrets.txt.bitter

I don't envision any practical use of the `-k-` and `-i-` forms, which have
the same effect of conflating the key and the input; anyway, the key is always
read first.
