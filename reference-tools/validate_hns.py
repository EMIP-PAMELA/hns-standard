"""
validate_hns.py -- reference conformance validator for the open .hns wire-harness format.

Checks a .hns file against the published contract (see ../spec/SPECIFICATION.md and
../spec/hns-schema-1.json):

  Container
    - the zip's FIRST entry is named 'mimetype', STORED (uncompressed), content exactly
      "application/vnd.emip.harness" (the OPC/EPUB magic-sniff convention);
    - manifest.json has format "emip-harness/1", an integer schemaVersion, and a `graph`;
    - meta.json carries the required provenance fields, and meta.graphSha256 RECOMPUTES from
      manifest.graph (canonical JSON -> sha256);
    - each meta.drawings[] entry points at a real STORED zip entry whose bytes recompute to
      that entry's own sha256/sizeBytes;
    - enrichment.json, if present, is never topology (must not carry nodes/segments/wires);
    - a missing README.txt is a WARNING, not a failure (the spec says SHOULD, not MUST).

  Harness graph (topology invariants a JSON Schema alone can't express -- see SPECIFICATION.md
  section "Structural validity rules"):
    - exactly one root; segments form a fully-connected tree (N nodes -> N-1 segments);
    - every connector pin referenced is in range and never double-booked;
    - a wire's path steps each have a declared segment (or a single-node same-connector loop);
    - a wire's cut length ties to the sum of its path's segment lengths (+/-1.0in per hop).

Stdlib only (zipfile / json / hashlib / re) -- no third-party dependency, no jsonschema
package. The schema file remains the published documentation of field shapes; this script
hand-checks the same contract so a producer can build a conforming file from the spec alone.

Usage:
    python validate_hns.py <file.hns> [<file2.hns> ...]
    python validate_hns.py --selftest      # prove it accepts a good file and rejects
                                            # broken fixtures; touches no files
"""
import hashlib
import io
import json
import re
import sys
import zipfile

MIMETYPE = "application/vnd.emip.harness"
ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
NODE_TYPES = {"connector", "breakout", "splice", "grommet", "terminal", "flying-lead"}
TIE_TOL_PER_SPAN = 1.0  # +/- inches of slack per connection point when tying wire length to path
REQUIRED_META_KEYS = ("partNumber", "rev", "generatedAt", "generatedBy", "source",
                      "graphSha256", "controlled", "provenance")


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def canonical_bytes(obj):
    # Must match the generator byte-for-byte so graphSha256 recomputes: sorted keys, no
    # whitespace, UTF-8, non-ASCII kept verbatim.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def graph_sha256(graph):
    return hashlib.sha256(canonical_bytes(graph)).hexdigest()


