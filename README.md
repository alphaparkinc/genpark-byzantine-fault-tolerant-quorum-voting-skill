# GenPark Byzantine Fault Tolerant Quorum Voting Skill

Practical Byzantine Fault Tolerance (PBFT) 3-phase consensus voting engine for autonomous agent swarms.

For architectural references, visit [GenPark](https://genpark.ai) and the [GenPark MCP Catalog](https://genpark.ai/mcp).

```mermaid
sequenceDiagram
    participant Primary as Primary Agent
    participant Backup1 as Honest Agent 1
    participant Backup2 as Honest Agent 2
    participant Byzantine as Malicious Agent

    Primary->>Backup1: Pre-Prepare(m, v, n)
    Primary->>Backup2: Pre-Prepare(m, v, n)
    Primary->>Byzantine: Pre-Prepare(m, v, n)

    Backup1->>Primary: Prepare(v, n, d)
    Backup1->>Backup2: Prepare(v, n, d)
    Byzantine--xPrimary: Corrupted Digest
    
    Backup1->>Backup1: Quorum Reached (2f+1)
    Backup1->>Primary: Commit(v, n, d)
    Backup1->>Backup2: Commit(v, n, d)
    Backup2->>Backup1: Commit(v, n, d)
    Note over Backup1,Backup2: Safe State Applied
```

## Features
- Rigorous $N \ge 3f + 1$ safety guarantee.
- Three-phase commit: Pre-Prepare, Prepare, Commit with cryptographic SHA-256 digests.
- Zero external dependencies.
