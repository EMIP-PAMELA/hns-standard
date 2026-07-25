# Examples

**Synthetic only.** Every `.hns` file here uses **fictional** part numbers, revisions, and
descriptions. Nothing in this folder is a real customer harness — see the data policy in the
top-level [README](../README.md) and [.gitignore](../.gitignore).

These examples are produced by the EMIP reference generator from a **synthetic** harness
graph, so they demonstrate the exact on-disk format a conforming producer emits. Each example
is meant to be:

- **unzipped and read** (plain JSON + a `README.txt` inside),
- **validated** with the reference validator against `../spec/hns-schema-1.json`,
- **opened** in the reference viewer, and
- **handed to an AI assistant** cold, to confirm it is understandable with no other context.

## `HNS-DEMO-001.hns`

A synthetic example harness — **not a real product.** Every part number is invented
(the `DEMO-*` prefix). It demonstrates the core of the format in one small file:

- a **plug-to-receptacle** run (`DEMO-PLUG-6P` → `DEMO-RCPT-4P`),
- a **double-crimp ferrule** — two blue wires sharing one plug pin via `DEMO-FERRULE-2W`, and
- a **loose ground lead** to a ring terminal.

Try it four ways:

1. **Unzip and read it** — `HNS-DEMO-001.hns` is a ZIP. Inside: `manifest.json` (the harness
   graph), `meta.json` (provenance + content hash), and a plain-English `README.txt`.
2. **Validate it** against [`../spec/hns-schema-1.json`](../spec/hns-schema-1.json).
3. **Open it in a viewer** — [`HNS-DEMO-001.hns.html`](HNS-DEMO-001.hns.html) is a
   self-contained viewer for this example: double-click it and it opens in any browser (no
   install, no network) showing the embedded drawing(s), a pin-to-pin chart, and a wire list.
   It shows customer/vendor part numbers only and does **not** draw an auto-generated
   schematic — it presents the real, trusted data.
4. **Hand it to an AI assistant** with no other context and ask it to explain or render the
   harness — the file is self-describing enough to work cold.