class Result:
    """Accumulates errors (hard FAIL) and warnings (non-blocking)."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    @property
    def ok(self):
        return not self.errors


def validate_graph(g):
    """Validate one parsed harness-graph/1 dict. Returns a Result."""
    r = Result()

    if g.get("format") != "harness-graph/1":
        r.err("format must be \"harness-graph/1\", got %r" % (g.get("format"),))
        return r

    nodes = g.get("nodes")
    segments = g.get("segments")
    wires = g.get("wires")
    if not isinstance(nodes, list) or not nodes:
        r.err("nodes must be a non-empty array")
        return r
    if not isinstance(segments, list):
        r.err("segments must be an array")
        return r
    if not isinstance(wires, list) or not wires:
        r.err("wires must be a non-empty array")
        return r

    # ---- nodes ----
    by_id = {}
    for i, n in enumerate(nodes):
        nid = n.get("id")
        if not nid or not ID_RE.match(str(nid)):
            r.err("node[%d]: invalid or missing id %r" % (i, nid))
            continue
        if nid in by_id:
            r.err("node %r: duplicate id" % (nid,))
            continue
        ntype = n.get("type")
        if ntype not in NODE_TYPES:
            r.err("node %r: invalid type %r (must be one of %s)" % (nid, ntype, sorted(NODE_TYPES)))
        if ntype == "connector":
            pins = n.get("pins")
            if not isinstance(pins, int) or pins < 1:
                r.err("node %r: connector requires integer pins >= 1" % (nid,))
        by_id[nid] = n

    if not r.ok:
        return r

    # ---- root ----
    roots = [nid for nid, n in by_id.items() if n.get("root")]
    if len(roots) > 1:
        r.err("multiple nodes marked root: %s (exactly one allowed)" % (roots,))
    elif len(roots) == 0:
        connectors = [nid for nid, n in by_id.items() if n.get("type") == "connector"]
        fallback = connectors[0] if connectors else next(iter(by_id))
        r.warn("no node marked root -- defaulting to %r" % (fallback,))

    # ---- segments form a tree ----
    node_ids = set(by_id.keys())
    edges = []
    seg_key_set = set()
    for i, s in enumerate(segments):
        f, t = s.get("from"), s.get("to")
        if f not in node_ids or t not in node_ids:
            r.err("segment[%d]: from/to must reference declared node ids (got %r -> %r)" % (i, f, t))
            continue
        if f == t:
            r.err("segment[%d]: from == to (%r) -- a segment cannot loop to itself" % (i, f))
            continue
        length_in = s.get("length_in")
        if length_in is not None and not _is_number(length_in):
            r.err("segment[%d] (%s->%s): length_in must be a number if present" % (i, f, t))
        if s.get("dim") == "A+B":
            datum = s.get("datum")
            if datum not in (f, t):
                r.err("segment[%d] (%s->%s): dim=A+B requires datum to be one of its own endpoints" % (i, f, t))
        edges.append((f, t))
        seg_key_set.add(frozenset((f, t)))

    if len(edges) != len(node_ids) - 1:
        r.err("segments must form a tree: %d nodes need exactly %d segments, found %d "
              "(cycle, duplicate segment, or disconnected node likely)"
              % (len(node_ids), len(node_ids) - 1, len(edges)))
    else:
        adj = {nid: [] for nid in node_ids}
        for f, t in edges:
            adj[f].append(t)
            adj[t].append(f)
        start = next(iter(node_ids))
        seen = {start}
        queue = [start]
        while queue:
            cur = queue.pop()
            for nxt in adj[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        if len(seen) != len(node_ids):
            unreached = sorted(node_ids - seen)
            r.err("graph is not fully connected -- unreachable node(s): %s" % (unreached,))

    if not r.ok:
        return r

    # ---- wires ----
    wire_ids = set()
    pin_bookings = {}  # (node_id, pin) -> wire id
    for i, w in enumerate(wires):
        wid = w.get("id")
        label = wid if wid else "wire[%d]" % i
        if not wid:
            r.err("wire[%d]: missing id" % i)
        elif wid in wire_ids:
            r.err("wire %r: duplicate id" % (wid,))
        else:
            wire_ids.add(wid)

        path = w.get("path")
        if not isinstance(path, list) or len(path) < 1:
            r.err("wire %s: path must be a non-empty array of node ids" % (label,))
            continue
        bad_nodes = [p for p in path if p not in node_ids]
        if bad_nodes:
            r.err("wire %s: path references unknown node id(s) %s" % (label, bad_nodes))
            continue

        # A path of length 1 is a same-connector jumper loop (start AND end on one
        # connector, zero hops -- no segment to check). Any longer path keeps the
        # every-hop-has-a-segment rule.
        is_loop = (len(path) == 1)
        if is_loop:
            node = by_id.get(path[0])
            if not node or node.get("type") != "connector":
                r.err("wire %s: single-node path %r only valid when that node is a "
                      "connector (a same-connector jumper loop)" % (label, path[0]))
        else:
            for a, b in zip(path, path[1:]):
                if frozenset((a, b)) not in seg_key_set:
                    r.err("wire %s: path step %s->%s has no declared segment" % (label, a, b))

        length_in = w.get("length_in")
        if not _is_number(length_in):
            r.err("wire %s: length_in must be a number" % (label,))
        elif float(length_in) != int(length_in):
            r.warn("wire %s: length_in %s is not a whole inch -- check for a feet-to-inch artifact"
                   % (label, length_in))

        end_pins = {}
        for end_key, end_pos in (("end1", 0), ("end2", -1)):
            end = w.get(end_key)
            if not isinstance(end, dict) or end.get("node") != path[end_pos]:
                r.err("wire %s: %s.node must equal path[%s] (%r)"
                      % (label, end_key, "0" if end_pos == 0 else "-1", path[end_pos]))
                continue
            node = by_id.get(end["node"])
            pin = end.get("pin")
            if node and node.get("type") == "connector":
                pins = node.get("pins", 0)
                if pin is None:
                    r.err("wire %s: %s at connector %r requires a pin" % (label, end_key, end["node"]))
                else:
                    try:
                        pin_n = int(pin)
                    except (TypeError, ValueError):
                        pin_n = None
                    if pin_n is None or not (1 <= pin_n <= pins):
                        r.err("wire %s: %s pin %r out of range 1..%d on connector %r"
                              % (label, end_key, pin, pins, end["node"]))
                    else:
                        key = (end["node"], pin_n)
                        if key in pin_bookings and pin_bookings[key] != label:
                            r.err("connector %r pin %d double-booked: wires %s and %s"
                                  % (end["node"], pin_n, pin_bookings[key], label))
                        pin_bookings[key] = label
                        end_pins[end_key] = key

        # A same-connector loop must span two DIFFERENT pins (the ordinary double-booking
        # check can't catch a loop claiming one pin at both ends -- same wire, same key).
        if is_loop and "end1" in end_pins and "end2" in end_pins and end_pins["end1"] == end_pins["end2"]:
            r.err("wire %s: same-connector loop must use two DIFFERENT pins (both ends are %r)"
                  % (label, end_pins["end1"]))

        # tie check -- only when every span along the path is dimensioned
        seg_lengths = {}
        for s in segments:
            seg_lengths[frozenset((s["from"], s["to"]))] = s.get("length_in")
        spans = [seg_lengths.get(frozenset((a, b))) for a, b in zip(path, path[1:])]
        if _is_number(length_in) and spans and all(_is_number(x) for x in spans):
            total = sum(spans)
            tol = TIE_TOL_PER_SPAN * len(spans)
            if abs(total - length_in) > tol:
                r.err("wire %s: segment lengths sum to %.2f but wire length_in is %s "
                      "(tolerance +/-%.1f) -- does not tie" % (label, total, length_in, tol))

    # optional confirmation record -- shape-check only when present
    confirmed = g.get("confirmed")
    if confirmed is not None:
        if not isinstance(confirmed, dict):
            r.err("confirmed must be an object with by/at/drawingRev, got %r" % (confirmed,))
        else:
            for key in ("by", "at", "drawingRev"):
                if not confirmed.get(key):
                    r.err("confirmed.%s is required and must be non-empty when confirmed is present" % key)

    hide_picture = g.get("hidePicture")
    if hide_picture is not None and not isinstance(hide_picture, bool):
        r.err("hidePicture must be a boolean, got %r" % (hide_picture,))

    return r


def validate_hns_bytes(data):
    """Validate one .hns file's raw bytes. Returns a Result."""
    r = Result()
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as e:
        r.err("not a valid zip: %s" % e)
        return r

    names = zf.namelist()
    if not names or names[0] != "mimetype":
        r.err("first zip entry must be named 'mimetype' (got %r)" % (names[0] if names else None,))
    else:
        info = zf.getinfo("mimetype")
        if info.compress_type != zipfile.ZIP_STORED:
            r.err("'mimetype' entry must be STORED (uncompressed), got compress_type=%r" % info.compress_type)
        if zf.read("mimetype") != MIMETYPE.encode("ascii"):
            r.err("'mimetype' entry content must be %r" % (MIMETYPE,))

    if "manifest.json" not in names:
        r.err("manifest.json entry missing")
        return r
    try:
        manifest = json.loads(zf.read("manifest.json"))
    except json.JSONDecodeError as e:
        r.err("manifest.json is not valid JSON: %s" % e)
        return r

    if manifest.get("format") != "emip-harness/1":
        r.err("manifest.format must be 'emip-harness/1', got %r" % (manifest.get("format"),))
    if not isinstance(manifest.get("schemaVersion"), int):
        r.err("manifest.schemaVersion must be an integer")
    graph = manifest.get("graph")
    if not isinstance(graph, dict):
        r.err("manifest.graph must be an object")
        graph = None

    if graph is not None:
        gres = validate_graph(graph)
        for e in gres.errors:
            r.err("graph: " + e)
        for w in gres.warnings:
            r.warn("graph: " + w)

    if "meta.json" not in names:
        r.err("meta.json entry missing")
        return r
    try:
        meta = json.loads(zf.read("meta.json"))
    except json.JSONDecodeError as e:
        r.err("meta.json is not valid JSON: %s" % e)
        return r

    for key in REQUIRED_META_KEYS:
        if key not in meta:
            r.err("meta.json missing required key %r" % (key,))
    if meta.get("controlled") is not False:
        r.err("meta.controlled must be exactly false (an export is always uncontrolled in v1)")

    if graph is not None and "graphSha256" in meta:
        recomputed = graph_sha256(graph)
        if recomputed != meta["graphSha256"]:
            r.err("meta.graphSha256 does not recompute: stored=%s recomputed=%s"
                  % (meta["graphSha256"], recomputed))

    if "README.txt" not in names:
        r.warn("README.txt entry missing -- the spec's self-describing requirement (SHOULD) is "
               "unmet, but this is non-fatal (not a MUST)")

    for d in meta.get("drawings") or []:
        arcname = d.get("arcname")
        if not arcname:
            r.err("meta.drawings entry missing arcname: %r" % (d,))
            continue
        if arcname not in names:
            r.err("meta.drawings arcname %r not found as a zip entry" % (arcname,))
            continue
        info = zf.getinfo(arcname)
        if info.compress_type != zipfile.ZIP_STORED:
            r.err("drawing entry %r must be STORED (uncompressed)" % (arcname,))
        dbytes = zf.read(arcname)
        if len(dbytes) != d.get("sizeBytes"):
            r.err("drawing entry %r size mismatch: meta says %r, zip has %d bytes"
                  % (arcname, d.get("sizeBytes"), len(dbytes)))
        if hashlib.sha256(dbytes).hexdigest() != d.get("sha256"):
            r.err("drawing entry %r sha256 does not recompute" % (arcname,))

    if "enrichment.json" in names:
        try:
            enrichment = json.loads(zf.read("enrichment.json"))
        except json.JSONDecodeError as e:
            r.err("enrichment.json is not valid JSON: %s" % e)
            enrichment = None
        if enrichment is not None:
            if enrichment.get("format") != "emip-harness-enrichment/1":
                r.err("enrichment.format must be 'emip-harness-enrichment/1', got %r" % (enrichment.get("format"),))
            for topo_key in ("nodes", "segments", "wires"):
                if topo_key in enrichment:
                    r.err("enrichment.json must never carry topology -- found top-level %r" % (topo_key,))

    return r


