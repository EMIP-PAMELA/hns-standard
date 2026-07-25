# `.hns` Wire-Harness Interchange Format — Specification

**Version:** 0.1 (pre-release draft) · **Format identifier:** `emip-harness/1` ·
**Media type:** `application/vnd.emip.harness` · **License:** CC BY 4.0

> This is the human-readable specification. The normative, machine-validatable contract is
> [`hns-schema-1.json`](hns-schema-1.json) (JSON Schema). Where the two differ, the JSON
> Schema governs the exact field list; this document explains intent and structure.

## 1. Overview

A `.hns` file describes a **wire harness** completely enough that a receiver never has to
interpret a drawing. It is a **ZIP archive** with a fixed internal layout, holding plain
JSON. The extension `.hns` plus the `mimetype` entry make it a first-class file type (the
same technique used by `.docx`, `.epub`, and `.3mf`, which are all ZIP archives).

## 2. Container layout

```
example.hns  (ZIP)
├── mimetype          Literal "application/vnd.emip.harness". First entry, stored
│                     uncompressed, so the type is identifiable without full unzip.
├── manifest.json     The harness definition (see §3).
├── meta.json         Part identity, revision, provenance, integrity hash (see §4).
├── README.txt        Plain-English description of THIS file + a pointer to this spec, so a
│                     person or an AI can understand the file with no other context (§6).
├── enrichment.json   OPTIONAL. View-only helpers (e.g. wire-color hints). Never changes
│                     the harness meaning.
└── (reserved)        Future, additive: CAD/DXF export, artwork, digital signature. Adding
                      these does not break readers of this version.
```

A conforming reader MUST ignore container entries it does not recognize, and MUST NOT treat
their presence as an error.

## 3. `manifest.json` — the harness

```jsonc
{
  "format": "emip-harness/1",
  "schemaVersion": 1,
  "graph": { "nodes": [...], "segments": [...], "wires": [...], "rev": "..." }
}
```

The `graph` is a topology model:

- **nodes** — the physical endpoints and junctions: `connector`, `terminal`, `splice`,
  `flying-lead`, `breakout`, `grommet`. A connector carries its pin count and part identity;
  a splice carries its ferrule/joint identity; a terminal carries its termination style.
- **segments** — the physical runs between nodes, each with a length (and, where a drawing
  splits a run at a landmark, an A/B dimension with a datum).
- **wires** — each conductor: gauge, color, cut length, the ordered `path` of nodes it
  traverses, and both ends (`end1`/`end2`) giving the node, pin, and termination at each end.

This is deliberately a *graph*, not a picture: the same data can be rendered as a schematic,
a pin-to-pin table, a flat wire list, or a formboard layout. See the JSON Schema for the
exact field names and required fields.

## 4. `meta.json` — identity, provenance, integrity

Carries: `partNumber`, `rev`, `title`, `customer`, generation info (`generatedAt`,
`generatedBy`, `source`), a `controlled` flag, a human `provenance` string, and
**`graphSha256`** — the SHA-256 of the canonicalized `graph` (sorted keys, no insignificant
whitespace). A reader can recompute this to verify the harness definition is intact and
unaltered. Cryptographic *signing* (proving issuer identity) is a future, optional addition.

## 5. Versioning & compatibility

- `format` and `schemaVersion` identify the contract. `schemaVersion` increments **only** on
  a breaking change.
- **Additive by default.** New fields may be introduced without a breaking bump.
- **Unknown-field preservation (normative):** a reader MUST preserve fields and container
  entries it does not understand rather than dropping them. This is what lets one party
  enrich a file that another party's tool round-trips without loss.
- Any entity MAY carry an `ext` object for non-standardized data; fields proven useful there
  are promoted into a later schema version.

## 6. Self-describing requirement (why "just ask an AI" works)

The format is designed so a file is understandable with **zero external tooling or context**:

- Data is plain, human-readable JSON with descriptive field names — not opaque codes.
- Every `.hns` contains a `README.txt` stating what the file is and pointing to this spec.
- Consequently, a person can unzip and read it, a developer can build to the schema, and an
  AI assistant can be handed the file cold and asked to explain, render, or convert it.

A conforming producer SHOULD include `README.txt`. A conforming file SHOULD be interpretable
by a competent reader (human or machine) without access to any resource outside the file
itself, except this publicly published specification.

## 7. Structural validity rules (topology invariants)

Passing JSON Schema validation is **necessary but not sufficient**. A schema can check field
*shapes* (this is a string, that is an integer) but not graph-theory relationships between
them, so a `manifest.graph` MUST also satisfy every rule below to be a valid `emip-harness/1`
harness. These are the same rules the reference validator enforces — published here in full
so an independent producer or consumer can implement them without reading any implementation
source.

