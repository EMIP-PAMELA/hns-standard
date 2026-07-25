# Reference tools

Reference implementations that make the format immediately usable. Licensed MIT (see the
top-level [LICENSE](../LICENSE)) so anyone can build on them.

- **Viewer** — [`../docs/index.html`](../docs/index.html) is a single self-contained HTML
  page: open any `.hns` (drag-drop or browse) and it renders in your browser — no install, no
  upload, no network. It reads the `.hns` ZIP client-side and shows the embedded drawing(s), a
  pin-to-pin chart, and a wire list. It shows customer/vendor part numbers only and does not
  draw an auto-generated schematic. Lives under `docs/` so it can also be served as a hosted
  page (GitHub Pages) — one link, no download.
- **Validator** — [`validate_hns.py`](validate_hns.py) checks a `.hns` against the published
  contract: container layout (`mimetype` first/STORED, `manifest.json`/`meta.json` present),
  the harness-graph topology invariants (one root, segments form a tree, no double-booked pin,
  wire length ties to its path), `graphSha256` integrity, and each embedded drawing's
  size/hash. Python **stdlib only** — no `pip install`, no `jsonschema` package.

  ```
  python validate_hns.py path/to/file.hns      # validate one (or several) .hns files
  python validate_hns.py --selftest            # prove it accepts a good file, rejects broken ones
  ```

Because a `.hns` is plain JSON in a ZIP, these tools are conveniences, not requirements — the
format is fully usable by reading the specification and building your own.
