# Governance

## Stewardship

Apogee Controls stewards the `.hns` specification during its early life. The goal is a format
that trading partners can rely on and implement freely — not a proprietary asset.

**Commitment to neutral stewardship.** At **three independent implementing organizations**,
Apogee will propose moving stewardship to a working group with one seat per implementer, and
will not retain a veto.

## If Apogee stops maintaining this

If Apogee ceases to maintain this specification, the specification text and the reference
implementation remain available under their existing licenses (CC BY 4.0 and MIT
respectively), and **any party may fork and continue the work under a different name**.
Apogee will not assert trademark over the technical content of such a fork.

## Intellectual property

**Patent non-assertion.** Apogee Controls will not assert any patent it holds that is
necessarily infringed by implementing this specification, against any conforming
implementation of it.

The specification text is CC BY 4.0 ([LICENSE-SPEC](LICENSE-SPEC)); the reference
implementation is MIT ([LICENSE](LICENSE)).

## Versioning policy

- **Additive changes** (new optional fields, new container entries) do not bump the major
  version and must not break existing readers. Readers must ignore unknown fields and unknown
  enum values without erroring; editors must preserve them on round-trip.
- **Breaking changes** (removing or renaming a field, changing meaning, changing
  canonicalization) bump the major version, with the reason recorded in `CHANGELOG.md`.
- Non-standardized data belongs in an entity's `ext` object until it is proven and promoted.

## Deprecation policy

A field is marked **deprecated in the specification for at least one full version before
removal**. A published version is never withdrawn: files that validate against it remain
valid, and the schema for it stays available.

## Proposing a change

Open an [issue](https://github.com/EMIP-PAMELA/hns-standard/issues) describing the harness
modeling need and, where possible, a **synthetic** example. **Please do not attach a real
customer harness definition or drawing** — describe the shape of the problem instead.

Schema changes are proposed as pull requests updating **both** `spec/SPECIFICATION.md` and
`spec/hns-schema-1.json`, plus a synthetic example exercising the change. Backwards
compatibility is the default expectation; a breaking proposal must justify the version bump.

**Response commitment.** Proposals are reviewed by the specification maintainer (currently
Apogee Controls engineering). Every proposal receives a substantive response **within 30
days**: accepted, deferred with a reason, or declined with a reason.

## Compatibility promise

A file that validates against a published version will remain readable by conforming tools
built for that version. We will not silently change what a version means.

**This promise begins at 1.0.** The current draft is published to invite feedback before
anything is frozen, and field names may still change in response to it — see
[SPECIFICATION §8.1](spec/SPECIFICATION.md) for the areas still open.
