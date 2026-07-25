# Changelog

All notable changes to the `.hns` specification are recorded here.

## [Unreleased]

### In development — v2 model

A revised model is being specified. It **will** change field names and structure, so v0.1
should not be used as the basis for a production implementation. Planned changes, each
addressing a defect in v0.1 that cannot be fixed additively:

- **Typed lengths.** A conductor carries cut length and terminal-seated length
  simultaneously, each labelled, resolving an ambiguity v0.1 could not express.
- **Units on every value.** No unit encoded in a field name; metric becomes expressible.
- **String cavity identifiers**, so lettered positions (`A1`) work.
- **Controlled colour vocabulary** (IEC 60757) with explicit base/stripe roles.
- **Required segment identifiers**, so features can be positioned along a span — the
  prerequisite for ties, sleeving, protection and bundle diameter.
- **Routing over segments** rather than a walk over nodes, so a conductor that does not
  enter the bundle is described truthfully.
- **Connections with two or more ends**, making multi-drop nets and double-crimps native.
- **Scoped identifiers**, so each party can carry its own part numbering without the format
  privileging either.
- **RFC 8785 canonicalization** for the integrity hash (see below).
- **A separate, unhashed layout layer**, so redrawing a harness does not change its identity.

### Fixed

- **Specification and schema scrubbed for publication.** Descriptions rewritten as
  third-party-facing prose; internal references removed.
- **Conformance section corrected.** §8 previously required `manifest.json` to validate
  against the schema root. The root describes the whole container as a single combined
  document that exists nowhere on disk, so that check could never pass. It now points at
  `#/definitions/manifest`, with worked instructions for off-the-shelf validators.
- **Broken citation removed** from §7, which referenced an implementation file not present
  in this repository.
- **Known defects documented** rather than left implicit — new §8.1.
- **Licensing split made real.** `LICENSE` is now unmodified MIT; CC BY 4.0 moves to
  `LICENSE-SPEC` with its canonical URL, an attribution string, and a per-path scope table.
  Previously the CC BY claim was prose appended below the MIT text, which meant automated
  license detection saw only MIT.
- **README** now links the specification (previously reachable only as inert text inside a
  code block), leads with the hosted viewer, states adoption honestly, and adds a
  prior-art section covering KBL, VEC and HCV.

### Corrected record

- The entry below dated 2026-07-23 claimed container drawing paths had been made
  vendor-neutral. **That was accurate for the schema only** — the reference generator was not
  updated, so every drawing record produced to date still uses vendor-named folders and
  violates the published pattern. Corrected in the v2 generator work.

## [0.1.1] — 2026-07-23

- **Reference viewer added** (`docs/index.html`): a single self-contained page that opens any
  `.hns` client-side — reads the ZIP in-browser, shows embedded drawings, a pin-to-pin chart
  and a wire list. Vendor/customer part numbers only; no auto-generated schematic.
- **Reference validator added** (`reference-tools/validate_hns.py`): checks container layout,
  topology invariants, hash integrity and embedded-drawing hashes. Python standard library
  only.
- **Synthetic example added** (`examples/HNS-DEMO-001.hns`): fictional `DEMO-*` parts only,
  demonstrating a plug-to-receptacle run, a double-crimp ferrule, and a loose ground lead.
- **Container drawing paths made vendor-neutral in the schema** — `drawings/source/` and
  `drawings/customer/`. See "Corrected record" above.
- **Added §7 "Structural validity rules"** — the graph-theory rules a JSON Schema cannot
  express. Previously these existed only in the reference implementation, so an independent
  producer had no way to build a conformant file without reading that source.
- **`meta.json` gained an optional `drawings[]` array** for embedded drawings, each with its
  own content hash.

## [0.1.0] — pre-release draft (2026-07-21)

- Initial public draft of the `emip-harness/1` format.
- Defines the ZIP container layout (`mimetype`, `manifest.json`, `meta.json`, `README.txt`,
  optional `enrichment.json`), the harness graph model, `meta` provenance and `graphSha256`
  integrity, additive versioning with unknown-field preservation, and the self-describing
  requirement.

_Not a stable release. Field names and required fields will change before v1._
