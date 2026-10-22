"""Cyber and data-security controls (v0.25).

Expanded redaction (more key formats, Discord, Telegram proxies), advanced isolation checks, improved lineage with triple-hash simulation. Research control plane.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from crypto_intel.models import AuditEvent, ExecutionMode

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|password|token|access[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
    re.compile(r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{8,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    re.compile(r"\b[A-Za-z0-9+/]{64,}={0,2}\b"),
    re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
    re.compile(r"\b[A-Za-z0-9]{24}\.[A-Za-z0-9]{6}\.[A-Za-z0-9_\-]{27}\b"),  # Discord token proxy
    re.compile(r"\b[0-9]{8,10}:[A-Za-z0-9_-]{35}\b"),  # Telegram bot token proxy
)

WALLET_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
SOLANA_PATTERN = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")
SEED_PATTERN = re.compile(r"(?i)(seed|mnemonic|phrase|bip39)\s*[:=]\s*['\"]?[a-z ]{20,}")
BIP39_PROXY = re.compile(r"\b(abandon|ability|able|about|above|absent|absorb|abstract|absurd|abuse|access|accident|account|accuse|achieve|acid|across|act|action)\b", re.IGNORECASE)

def redact(text: str) -> str:
    cleaned = text
    for pattern in SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    cleaned = WALLET_PATTERN.sub("[WALLET]", cleaned)
    cleaned = SOLANA_PATTERN.sub("[SOLANA]", cleaned)
    cleaned = SEED_PATTERN.sub("[SEED]", cleaned)
    cleaned = BIP39_PROXY.sub("[BIP39]", cleaned)
    return cleaned

def contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS) or bool(WALLET_PATTERN.search(text)) or bool(SOLANA_PATTERN.search(text)) or bool(SEED_PATTERN.search(text)) or bool(BIP39_PROXY.search(text))

def assert_paper_only(mode: ExecutionMode) -> None:
    if mode is not ExecutionMode.PAPER:
        raise PermissionError("live execution is disabled; this system is paper-only")

def hash_event(previous_hash: str, sequence: int, action: str, detail: str) -> str:
    material = f"{previous_hash}|{sequence}|{action}|{detail}".encode()
    return hashlib.sha256(material).hexdigest()

def _sim_encrypt(data: str, key: str = "research-key-v025") -> str:
    return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

def _triple_hash(data: str) -> str:
    h = hashlib.sha256(data.encode()).digest()
    h = hashlib.sha256(h).digest()
    return hashlib.sha256(h).hexdigest()

class AuditLog:
    """Append-only hash chain with advanced simulated Merkle lineage and encryption."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []
        self._previous = "GENESIS"
        self._lineage: list[str] = []

    def append(self, action: str, detail: str) -> AuditEvent:
        safe_detail = redact(detail)
        sequence = len(self.events) + 1
        digest = hash_event(self._previous, sequence, action, safe_detail)
        event = AuditEvent(sequence, action, safe_detail, self._previous, digest)
        self.events.append(event)
        self._previous = digest
        # Advanced lineage with triple-hash and encryption
        enc_digest = _sim_encrypt(digest)
        triple = _triple_hash(enc_digest)
        self._lineage.append(triple)
        if len(self._lineage) > 1:
            lineage_hash = _triple_hash("|".join(self._lineage[-2:]))
            self._lineage[-1] = lineage_hash
        return event

    def verify(self) -> bool:
        previous = "GENESIS"
        for event in self.events:
            expected = hash_event(previous, event.sequence, event.action, event.detail)
            if event.previous_hash != previous or event.digest != expected:
                return False
            previous = event.digest
        return True

    def lineage_root(self) -> str:
        return self._lineage[-1] if self._lineage else "GENESIS"

    def isolation_check(self) -> bool:
        """Advanced isolation anomaly: consistent length and verify."""
        return self.verify() and len(self._lineage) == len(self.events) and all(len(h) == 64 for h in self._lineage)
