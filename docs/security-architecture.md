# Security architecture (v0.25)

Research control plane with strengthened zero-trust, expanded redaction (Discord/Telegram proxies, more BIP39), advanced lineage with triple-hash simulation, isolation checks. Not a certified product.

## Trust boundaries

Synthetic fixtures -> Source attestation + advanced Merkle-style lineage simulation (triple-hash) -> Strategy rules + regime/anomaly/correlation/multi-TF -> Risk gate (caps, kill switch, drawdown, concentration, adaptive) -> Paper fill only -> Hash-chained audit with enhanced lineage digest.

Trade/withdrawal keys refused. No live mode.

## Roles

Researcher / Auditor / Operator: all denied order placement. Operator can engage kill switch.

## Data classes

Symbol/OHLCV: public. Funding: public research. Source label: integrity (SYNTHETIC required). Read-only keys: optional, redacted. Trade keys: refused. Wallet: redacted/banned. Personal data: PDPA tripwire. Seeds: redacted. Solana/Discord/Telegram: redacted.

## Enhanced controls

- Expanded redaction: API keys, secrets, passwords, tokens, AWS, GitHub PATs, private key hex (64+), seed phrase proxies, BIP39 word proxies (expanded), JWTs, emails, Ethereum wallets, Solana base58, Discord tokens, Telegram bot tokens.
- Feed integrity: non-positive, stale (>15 min), jump (>25%), volume-price divergence anomaly, volatility spike, multi-TF inconsistency.
- Anomaly score: statistical (skew, kurtosis), volume consistency, isolation proxy, RSI divergence, volatility-adjusted.
- Audit: SHA-256 chain + simulated Merkle lineage over events with triple-hash and XOR encryption simulation.
- Zero-trust: mutual attestation simulation, advanced isolation anomaly checks, data residency note (research only), correlation gates, adaptive risk.

## Threats and controls

Secret committed: gitleaks + expanded redaction. Strategy injection: SYNTHETIC + attestation. Stale/jumped feed: status flags. Oversized risk: class caps + adaptive + correlation. Runaway: drawdown + kill switch. Audit tamper: chain + enhanced lineage. Live-order: mode guard + RBAC. Personal data / seeds / addresses / tokens: tripwire.

## Incident handling

1. Kill switch. 2. Freeze audit + lineage digest. 3. Rotate any pasted secret outside repo. 4. Human review before clear.

Default: research only. Promoting signals to broker is separate human-approved system.