# ---- selftest: a hand-built minimal .hns must PASS; broken fixtures must FAIL ----

def _write_hns_bytes(manifest, meta, enrichment=None):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        zf.writestr(zi, MIMETYPE.encode("ascii"))
        zf.writestr("manifest.json", canonical_bytes(manifest))
        zf.writestr("meta.json", canonical_bytes(meta))
        if enrichment:
            zf.writestr("enrichment.json", canonical_bytes(enrichment))
    return buf.getvalue()


def _minimal_graph():
    return {
        "format": "harness-graph/1", "pn": "TEST", "rev": "00",
        "nodes": [
            {"id": "J1", "type": "connector", "root": True, "pins": 2},
            {"id": "T1", "type": "terminal"},
        ],
        "segments": [{"from": "J1", "to": "T1", "length_in": 10.0}],
        "wires": [
            {"id": "W1", "gauge": "18", "color": "RED", "length_in": 10,
             "path": ["J1", "T1"], "end1": {"node": "J1", "pin": "1"}, "end2": {"node": "T1"}},
        ],
    }


def _good_meta(graph):
    return {
        "partNumber": "TEST", "rev": "00", "generatedAt": "2026-01-01T00:00:00Z",
        "generatedBy": "selftest", "source": "TEST", "graphSha256": graph_sha256(graph),
        "controlled": False, "provenance": "selftest fixture",
    }


