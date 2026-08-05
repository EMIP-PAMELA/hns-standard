# Changelog

Notable changes to the `.hns` specification.

## [Unreleased]

### 2026-08-05 — repository moved to the company org

The repo, its Pages site, and the schema's `$id` moved from the personal `EMIP-PAMELA` account to
the company `nehemiah-holdings` GitHub organization. Nothing has been released yet, so this was the
cheapest time to make that move — no known external consumer had adopted the old URLs.

Initial draft, published for feedback. Nothing has been released yet, so field names and
required fields may still change. Areas actively being worked on are listed in
[SPECIFICATION §8.1](spec/SPECIFICATION.md) — most substantially, a formal canonicalization
scheme for the integrity hash, an explicit length datum (cut vs. terminal-seated), string
position identifiers, a controlled colour vocabulary, and segment identifiers so that
features can be located along a span.

### Contents

- **Specification** (`spec/SPECIFICATION.md`) — the container layout, the harness model,
  provenance and integrity, structural validity rules, and conformance.
- **JSON Schema** (`spec/hns-schema-1.json`) — the machine-validatable field contract.
- **Reference viewer** (`docs/index.html`) — a single self-contained page that opens any
  `.hns` client-side: reads the ZIP in the browser, shows embedded drawings, a pin-to-pin
  chart and a wire list. Hosted at
  [nehemiah-holdings.github.io/hns-standard](https://nehemiah-holdings.github.io/hns-standard/).
- **Reference validator** (`reference-tools/validate_hns.py`) — checks container layout,
  topology invariants, hash integrity and embedded-drawing hashes. Python standard library
  only.
- **Synthetic example** (`examples/HNS-DEMO-001.hns`) — fictional `DEMO-*` parts only,
  demonstrating a plug-to-receptacle run, a double-crimp ferrule, and a loose ground lead.
  Also served alongside the viewer for one-click loading.
