"""
ChaCha20-Poly1305 helpers and key management.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def load_psk(path: Path) -> bytes:
    """
    Load a pre-shared key from disk.
    """
    del path
    raise NotImplementedError("load_psk is not yet implemented.")


def encrypt_payload(key: bytes, nonce: bytes, payload: bytes, *, aad: Optional[bytes] = None) -> bytes:
    """
    Encrypt a payload with ChaCha20-Poly1305 and return ciphertext||tag.
    """
    del key, nonce, payload, aad
    raise NotImplementedError("encrypt_payload is not yet implemented.")


def decrypt_payload(key: bytes, nonce: bytes, ciphertext: bytes, *, aad: Optional[bytes] = None) -> bytes:
    """
    Decrypt a payload with ChaCha20-Poly1305 and return plaintext.
    """
    del key, nonce, ciphertext, aad
    raise NotImplementedError("decrypt_payload is not yet implemented.")