def _selftest():
    print("--- selftest: .hns validator ---")
    ok = True

    def check(name, data, want_pass):
        nonlocal ok
        res = validate_hns_bytes(data)
        good = res.ok if want_pass else (not res.ok)
        verb = ("correctly PASSED" if res.ok else "WRONGLY REJECTED") if want_pass \
            else ("correctly REJECTED" if not res.ok else "WRONGLY ACCEPTED")
        print("%-26s -> %s" % (name, verb))
        if want_pass and not res.ok:
            for e in res.errors:
                print("        " + e)
        ok = ok and good

    g = _minimal_graph()
    check("valid minimal .hns", _write_hns_bytes({"format": "emip-harness/1", "schemaVersion": 1, "graph": g}, _good_meta(g)), True)

    bad = {"schemaVersion": 1, "graph": g}  # missing manifest.format
    check("missing manifest.format", _write_hns_bytes(bad, _good_meta(g)), False)

    g2 = _minimal_graph(); g2["wires"][0]["end2"]["node"] = "NOPE"
    check("bad wire end reference", _write_hns_bytes({"format": "emip-harness/1", "schemaVersion": 1, "graph": g2}, _good_meta(g2)), False)

    m = _good_meta(g); m["graphSha256"] = "0" * 64
    check("tampered graph (hash)", _write_hns_bytes({"format": "emip-harness/1", "schemaVersion": 1, "graph": g}, m), False)

    print("\nselftest " + ("OK" if ok else "FAILED"))
    sys.exit(0 if ok else 1)


def main():
    args = sys.argv[1:]
    if args == ["--selftest"]:
        _selftest()
        return
    if not args:
        print(__doc__)
        sys.exit(1)

    any_fail = False
    for path in args:
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError as e:
            print("FAIL  %-40s  %s" % (path, e))
            any_fail = True
            continue
        res = validate_hns_bytes(data)
        print("%-4s  %s" % ("PASS" if res.ok else "FAIL", path))
        for e in res.errors:
            print("        ERROR: " + e)
        for w in res.warnings:
            print("        WARN:  " + w)
        any_fail = any_fail or not res.ok

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
