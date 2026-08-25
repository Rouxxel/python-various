"""
#############################################################################
### Deterministic asymmetric key generator (passphrase + KDF)
###
### @file keys_generator_dtrmnstc.py
### @Sebastian Russo
### @date: 2026
#############################################################################

Derives a reproducible Ed25519 key pair from a passphrase using PBKDF2-HMAC-SHA256.

Unlike keys_generator.py (random RSA via OS CSPRNG), the same passphrase + salt +
KDF parameters always produce the same key pair. Salt and KDF settings are written
to a small metadata JSON file so keys can be reproduced later.

NOTE: Ed25519 keys are not compatible with en_de_crypt.py in the REST/GraphQL/
WebSocket templates, which expect RSA keys for OAEP encryption.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import secrets
import sys
from pathlib import Path
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

DEFAULT_ITERATIONS = 200_000
DEFAULT_METADATA_NAME = "key_derivation.json"
DEFAULT_PRIVATE_NAME = "private_key.pem"
DEFAULT_PUBLIC_NAME = "public_key.pem"


def derive_ed25519_keypair(
    passphrase: bytes,
    salt: bytes,
    iterations: int = DEFAULT_ITERATIONS,
):
    """Derive a deterministic Ed25519 key pair from passphrase, salt, and KDF settings."""
    if not passphrase:
        raise ValueError("Passphrase must not be empty.")
    if not salt:
        raise ValueError("Salt must not be empty.")
    if iterations < 1:
        raise ValueError("PBKDF2 iterations must be at least 1.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend(),
    )
    seed = kdf.derive(passphrase)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
    return private_key, private_key.public_key()


def export_key_pems(
    private_key: ed25519.Ed25519PrivateKey,
    public_key: ed25519.Ed25519PublicKey,
    pem_password: Optional[bytes] = None,
):
    """Serialize keys to PEM bytes. Optionally encrypt the private PEM."""
    if pem_password:
        encryption = serialization.BestAvailableEncryption(pem_password)
    else:
        encryption = serialization.NoEncryption()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def write_metadata(
    metadata_path: Path,
    *,
    algorithm: str,
    salt: bytes,
    iterations: int,
    private_key_file: str,
    public_key_file: str,
) -> None:
    metadata = {
        "algorithm": algorithm,
        "kdf": "PBKDF2-HMAC-SHA256",
        "iterations": iterations,
        "salt_b64": base64.b64encode(salt).decode("ascii"),
        "private_key_file": private_key_file,
        "public_key_file": public_key_file,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def generate_deterministic_keys(
    passphrase: bytes,
    output_dir: Path,
    *,
    salt: Optional[bytes] = None,
    iterations: int = DEFAULT_ITERATIONS,
    pem_password: Optional[bytes] = None,
    private_name: str = DEFAULT_PRIVATE_NAME,
    public_name: str = DEFAULT_PUBLIC_NAME,
    metadata_name: str = DEFAULT_METADATA_NAME,
) -> dict:
    """Generate deterministic keys and metadata files in output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    used_salt = salt if salt is not None else secrets.token_bytes(16)
    private_key, public_key = derive_ed25519_keypair(
        passphrase=passphrase,
        salt=used_salt,
        iterations=iterations,
    )
    private_pem, public_pem = export_key_pems(private_key, public_key, pem_password)

    private_path = output_dir / private_name
    public_path = output_dir / public_name
    metadata_path = output_dir / metadata_name

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)
    write_metadata(
        metadata_path,
        algorithm="Ed25519",
        salt=used_salt,
        iterations=iterations,
        private_key_file=private_name,
        public_key_file=public_name,
    )

    return {
        "private_path": private_path,
        "public_path": public_path,
        "metadata_path": metadata_path,
        "salt": used_salt,
        "iterations": iterations,
    }


def _parse_salt(value: str) -> bytes:
    """Accept raw UTF-8 text or base64-encoded salt."""
    if value.startswith("b64:"):
        return base64.b64decode(value[4:], validate=True)
    return value.encode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic Ed25519 key pair from a passphrase using PBKDF2. "
            "The same passphrase, salt, and iterations always produce the same keys."
        )
    )
    parser.add_argument(
        "-p",
        "--passphrase",
        help="Passphrase used for key derivation (prompted securely if omitted).",
    )
    parser.add_argument(
        "-s",
        "--salt",
        help=(
            "Salt for PBKDF2. Use plain text or prefix with b64: for base64 input. "
            "If omitted, a random salt is generated and saved to the metadata file."
        ),
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"PBKDF2 iteration count (default: {DEFAULT_ITERATIONS}).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory where PEM and metadata files are written (default: current directory).",
    )
    parser.add_argument(
        "--private-name",
        default=DEFAULT_PRIVATE_NAME,
        help=f"Private key filename (default: {DEFAULT_PRIVATE_NAME}).",
    )
    parser.add_argument(
        "--public-name",
        default=DEFAULT_PUBLIC_NAME,
        help=f"Public key filename (default: {DEFAULT_PUBLIC_NAME}).",
    )
    parser.add_argument(
        "--metadata-name",
        default=DEFAULT_METADATA_NAME,
        help=f"Metadata filename (default: {DEFAULT_METADATA_NAME}).",
    )
    parser.add_argument(
        "--pem-password",
        help="Optional password to encrypt the private PEM (prompted if flag is used without value).",
        nargs="?",
        const="",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    passphrase_text = args.passphrase
    if not passphrase_text:
        passphrase_text = getpass.getpass("Passphrase: ")
        confirm = getpass.getpass("Confirm passphrase: ")
        if passphrase_text != confirm:
            print("Error: passphrases do not match.", file=sys.stderr)
            return 1

    salt = _parse_salt(args.salt) if args.salt else None

    pem_password: Optional[bytes] = None
    if args.pem_password is not None:
        pem_password_text = args.pem_password or getpass.getpass("Private PEM password: ")
        pem_password = pem_password_text.encode("utf-8")

    try:
        result = generate_deterministic_keys(
            passphrase=passphrase_text.encode("utf-8"),
            output_dir=Path(args.output_dir),
            salt=salt,
            iterations=args.iterations,
            pem_password=pem_password,
            private_name=args.private_name,
            public_name=args.public_name,
            metadata_name=args.metadata_name,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Deterministic Ed25519 keys generated successfully!")
    print(f"Private key: {result['private_path']}")
    print(f"Public key:  {result['public_path']}")
    print(f"Metadata:    {result['metadata_path']}")
    if args.salt is None:
        print(
            "A random salt was generated and saved in the metadata file. "
            "Keep that file to reproduce the same keys later."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
