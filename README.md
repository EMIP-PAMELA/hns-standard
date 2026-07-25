# `.hns` — Open Wire-Harness Interchange Format

*An open format for exchanging wire-harness definitions between companies — carrying the
**meaning** of a harness (every connector, wire, pin, length, termination) as structured
data, not a picture of it.*

**Status: prototype / pre-release draft (v0.1).** Stewarded by Apogee Controls.

> **⚠️ v0.1 is superseded and a revised model (v2) is in development.** v0.1 remains
> published so existing files stay readable, but it has known defects — see
> [SPECIFICATION §8.1](spec/SPECIFICATION.md). **Don't build a production implementation
> against it yet.** Feedback on the direction is very welcome now.

**Try it:** [open the viewer](https://emip-pamela.github.io/hns-standard/) → drag in
[`examples/HNS-DEMO-001.hns`](examples/HNS-DEMO-001.hns). Nothing is uploaded; it runs
entirely in your browser.

**Who uses it:** Apogee Controls produces `.hns` from its own engineering system today.
There is no second implementer yet — that is exactly what this repository is for.

---

## Why

Today a harness is exchanged as a **drawing**. The receiving company re-interprets that
drawing into their own — and often sends it back to confirm they read it right. Every
hand-off is a chance to get a wire, a length, or a termination wrong.

A `.hns` file removes that interpretation layer. It carries the harness definition directly,
so there is nothing to re-draw and nothing to re-interpret.

## How this relates to existing formats

**KBL (VDA 4964), VEC (VDA 4968), and HCV already model harnesses**, and model them in far
more depth — 3D routing, bundle geometry, full manufacturing detail. Both KBL and VEC are
genuinely open: the XSDs are MIT-licensed and the model documentation is CC BY 4.0, free from
[prostep ivip](https://ecad-wiki.prostep.org/). If you already exchange KBL, **you do not
need this.**

`.hns` targets the case those formats do not reach: the small-to-mid harness shop and its
customer, exchanging a few hundred part numbers a year, today over PDF and email, with no
harness-CAD seat on either side. A three-wire lead assembly uses roughly a dozen of KBL's 104
types. The bar here is not "richer than KBL" — it is *"better than a PDF, and implementable
in an afternoon by one developer with the standard library."*

The v2 model deliberately borrows KBL's structure (typed lengths, string cavities, scoped
identifiers, positioned features) and supplies the tight vocabulary KBL leaves to reference
data. A field-by-field mapping will be published alongside it.

## Principles

1. **Open & documented.** The format is a published JSON Schema. Read one, write one, or
   build your own viewer — no proprietary reader, no royalties, no permission required. We
   version the *specification*; we do not lock the *data*.
2. **Self-describing — zero tooling required.** A `.hns` is a ZIP of plain, human-readable
   JSON with a plain-English `README.txt` inside it. No viewer? Unzip and read it, or build
   to the schema. It works with no other context, because the file explains itself.
3. **Verifiable.** Every file carries a content hash of its harness definition, so
   alteration after export is detectable. (This is an integrity check, not a signature — it
   does not establish who authored or approved the harness.)
4. **One file, many views.** The same data drives a schematic, a pin-to-pin chart, a wire
   list, a cut sheet. The data never changes; the reader chooses the lens.

## Non-goals

- 3D vehicle routing, splines, or installation geometry.
- Vehicle or module configuration, option codes, variant management.
- Replacing the customer's drawing as the controlling document. **The drawing governs;**
  a `.hns` is a derived interpretation of it.
- Competing with KBL/VEC on depth.

## Repository layout

| Path | |
|---|---|
| [`spec/SPECIFICATION.md`](spec/SPECIFICATION.md) | Human-readable specification |
| [`spec/hns-schema-1.json`](spec/hns-schema-1.json) | Machine-validatable JSON Schema |
| [`examples/`](examples/) | **Synthetic** example files — fictional parts only (see policy) |
| [`reference-tools/`](reference-tools/) | Reference validator (MIT) |
| [`docs/index.html`](docs/index.html) | Reference viewer — also the hosted page above |
| [`GOVERNANCE.md`](GOVERNANCE.md) | How the spec is versioned and changed |
| [`CHANGELOG.md`](CHANGELOG.md) | |
| [`LICENSE`](LICENSE) · [`LICENSE-SPEC`](LICENSE-SPEC) | MIT (code) · CC BY 4.0 (spec text) |

## How to read a `.hns`

1. **The hosted viewer** — [emip-pamela.github.io/hns-standard](https://emip-pamela.github.io/hns-standard/).
   Drop in any `.hns` and it renders in your browser: embedded drawings, pin-to-pin chart,
   wire list. No install, no upload, no network round-trip.
2. **Unzip it** — it's a ZIP of plain JSON with a `README.txt` inside. No tools required.
3. **Your own tools** — build to [`spec/hns-schema-1.json`](spec/hns-schema-1.json) and
   ingest directly. Check a file with
   [`reference-tools/validate_hns.py`](reference-tools/validate_hns.py) (Python stdlib only).

## Licensing

- **Specification text** (`spec/`, `*.md`): CC BY 4.0 — see [LICENSE-SPEC](LICENSE-SPEC).
- **Reference implementation** (`reference-tools/`, `docs/index.html`): MIT — see
  [LICENSE](LICENSE).

**Patent non-assertion.** Apogee Controls will not assert any patent it holds that is
necessarily infringed by implementing this specification, against any conforming
implementation.

## ⚠️ Data policy (read before committing anything)

This is a **public-facing** package. **Never commit a real customer harness definition here.**
A real harness's definition may be the customer's intellectual property, and an embedded
customer drawing almost certainly is. This repository contains the *format* and **synthetic**
examples using **fictional** part numbers only. Real `.hns` files stay in private systems.

## Contributing

Proposals and defect reports are welcome via
[Issues](https://github.com/EMIP-PAMELA/hns-standard/issues). Please do not attach a real
customer harness or drawing to an issue — describe the shape of the problem instead. See
[GOVERNANCE.md](GOVERNANCE.md) for how changes are decided.

## Contact / stewardship

Apogee Controls stewards this specification. This format is meant to be shaped by the people
who will exchange it — feedback from harness manufacturers and OEMs is actively wanted.

Contact: Matt Robinson, Apogee Controls (matt.robinson@apogeecontrols.com).