- **Node identity.** Every node `id` matches `^[A-Za-z0-9_-]+$` and is unique within the
  graph. Every node's `type` is one of `connector`, `breakout`, `splice`, `grommet`,
  `terminal`, `flying-lead`. A `connector` node MUST declare an integer `pins >= 1`.
- **Exactly one root.** At most one node may be marked `root: true`; more than one is an
  error. Zero is tolerated by the reference implementation (it warns and defaults to the
  first connector) but a conforming producer SHOULD always mark exactly one.
- **Segments form a tree.** The number of `segments` MUST equal `(number of nodes − 1)`. No
  segment may have `from == to` (a segment cannot loop to itself). Every node MUST be
  reachable from every other node by walking segments (no disconnected node, and — combined
  with the exact edge count above — no cycle either).
- **`dim: "A+B"` requires a matching datum.** When a segment carries `"dim": "A+B"`, its
  `datum` field MUST equal one of that segment's own two endpoints (`from` or `to`).
- **Wire identity.** Every wire `id` is present and unique within the graph.
- **A wire's `path` must be walkable.** `path` is a non-empty ordered list of node ids. For
  every consecutive pair in `path`, a segment connecting them MUST exist in `segments` — with
  one exception: a **path of length 1** (a same-connector jumper wire, both ends on one
  housing) is valid only when that single node's `type` is `connector`.
- **A same-connector loop must use two different pins.** For a length-1 `path`, `end1.pin`
  and `end2.pin` on that connector MUST NOT be the same pin.
- **Wire ends must match their path's own endpoints.** `end1.node` MUST equal `path[0]`;
  `end2.node` MUST equal `path[-1]`.
- **Pin assignment and no double-booking.** When a wire end lands on a `connector` node, it
  MUST declare a `pin`, and that pin number MUST be within `1..connector.pins`. No two wires
  may claim the same `(connector node, pin)` pair.
- **Length ties to the path.** `length_in` MUST be a number. When every segment span along a
  wire's `path` carries a declared `length_in`, the sum of those spans MUST equal the wire's
  own `length_in` within a tolerance of **±1.0 inch per hop** (the reference implementation's
  `TIE_TOL_PER_SPAN`, sized to absorb per-connection-point slack — a wire with a 3-segment
  path may differ from the summed segment lengths by up to ±3.0 inches before this is an
  error). A `length_in` that is not a whole number of inches is a non-fatal warning (a likely
  feet→inches conversion artifact), not an error.

A `manifest.graph` that satisfies every rule above is **structurally valid**; one that
violates any of them is not a conforming file regardless of what the JSON Schema alone would
accept.

## 8. Conformance

- A **conforming file** is a ZIP with the `mimetype` entry, a `manifest.json` validating
  against [`hns-schema-1.json#/definitions/manifest`](hns-schema-1.json) **and** every
  structural rule in §7, and a `meta.json` validating against
  `hns-schema-1.json#/definitions/meta` whose `graphSha256` matches its `graph`.
- A **conforming reader** validates against those definitions and §7's structural rules,
  verifies the hash, and preserves unknown fields.
- A **conforming producer** emits the above and SHOULD include `README.txt`.

> **Validating with off-the-shelf tools.** The schema's *root* object describes the whole
> container as a single combined document `{mimetype, manifest, meta, enrichment}` — a
> validation convenience that exists nowhere on disk. Validating `manifest.json` against the
> schema root will fail. Point your validator at the specific definition instead:
>
> ```
> jsonschema -i manifest.json --ref hns-schema-1.json '#/definitions/manifest'
> ```
>
> Or assemble the combined document first:
>
> ```json
> { "mimetype": "application/vnd.emip.harness",
>   "manifest": <contents of manifest.json>,
>   "meta":     <contents of meta.json> }
> ```

### 8.1 Open items

Stated plainly so an implementer is not surprised. These are the areas still being worked
out, and feedback on any of them is welcome.

- **Number formatting in the hash.** The canonicalization rule above does not constrain how
  numbers are written, so a producer emitting `18.0` and one emitting `18` for the same value
  compute different digests. Implementations in languages with a single numeric type may
  therefore disagree with one that distinguishes integers from floats. Pin your number
  formatting explicitly. Adopting a formal canonicalization scheme (RFC 8785) is the
  intended fix.
- **Length datum.** `length_in` does not state whether it is a cut length or a length
  measured with terminals fully seated. These differ by the seating depth on every
  conductor. Producers and consumers must agree until the format carries the distinction
  explicitly.
- **Position identifiers are integers**, so lettered cavities (`A1`) cannot be expressed.
- **Colour is free text** — no controlled vocabulary, and base/stripe ordering is undefined.
- **Segments have no identifier**, so nothing can be located along a span. This is what
  prevents the format from carrying tie placement, sleeving, or bundle diameter.
- **The tree rule in §7 can force a misleading route.** Because a wire's `path` is a walk
  over nodes, a conductor that does not enter the bundle — a short jumper between two
  adjacent terminations, say — must still be described as passing through intervening nodes.
