# `.hns` — Open Wire-Harness Interchange Format

*An open format for exchanging wire-harness definitions between companies — carrying the
**meaning** of a harness (every connector, wire, pin, length, termination) as structured
data, not a picture of it.*

**Status: draft, published for feedback.** Field names and required fields may still change.
Stewarded by Apogee Controls.

**Try it in 30 seconds:** [open the viewer](https://emip-pamela.github.io/hns-standard/) and
click **"Load the example harness"** — or drag in any `.hns` of your own. Nothing is
uploaded; it runs entirely in your browser.

**Who uses it:** Apogee Controls produces `.hns` from its own engineering system today.
There is no second implementer yet — that is exactly what this repository is for.

---

## The problem

A harness is designed by one company and built by another. The definition is handed over as
a **drawing** — a PDF, usually emailed, sometimes with a spreadsheet beside it.

So the receiving shop reads that drawing and types it back in. Every wire, every pin, every
length, every termination, into their own system. Then they draw their own version of it and
send it back so the customer can confirm they read it right. That confirmation round-trip
exists for one reason: **there was no way to send the meaning, only a picture of it.**

Three things follow, and all of them cost real money:

- **Re-keying is where errors enter.** One drawing can carry thirty or more part numbers.
  Every one is transcribed by hand, by someone reading a dimension off a printout.
- **A picture cannot be checked.** A released drawing can name a wire's colour one way in the
  from-column and a different way in the to-column, and nothing anywhere objects. It can
  double-book a connector position. It can dimension a length that doesn't match the sum of
  its own segments. These sit in circulation for years because no tool can read a PDF well
  enough to disagree with it.
- **The round-trip is pure overhead.** Redrawing someone else's harness to prove you
  understood it adds weeks and produces nothing that didn't already exist.

## What a `.hns` does about it

It carries the definition itself, so there is nothing to re-key and nothing to re-interpret.
The original drawing can ride along inside the same file, so nobody loses the controlling
document.

And because the harness is data rather than a picture, **it can be checked.** A `.hns` with a
double-booked position, a wire whose length disagrees with its own path, or an end that
references a connector that isn't there does not validate. You cannot send an
internally-inconsistent harness without being told. That is the part a PDF can never do, and
it is the whole point.

## Why not just send a spreadsheet?

Because a spreadsheet has no shape. Every shop's columns differ, so each trading pair
negotiates a layout and writes a one-off importer for it. Nothing detects a pin used twice or
a length that doesn't add up. The drawing travels separately and drifts out of sync. And
there is no way to prove the file you received is the file that was sent.

A `.hns` fixes the shape, carries the drawing inside it, validates against published rules,
and hashes its own contents. It is still just a ZIP of plain JSON you can unzip and read.

## How this relates to KBL

**This is not a competitor to KBL, and it is not an argument that KBL got anything wrong.**
It fills a niche KBL was never aimed at.

KBL (VDA 4964) and VEC (VDA 4968) are the automotive harness standards, and they are
genuinely open — the XSDs are MIT-licensed and the full model documentation is CC BY 4.0,
free from [prostep ivip](https://ecad-wiki.prostep.org/). No paywall, nothing to route
around.

**KBL models more than this does, and most of that is vehicle-specific.** 3D routing with
B-spline centre curves, bundle cross-sections, fixing orientation in space, modules and
variants and option codes, component boxes, fuses. That richness exists because a KBL file is
produced *by harness CAD* — the geometry is a by-product of designing the harness in 3D
against a vehicle body.

Which is exactly why it doesn't reach this tier:

- **Neither side has the tooling, or the data.** KBL is native to Capital and E3.series. An
  HVAC or appliance OEM drawing its wiring in Creo Schematics or AutoCAD has no KBL export
  and no 3D harness model to export *from*. Its supplier has no importer. Sending that
  customer a KBL file hands them something they cannot open — the same problem as a PDF, with
  a less familiar extension.
- **Most of the model would sit empty.** A three-wire lead assembly uses roughly a dozen of
  KBL's 104 types. You would be carrying the machinery for a vehicle wiring system to ship a
  furnace harness, and leaving the fields that justify that machinery blank.
- **The implementation doesn't fit the shop.** Every concept is split into a catalog `Part`
  and an instance `Occurrence`, wired together by `IDREF`. Reading a single wire means
  resolving `Connection → Extremity → Contact_point → Cavity_occurrence → Cavity`. That is
  the right design at vehicle scale. It is also weeks of work for a company whose software
  team is one person, if it has one.
- **And it would not hand you interoperability anyway.** KBL declares `Length_type`,
  `Wire_colour_type`, `Terminal_type` and `Tolerance_type` as unconstrained strings — the
  permitted values live in reference data, not in the schema. Two parties adopting KBL still
  have to agree bilaterally on what goes in those fields. That agreement is most of the real
  work, and writing it down is what this format actually contributes.

So the bar here is not *"richer than KBL."* It is **"better than a PDF, and implementable in
an afternoon by one developer with nothing but the standard library."**

Where the two overlap, this format deliberately borrows KBL's structure — typed lengths,
string cavity identifiers, party-scoped part numbers, features located along a span — rather
than inventing alternatives to it. A field-by-field mapping to KBL 2.5 is planned, so a shop
that later moves up to harness CAD has a path rather than a migration.

**If you already exchange KBL with your customers, keep doing that.** This is for the far
larger number of shops who exchange PDFs.

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

## Two forms of the same harness

A producer can hand you either of these. They carry identical data — the difference is only
whether a reader is bundled with it.

| | `harness.hns` | `harness.hns.html` |
|---|---|---|
| **What it is** | The interchange file: a ZIP of plain JSON | The same harness with a viewer baked in |
| **Opening it** | Any `.hns` viewer, your own tools, or just unzip it | Double-click — opens in any browser |
| **Recipient needs** | To know what a `.hns` is | Nothing at all |
| **Machine-readable** | Yes — this is the one to build against | Not intended for ingest |
| **Size** | Small | Larger (carries the viewer) |
| **Works offline** | Yes | Yes — no network, no install, nothing to trust |

Both are in [`examples/`](examples/): [`HNS-DEMO-001.hns`](examples/HNS-DEMO-001.hns) and
[`HNS-DEMO-001.hns.html`](examples/HNS-DEMO-001.hns.html) (13 KB, entirely self-contained).

**Send the `.hns.html` when the recipient has never heard of this format** — it needs no
explanation and no software. **Send the `.hns` when they intend to consume the data.**

> **Emailing the `.hns.html`?** Zip it first. Some mail and chat clients try to preview an
> HTML attachment inline, fail, and show a blank white page — the file is fine, but the
> recipient concludes it's broken. Zipping forces a download. Sending a link to a hosted
> viewer avoids the problem entirely.

## How to read a `.hns`

1. **The hosted viewer** — [emip-pamela.github.io/hns-standard](https://emip-pamela.github.io/hns-standard/).
   Drop in any `.hns` and it renders in your browser: embedded drawings, pin-to-pin chart,
   wire list. No install, no upload, no network round-trip.
2. **Unzip it** — it's a ZIP of plain JSON with a `README.txt` inside. No tools required.
3. **Your own tools** — build to [`spec/hns-schema-1.json`](spec/hns-schema-1.json) and
   ingest directly. Check a file with
   [`reference-tools/validate_hns.py`](reference-tools/validate_hns.py) (Python stdlib only).
4. **Hand it to an AI assistant** — with no schema, no documentation, and no other context.
   Ask it what's on pin 3 of J1, or to turn the harness into a cut list. It works because
   every `.hns` carries a plain-text `README.txt` that describes that specific file's own
   structure, and because the JSON uses descriptive field names rather than codes — so the
   file explains itself to whatever opens it. This is a consequence of the design being
   small, flat and self-describing, not a feature bolted on afterwards.

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
