# Use Case Diagram — AstraNotes

```mermaid
graph LR
    Actor(["👤 User"])
    subgraph AstraNotes Application
        UC1["FR-01: Create Note"]
        UC2["FR-02: Edit Note"]
        UC3["FR-03: Delete Note"]
        UC4["FR-04: Toggle Privacy"]
        UC5["FR-05: Duplicate Note"]
        UC6["FR-07: Search Notes"]
        UC7["FR-08: View Note List (sorted)"]
        UC8["FR-10: View System Dashboard"]
        UC9["Unlock Passphrase"]
        UC10["Set Up Passphrase"]
        UC11["FR-09: Dynamic Button States"]
    end

    Actor --> UC1
    Actor --> UC2
    Actor --> UC3
    Actor --> UC4
    Actor --> UC5
    Actor --> UC6
    Actor --> UC7
    Actor --> UC8

    UC1 -.->|extends| UC9
    UC4 -.->|extends| UC9
    UC9 -.->|extends| UC10

    UC2 -.->|requires| UC11
    UC3 -.->|requires| UC11
    UC5 -.->|requires| UC11

    style Actor fill:#4a90d9,color:#fff
    style UC9 fill:#f59e0b,color:#000
    style UC10 fill:#f59e0b,color:#000
    style UC11 fill:#6b7280,color:#fff
```

## Use Case Descriptions

| ID | Use Case | Actor | Pre-condition | Main Flow | Post-condition |
|----|----------|-------|---------------|-----------|----------------|
| UC1 | **Create Note** | User | App running | Enter title; optionally body, tags, private flag; click Save | Note persisted; list refreshed |
| UC2 | **Edit Note** | User | Note selected (not locked) | Modify fields; click Save | Note updated; `modified_at` advanced |
| UC3 | **Delete Note** | User | Note selected | Click Delete (enabled) | Note removed; list refreshed |
| UC4 | **Toggle Privacy** | User | Note selected | Toggle "Private" switch; Save | Body re-encrypted or decrypted on disk |
| UC5 | **Duplicate Note** | User | Note selected | Click Duplicate | Copy with "Copy of …" title created |
| UC6 | **Search Notes** | User | — | Type keyword in search box | Matching notes displayed live |
| UC7 | **View Note List** | User | — | Open app | Notes sorted by `modified_at` desc; locked notes show 🔒 |
| UC8 | **System Dashboard** | User | — | Click System button | Live stats popup: note count, storage, encryption status |
| UC9 | **Unlock Passphrase** | User | `passphrase.json` exists | Enter passphrase in dialog | Encryption key loaded into memory |
| UC10 | **Set Up Passphrase** | User | No passphrase configured | Enter + confirm passphrase | Salt + verifier written to `passphrase.json`; key in memory |
| UC11 | **Dynamic Buttons** | System | — | Note selection changes | Delete/Duplicate enabled iff note selected |
