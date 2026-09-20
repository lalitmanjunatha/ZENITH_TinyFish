from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))


@dataclass(frozen=True)
class SharedSecret:
    """Authenticated encryption for a paired-device context.

    The base key is created during QR pairing and is never sent to the relay.
    """
    key: bytes

    @classmethod
    def new(cls) -> "SharedSecret":
        return cls(os.urandom(32))

    @classmethod
    def from_export(cls, exported: str) -> "SharedSecret":
        return cls(_unb64(exported))

    def export(self) -> str:
        return _b64(self.key)

    def _key_for(self, purpose: str) -> bytes:
        return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                    info=("zenith-fabric-v1:" + purpose).encode()).derive(self.key)

    def seal(self, value: dict, purpose: str = "event") -> dict[str, str]:
        nonce = os.urandom(12)
        aad = purpose.encode()
        plaintext = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
        ciphertext = AESGCM(self._key_for(purpose)).encrypt(nonce, plaintext, aad)
        return {"nonce": _b64(nonce), "ciphertext": _b64(ciphertext), "purpose": purpose}

    def open(self, envelope: dict[str, str]) -> dict:
        purpose = envelope["purpose"]
        plaintext = AESGCM(self._key_for(purpose)).decrypt(
            _unb64(envelope["nonce"]), _unb64(envelope["ciphertext"]), purpose.encode())
        return json.loads(plaintext)
