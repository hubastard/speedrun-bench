#!/usr/bin/env python3
"""The benchmarks' results: every full run of a benchmark, kept in results/history.jsonl, and
the pages made from it.

  ./results.py record SUITE PLATFORM TOOL [options]
      Adds one run of TOOL to the history, then writes results/*.md again. The benchmarks'
      scripts call it after a full run (a run of some flows only records nothing). SUITE: app,
      flutter, compose, journey, web-todomvc, web-rwa. PLATFORM: android, ios, or the browser (chrome,
      electron, firefox).
  ./results.py render
      Writes results/*.md again from the history.
  ./results.py readme [FILE...]
      Writes the tables between <!-- results:NAME --> and <!-- /results:NAME --> in each FILE
      again, from the latest runs: by default Speedrun's README (../README.md) and the
      benchmarks' own. Done when Speedrun ships a version, never by a benchmark run.
  ./results.py import FILE
      Adds the runs of another history (a CI job's, such as the Linux web benchmark's) that this
      one lacks, then writes results/*.md again.
  ./results.py app-table PLATFORM RESULTS_DIR
      Speedrun Bench's table for the run in RESULTS_DIR (app/bench.sh prints it after each run).
  ./results.py ci ARTIFACTS --commit SHA --subject TEXT
      CI (Speedrun's journey workflow, after a push to main): records the journey's and the web
      flows' runs found in the downloaded artifacts. With --history and --out, CI keeps that
      history apart: a branch of its own (bench-history), with its pages.

BENCH_RESULTS=<folder> keeps the history and the pages there instead of results/ (to try a
change out). Python 3.9 and its standard library only: macOS's own python3 runs it.
"""
import argparse
import datetime
import glob
import json
import os
import re
import shlex
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET

BENCH = os.path.dirname(os.path.abspath(__file__))
# BENCH_RESULTS=<folder>: the history and pages there instead (to try a change out).
RESULTS = os.environ.get("BENCH_RESULTS") or os.path.join(BENCH, "results")

SUITES = {
    "app": "Speedrun Bench",
    "flutter": "Flutter Bench",
    "compose": "Compose Bench",
    "journey": "Journey",
    "web-todomvc": "TodoMVC",
    "web-rwa": "Real World App",
    "web-site": "Speedrun's web flows",
}
# Seconds' decimals in tables, and how much slower (at least this many seconds, and CHANGE)
# a time must be to be flagged.
DECIMALS = {"app": 0, "flutter": 1, "compose": 1, "journey": 1, "web-todomvc": 2, "web-rwa": 2, "web-site": 2}
MIN_CHANGE_S = {"app": 1.0, "flutter": 0.5, "compose": 0.5, "journey": 1.0, "web-todomvc": 0.05, "web-rwa": 0.2, "web-site": 0.2}
CHANGE = 0.15
TOOLS = {
    "speedrun": ("Speedrun", None),
    "maestro": ("Maestro", None),
    "maestro-runner": ("maestro-runner", "https://github.com/devicelab-dev/maestro-runner"),
    "appium": ("Appium", None),
    "argent": ("Argent", "https://github.com/software-mansion/argent"),
    "xcuitest": ("XCUITest", None),
    "playwright": ("Playwright", None),
    "cypress": ("Cypress", None),
}
BROWSERS = {"chrome": "Chrome", "electron": "Electron", "firefox": "Firefox"}
PLATFORMS = {"android": "Android", "ios": "iOS", **BROWSERS}
TREND_RUNS = 8  # columns of the "last runs" tables

GENERATED = "<!-- Written by results.py from history.jsonl: edits here are overwritten. -->"


# ---- the history ------------------------------------------------------------------------
# One JSON object per line, one per run of a tool on a suite:
#   date, source (local, ci), machine, device, suite, platform, tool, version, args,
#   bench (this repository's commit), commit and subject (CI: Speedrun's), wall (s),
#   flows: {name: [[seconds, passed], ...]} (one entry per timed run of the flow),
#   est: {name: seconds} (Maestro: a failed flow's estimated full time), notes: {"short",
#   "long"} (a run the tables describe in words), steps: {name: [[command, ms, passed], ...]}.

def load(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def append(path, rec):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def group(rec):
    """Runs that compare: the same benchmark, tool and settings, on the same machine and device."""
    return (rec["suite"], rec["platform"], rec["tool"], rec.get("source", "local"),
            rec.get("machine", ""), rec.get("device", ""), rec.get("args", ""))


def flow_time(runs):
    """(seconds, passed) of a flow: its one run, or the median of its passed runs."""
    if len(runs) == 1:
        return runs[0][0], bool(runs[0][1])
    ok = [s for s, good in runs if good]
    return (statistics.median(ok) if ok else None), len(ok) == len(runs)


def total(rec, only=None):
    times = [flow_time(r)[0] for n, r in rec["flows"].items() if only is None or n in only]
    return sum(t for t in times if t is not None)


def passed(rec):
    return sum(flow_time(r)[1] for r in rec["flows"].values()), len(rec["flows"])


def runs_of(records, suite, platform=None, tool=None, source="local"):
    return [r for r in records if r["suite"] == suite and (platform is None or r["platform"] == platform)
            and (tool is None or r["tool"] == tool) and r.get("source", "local") == source]


def latest(records, suite, platform, tool, source="local"):
    found = runs_of(records, suite, platform, tool, source)
    return found[-1] if found else None


def previous(records, rec, n=1):
    """The n runs before rec in its group, newest first."""
    same = [r for r in records if group(r) == group(rec)]
    i = next(k for k, r in enumerate(same) if r is rec)
    return list(reversed(same[max(0, i - n):i]))


# ---- formatting ------------------------------------------------------------------------

def secs(t, suite):
    return "–" if t is None else f"{t:.{DECIMALS.get(suite, 1)}f} s"


def tool_label(rec, version=True, link=False):
    name, url = TOOLS.get(rec["tool"], (rec["tool"], None))
    if link and url:
        name = f"[{name}]({url})"
    v = rec.get("version", "")
    if version and v and rec["tool"] not in ("speedrun", "xcuitest"):
        name += f" {v}"
    return name


def day(rec):
    return rec["date"][:10]


def change(t, before, suite):
    """▲ +23% when t is slower than before by CHANGE and MIN_CHANGE_S, ▼ −18% when faster."""
    if t is None or not before:
        return ""
    d = t - before
    if abs(d) < MIN_CHANGE_S.get(suite, 1.0) or abs(d) < CHANGE * before:
        return ""
    return f"▲ +{d / before:.0%}" if d > 0 else f"▼ −{-d / before:.0%}"


def table(header, rows, right=None):
    right = right or []
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---:" if i in right else "---" for i in range(len(header))) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def when(rec):
    s = f"{tool_label(rec)}, {day(rec)}"
    if rec["tool"] == "speedrun" and rec.get("version"):
        s = f"Speedrun {rec['version']}, {day(rec)}"
    if rec.get("args"):
        s += f" (`{rec['args']}`)"
    return s


def where(rec):
    return ", ".join(x for x in (rec.get("machine"), rec.get("device")) if x)


def phrase(rec):
    """'Speedrun v0.4.5 on 2026-11-05 (`--animations off`)', 'Maestro 2.11 on 2026-10-27'"""
    name = f"Speedrun {rec['version']}" if rec["tool"] == "speedrun" and rec.get("version") else tool_label(rec)
    return f"{name} on {day(rec)}" + (f" (`{rec['args']}`)" if rec.get("args") else "")


def and_list(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def dates_phrase(recs):
    """'Speedrun and Argent on 2026-10-29, Appium and Maestro on 2026-10-27': the tools by the
    day of their run, the latest first."""
    days = {}
    for r in recs:
        name = "Speedrun" if r["tool"] == "speedrun" else tool_label(r, version=False)
        names = days.setdefault(day(r), [])
        if name not in names:
            names.append(name)
    return ", ".join(f"{and_list(names)} on {d}" for d, names in sorted(days.items(), reverse=True))


def places(recs):
    machines = list(dict.fromkeys(r.get("machine") for r in recs if r.get("machine")))
    devices = list(dict.fromkeys(r.get("device") for r in recs if r.get("device") and r.get("device") != "headless"))
    return and_list(machines) + (" with " + and_list([f"the {d}" for d in devices]) if devices else "")


# ---- suites of flows: Speedrun Bench, Flutter Bench ---------------------------------------

def suite_table(ours, theirs, suite, flows_label="Flow", bold=False):
    """Speedrun against another tool (Maestro), flow by flow, as app/bench.sh prints it."""
    other = tool_label(theirs, version=False) if theirs else None
    header = [flows_label, "Speedrun"] + ([other, "Speedup"] if theirs else [])
    names = sorted(set(ours["flows"] if ours else []) | set(theirs["flows"] if theirs else []))
    est = (theirs or {}).get("est", {})

    def cell(rec, n, estimate=None):
        if not rec or n not in rec["flows"]:
            return "–"
        t, ok = flow_time(rec["flows"][n])
        return secs(t, suite) + ("" if ok else " ✗") + (f" (~{estimate:.0f} s)" if estimate else "")

    rows = []
    for n in names:
        row = [n, cell(ours, n)]
        if theirs:
            speed = ""
            a = flow_time(ours["flows"][n]) if ours and n in ours["flows"] else None
            b = flow_time(theirs["flows"][n]) if n in theirs["flows"] else None
            e = est.get(n) if a and a[1] and b and not b[1] else None
            if a and b and a[0] and a[1]:
                if b[1]:
                    speed = f"{b[0] / a[0]:.1f}x"
                elif e:
                    speed = f"~{e / a[0]:.1f}x"
            row += [cell(theirs, n, e), speed]
        rows.append(row)
    b = (lambda s: f"**{s}**") if bold or theirs else (lambda s: s)
    if ours and theirs:
        ta, tb = total(ours), total(theirs)
        rows.append([b("All flows"), b(f"{ta:.0f} s"), b(f"{tb:.0f} s"), b(f"{tb / ta:.1f}x") if ta else ""])
        both = [n for n in names if n in ours["flows"] and n in theirs["flows"]
                and flow_time(ours["flows"][n])[1] and flow_time(theirs["flows"][n])[1]]
        if both and len(both) < len(names):
            ba, bb = total(ours, both), total(theirs, both)
            rows.append([b(f"Flows both passed ({len(both)})"), b(f"{ba:.0f} s"), b(f"{bb:.0f} s"), b(f"{bb / ba:.1f}x")])
        failed = [n for n in theirs["flows"] if not flow_time(theirs["flows"][n])[1]]
        if failed and all(n in est for n in failed if n in ours["flows"] and flow_time(ours["flows"][n])[1]):
            te = sum(est.get(n, flow_time(r)[0] or 0) for n, r in theirs["flows"].items())
            rows.append([b("All flows, Maestro's failures estimated"), b(f"{ta:.0f} s"), b(f"~{te:.0f} s"), b(f"~{te / ta:.1f}x")])
        if ours.get("wall") and theirs.get("wall"):
            rows.append([b("Wall clock"), b(f"{ours['wall']:.0f} s"), b(f"{theirs['wall']:.0f} s"), b(f"{theirs['wall'] / ours['wall']:.1f}x")])
    elif ours:
        rows.append([b("All flows"), b(secs(total(ours), suite))])
        if ours.get("wall"):
            rows.append([b("Wall clock"), b(secs(ours["wall"], suite))])
    return table(header, rows, right=list(range(1, len(header))))


def passed_line(ours, theirs):
    parts = []
    for rec in (ours, theirs):
        if rec:
            p, n = passed(rec)
            parts.append(f"{tool_label(rec, version=False)} {p}/{n}")
    s = "Passed: " + ", ".join(parts) + "."
    if theirs:
        s += " ✗: failed (its time up to the failure); ~: estimated, had Maestro finished the flow."
    else:
        s += " ✗: failed (its time up to the failure)."
    return s


def trend(records, rec, rows_of, label_of, suite, first="Flow"):
    """Speedrun's last runs like rec (same machine, device and settings), newest first: a
    column per run, a row per flow; ▲/▼ where a run changed from the one before it."""
    runs = [rec] + previous(records, rec, TREND_RUNS - 1)
    header = [first] + [label_of(r) for r in runs]
    rows = []
    for name, get in rows_of(runs):
        row = [name]
        for i, r in enumerate(runs):
            t, ok = get(r)
            before = get(runs[i + 1])[0] if i + 1 < len(runs) else None
            mark = change(t, before, suite) if ok else ""
            row.append(("–" if t is None else secs(t, suite)) + ("" if ok or t is None else " ✗") + (f" {mark}" if mark else ""))
        rows.append(row)
    return table(header, rows, right=list(range(1, len(header))))


def run_label(r):
    v = r.get("version") or ""
    if r.get("commit"):
        v = r["commit"][:7]
    return f"{v}<br>{r['date'][5:16].replace('T', ' ')}" if v else r["date"][5:16].replace("T", " ")


def flow_rows(runs):
    names = sorted({n for r in runs for n in r["flows"]})
    rows = [(n, (lambda n: lambda r: flow_time(r["flows"][n]) if n in r["flows"] else (None, True))(n)) for n in names]
    rows.append(("**All flows**", lambda r: (total(r), all(flow_time(x)[1] for x in r["flows"].values()))))
    rows.append(("**Wall clock**", lambda r: (r.get("wall"), True)))
    return rows


def suite_page(records, suite, platform):
    ours = latest(records, suite, platform, "speedrun")
    theirs = latest(records, suite, platform, "maestro")
    if not ours and not theirs:
        return None
    lines = [f"# {SUITES[suite]} on {PLATFORMS[platform]}", "", GENERATED, "",
             "The latest full run of each tool:", ""]
    for rec in (ours, theirs):
        if rec:
            p, n = passed(rec)
            wall = f", {rec['wall']:.0f} s wall clock" if rec.get("wall") else ""
            lines.append(f"- {when(rec)}: {p}/{n} passed{wall}. {where(rec)}.")
    lines += ["", suite_table(ours, theirs, suite), "", passed_line(ours, theirs)]
    if ours:
        before = previous(records, ours)
        if before:
            lines += ["", f"Against Speedrun's run before ({run_label(before[0]).replace('<br>', ', ')}):", ""]
            lines.append(table(["Flow", "Before", "Now", "Change"], [
                [n, secs(flow_time(before[0]["flows"][n])[0], suite) if n in before[0]["flows"] else "–",
                 secs(flow_time(r)[0], suite) + ("" if flow_time(r)[1] else " ✗"),
                 change(flow_time(r)[0], flow_time(before[0]["flows"][n])[0] if n in before[0]["flows"] else None, suite)]
                for n, r in sorted(ours["flows"].items())], right=[1, 2, 3]))
        lines += ["", "## Speedrun's last runs", "",
                  f"On {where(ours)}{', `' + ours['args'] + '`' if ours.get('args') else ''}, newest first. "
                  f"▲/▼: at least {CHANGE:.0%} (and {MIN_CHANGE_S[suite]:g} s) slower/faster than the run before it.", "",
                  trend(records, ours, flow_rows, run_label, suite)]
    return "\n".join(lines) + "\n"


# ---- runs of a whole command: the journey, the web apps ----------------------------------

def runs_cell(rec, flow, suite, bold=False, details=True, short=False):
    if rec is None:
        return ""
    notes = rec.get("notes")
    if notes:
        return notes["short" if short else "long"]
    runs = rec["flows"][flow]
    t, _ = flow_time(runs)
    ok = sum(1 for _, good in runs if good)
    head = secs(t, suite) if t is not None else "failed"
    if bold and t is not None:
        head = f"**{head}**"
    if not details:
        return head
    each = ", ".join(f"{s:.{DECIMALS.get(suite, 1)}f}" + ("" if good else " ✗") for s, good in runs)
    return f"{head}, {ok}/{len(runs)} passed ({each})"


def journey_page(records, platform):
    recs = [latest(records, "journey", platform, t) for t in TOOLS]
    recs = sorted([r for r in recs if r], key=lambda r: (r["tool"] != "speedrun", flow_time(r["flows"]["Journey"])[0] or 1e9))
    if not recs:
        return None
    lines = [f"# The journey on {PLATFORMS[platform]}", "", GENERATED, "",
             "The latest runs of each tool: the median of its passed runs, the pass count, and each run's time.", ""]
    lines.append(table(["Tool", "Journey", "Version", "Date", "Where"], [
        [("**Speedrun**" if r["tool"] == "speedrun" else tool_label(r, version=False)),
         runs_cell(r, "Journey", "journey", bold=r["tool"] == "speedrun"), r.get("version", ""),
         day(r) + (f" (`{r['args']}`)" if r.get("args") else ""), where(r)] for r in recs]))
    ours = latest(records, "journey", platform, "speedrun")
    if ours:
        hist = [ours] + previous(records, ours, 19)
        lines += ["", "## Speedrun's last runs", "", f"On {where(ours)}, newest first.", ""]
        rows = []
        for i, r in enumerate(hist):
            t = flow_time(r["flows"]["Journey"])[0]
            before = flow_time(hist[i + 1]["flows"]["Journey"])[0] if i + 1 < len(hist) else None
            rows.append([r["date"][:16].replace("T", " "), r.get("version", ""), runs_cell(r, "Journey", "journey"),
                         change(t, before, "journey")])
        lines.append(table(["Date", "Speedrun", "Journey", "Change"], rows))
    return "\n".join(lines) + "\n"


WEB_APPS = [("web-todomvc", "TodoMVC"), ("web-rwa", "Real World App")]


def web_rows(records, machine, browsers):
    """(tool, browser) pairs run on machine, Speedrun first."""
    seen = []
    for r in records:
        if r["suite"] in dict(WEB_APPS) and r.get("machine") == machine and r["platform"] in browsers:
            k = (r["tool"], r["platform"])
            if k not in seen:
                seen.append(k)
    order = ["speedrun", "playwright", "cypress", "maestro"]
    return sorted(seen, key=lambda k: (k[1] == "firefox", order.index(k[0]) if k[0] in order else 99))


def web_latest(records, suite, tool, browser, machine):
    found = [r for r in runs_of(records, suite, browser, tool) if r.get("machine") == machine]
    return found[-1] if found else None


def web_machines(records):
    out = []
    for r in records:
        if r["suite"] in dict(WEB_APPS) and r.get("machine") not in out:
            out.append(r.get("machine"))
    return out


def web_page(records):
    machines = web_machines(records)
    if not machines:
        return None
    lines = ["# The web benchmark", "", GENERATED, "",
             "The latest runs of each tool: the median of its passed runs, the pass count, and each run's time.", ""]
    for m in machines:
        lines += [f"## {m}", ""]
        rows = []
        for tool, browser in web_rows(records, m, list(BROWSERS)):
            row = [f"{tool_label({'tool': tool}, version=False)}, {BROWSERS[browser]}"]
            for suite, flow in WEB_APPS:
                r = web_latest(records, suite, tool, browser, m)
                row.append(f"{runs_cell(r, flow, suite)} · {day(r)}" if r else "")
            rows.append(row)
        lines += [table(["Tool"] + [f for _, f in WEB_APPS], rows), ""]
    return "\n".join(lines)


# ---- the summary --------------------------------------------------------------------------

def summary_page(records):
    lines = ["# Benchmark results", "", GENERATED, "",
             "Every full run of a benchmark adds its times to [`history.jsonl`](history.jsonl) "
             "(`../results.py record`, which the benchmarks' scripts call after a full run), and these "
             "pages are written again from it: the latest run of each tool, and Speedrun's last runs, "
             "so a run that got slower shows. Speedrun's README and the benchmarks' own READMEs take "
             "their numbers from here only when Speedrun ships a version (`../results.py readme`).", ""]
    for suite in ("app", "flutter", "compose"):
        recs = runs_of(records, suite)
        if not recs:
            continue
        platforms = [p for p in ("android", "ios") if runs_of(records, suite, p)]
        links = ", ".join(f"[{PLATFORMS[p]}]({suite}-{p}.md)" for p in platforms)
        lines += [f"## {SUITES[suite]} ({links})", ""]
        rows = []
        for tool in TOOLS:
            cells = []
            for p in platforms:
                r = latest(records, suite, p, tool)
                if r:
                    ok, n = passed(r)
                    t = secs(total(r), suite)
                    cells.append(f"{'**' + t + '**' if tool == 'speedrun' else t}, {ok}/{n} passed · {day(r)}")
                else:
                    cells.append("")
            if any(cells):
                rows.append([("**Speedrun**" if tool == "speedrun" else tool_label(latest_any(records, suite, tool)))] + cells)
        lines += [table(["Tool, all flows"] + [PLATFORMS[p] for p in platforms], rows), ""]
        s = speedup_line(records, suite, platforms)
        if s:
            lines += [s, ""]
    for platform_set in (("android", "ios"),):
        if runs_of(records, "journey"):
            links = ", ".join(f"[{PLATFORMS[p]}](journey-{p}.md)" for p in platform_set if runs_of(records, "journey", p))
            lines += [f"## The journey ({links})", "", journey_block(records, details=False, dates=True), ""]
    if web_machines(records):
        lines += ["## The web ([details](web.md))", ""]
        for m in web_machines(records):
            lines += [f"{m}:", "", web_block(records, m, details=False, dates=True), ""]
    return "\n".join(lines)


def latest_any(records, suite, tool):
    found = runs_of(records, suite, None, tool)
    return found[-1] if found else {"tool": tool}


def speedup_line(records, suite, platforms):
    parts = []
    for p in platforms:
        ours, theirs = latest(records, suite, p, "speedrun"), latest(records, suite, p, "maestro")
        if not ours or not theirs:
            continue
        both = [n for n in ours["flows"] if n in theirs["flows"] and flow_time(ours["flows"][n])[1] and flow_time(theirs["flows"][n])[1]]
        if both:
            parts.append(f"{total(theirs, both) / total(ours, both):.1f}x on {PLATFORMS[p]} ({len(both)} flows)")
    return f"Speedrun's speedup over Maestro on the flows both passed: {', '.join(parts)}." if parts else ""


# ---- README blocks ---------------------------------------------------------------------

def journey_block(records, details=True, dates=False, versions=False, links=False):
    recs = {}
    for p in ("android", "ios"):
        for t in TOOLS:
            r = latest(records, "journey", p, t)
            if r:
                recs[(t, p)] = r
    tools = []
    for (t, p) in recs:
        if t not in tools:
            tools.append(t)

    def key(t):
        # Speedrun first, Maestro last, the others by their Android time, then iOS-only ones.
        a, i = recs.get((t, "android")), recs.get((t, "ios"))
        return (t != "speedrun", t == "maestro", a is None, flow_time((a or i)["flows"]["Journey"])[0] or 1e9)
    rows = []
    for t in sorted(tools, key=key):
        any_rec = recs.get((t, "android")) or recs.get((t, "ios"))
        name = "**Speedrun**" if t == "speedrun" else tool_label(any_rec, version=versions, link=links)
        if t == "argent" and versions:
            name += " (`argent e2e`)"
        cells = []
        for p in ("android", "ios"):
            r = recs.get((t, p))
            if not r:
                cells.append("")
                continue
            c = runs_cell(r, "Journey", "journey", bold=t == "speedrun", details=details)
            if not details:
                runs = r["flows"]["Journey"]
                c += f", {sum(1 for _, g in runs if g)}/{len(runs)} passed"
            if dates:
                c += f" · {day(r)}"
            cells.append(c)
        rows.append([name] + cells)
    return table(["Tool", "Android emulator", "iOS simulator"], rows, right=[] if details else [1, 2])


def web_block(records, machine, details=True, dates=False, versions=False, firefox=True):
    browsers = list(BROWSERS) if firefox else ["chrome", "electron"]
    pairs = web_rows(records, machine, browsers)
    multi = len({b for _, b in pairs if b == "firefox"}) > 0
    rows = []
    for tool, browser in pairs:
        any_rec = next((r for s, _ in WEB_APPS for r in [web_latest(records, s, tool, browser, machine)] if r), {"tool": tool})
        name = "**Speedrun**" if tool == "speedrun" else tool_label(any_rec, version=versions)
        if multi:
            name += f", {BROWSERS[browser]}"
        cells = []
        for suite, flow in WEB_APPS:
            r = web_latest(records, suite, tool, browser, machine)
            if not r:
                cells.append("")
                continue
            if r.get("notes"):
                c = r["notes"]["long" if details else "short"]
            else:
                runs = r["flows"][flow]
                t, _ = flow_time(runs)
                prec = DECIMALS[suite] if details or suite == "web-todomvc" else 1
                head = "failed" if t is None else f"{t:.{prec}f} s"
                if tool == "speedrun" and t is not None:
                    head = f"**{head}**"
                if details:
                    c = head + " (" + ", ".join(f"{s:.{DECIMALS[suite]}f}" + ("" if g else " ✗") for s, g in runs) + ")"
                else:
                    tests = r.get("tests")
                    ok = all(g for _, g in runs)
                    c = head + (", " + (f"{tests}/{tests} passed" if tests and tests > 1 else "passed") if ok else ", failed")
            if dates:
                c += f" · {day(r)}"
            cells.append(c)
        rows.append([name] + cells)
    header = ["Tool", "TodoMVC", "Real World App (7 tests)" if details else "Real World App, 7 tests"]
    return table(header, rows, right=[] if details else [1, 2])


def firefox_sentence(records, machine):
    tools = ["speedrun", "playwright", "cypress"]
    parts = []
    for suite, flow in WEB_APPS:
        ts = []
        for t in tools:
            r = web_latest(records, suite, t, "firefox", machine)
            ts.append(None if not r or r.get("notes") else flow_time(r["flows"][flow])[0])
        if any(x is None for x in ts):
            return None
        parts.append(ts)
    (a1, a2, a3), (b1, b2, b3) = parts
    return (f"TodoMVC took {a1:.1f} s with Speedrun, {a2:.1f} s with Playwright and {a3:.1f} s with "
            f"Cypress, and the Real World App {b1:.1f} s, {b2:.1f} s and {b3:.1f} s")


def app_sentence(records):
    """The README's line on Speedrun Bench against Maestro."""
    flows, pf, speed = {}, [], []
    for p in ("android", "ios"):
        ours, theirs = latest(records, "app", p, "speedrun"), latest(records, "app", p, "maestro")
        if not ours or not theirs:
            return None
        flows[p] = passed(ours)
        tp, tn = passed(theirs)
        pf.append(f"{tp} of {tn} on {PLATFORMS[p]}")
        both = [n for n in ours["flows"] if n in theirs["flows"] and flow_time(ours["flows"][n])[1] and flow_time(theirs["flows"][n])[1]]
        speed.append(f"{total(theirs, both) / total(ours, both):.1f}x")
    (ap, an), (ip, inn) = flows["android"], flows["ios"]
    if ap == an and ip == inn and an == inn:
        ours_s = f"Speedrun passes all {an} of the app's flows on both platforms"
    else:
        ours_s = f"Speedrun passes {ap} of {an} of the app's flows on Android and {ip} of {inn} on iOS"
    return (f"{ours_s}, Maestro {pf[0]} and {pf[1]}. On the flows both pass, Speedrun is "
            f"{speed[0]} faster on Android and {speed[1]} on iOS")


def months(records, suites):
    ms = sorted({r["date"][:7] for r in records if r["suite"] in suites and r.get("source", "local") == "local"
                 and r is latest(records, r["suite"], r["platform"], r["tool"])})
    names = [datetime.date(int(m[:4]), int(m[5:]), 1).strftime("%B %Y") for m in ms]
    if not names:
        return None
    if len(names) == 1:
        return names[0]
    return ", ".join(n.split()[0] for n in names[:-1]) + " and " + names[-1]


def block(records, name):
    """The text of README block NAME."""
    mac = next((m for m in web_machines(records) if m and m.startswith("Apple")), None)
    linux = next((m for m in web_machines(records) if m and not m.startswith("Apple")), None)
    if name == "journey":
        return journey_block(records, details=False, versions=True, links=True)
    if name == "journey-runs":
        recs = [r for p in ("android", "ios") for t in TOOLS for r in [latest(records, "journey", p, t)] if r]
        return (f"{dates_phrase(recs)}; {places(recs)}. The median of the passed runs, the pass "
                f"count, and each run's time in seconds:\n\n" + journey_block(records))
    if name == "web":
        return web_block(records, mac, details=False, versions=True, firefox=False)
    if name in ("web-mac-runs", "web-linux-runs"):
        m = mac if name == "web-mac-runs" else linux
        recs = [r for r in records if r["suite"] in dict(WEB_APPS) and r.get("machine") == m]
        recs = [r for r in recs if r is web_latest(records, r["suite"], r["tool"], r["platform"], m)]
        return f"{places(recs)}: {dates_phrase(recs)}.\n\n" + web_block(records, m, firefox=name == "web-linux-runs")
    if name == "web-firefox":
        return firefox_sentence(records, linux)
    if name == "app-sentence":
        return app_sentence(records)
    if name == "app-flows":
        r = latest(records, "app", "android", "speedrun") or latest(records, "app", "ios", "speedrun")
        return str(len(r["flows"])) if r else None
    if name == "measured-when":
        return months(records, {"journey", "app", "web-todomvc", "web-rwa"})
    m = re.fullmatch(r"(app|flutter)-(android|ios)", name)
    if m:
        suite, p = m.groups()
        ours, theirs = latest(records, suite, p, "speedrun"), latest(records, suite, p, "maestro")
        if not ours and not theirs:
            return None
        head = and_list([phrase(r) for r in (ours, theirs) if r])
        return (f"{head}, on {places([r for r in (ours, theirs) if r])}:\n\n"
                + suite_table(ours, theirs, suite, flows_label=f"Flow ({p})") + "\n\n" + passed_line(ours, theirs))
    if name in ("flutter", "compose"):
        # Speedrun's times, a column per platform (Compose Bench is Android only).
        platforms = ("android", "ios") if name == "flutter" else ("android",)
        recs = {p: latest(records, name, p, "speedrun") for p in platforms}
        if not any(recs.values()):
            return None
        names = sorted({n for r in recs.values() if r for n in r["flows"]})
        rows = []
        for n in names:
            row = [n]
            for p in platforms:
                r = recs[p]
                if r and n in r["flows"]:
                    t, ok = flow_time(r["flows"][n])
                    row.append(secs(t, name) + ("" if ok else " ✗"))
                else:
                    row.append("–")
            rows.append(row)
        rows.append(["**All flows**"] + [f"**{secs(total(recs[p]), name)}**" if recs[p] else "–" for p in platforms])
        lines = [f"- {PLATFORMS[p]}: {phrase(r)}, on {places([r])}." for p, r in recs.items() if r]
        return "\n".join(lines) + "\n\n" + table(["Flow"] + [PLATFORMS[p] for p in platforms], rows,
                                                   right=list(range(1, len(platforms) + 1)))
    raise SystemExit(f"results.py: no block named {name}")


def readme(files, records):
    pat = re.compile(r"(<!-- results:([\w-]+) -->)(.*?)(<!-- /results:\2 -->)", re.S)
    for path in files:
        text = open(path).read()

        def sub(m):
            new = block(records, m[2])
            if new is None:
                print(f"{os.path.normpath(path)}: {m[2]}: no runs recorded, left as it is")
                return m[0]
            inline = "\n" not in m[3]
            return m[1] + (new if inline else "\n" + new + "\n") + m[4]
        out = pat.sub(sub, text)
        if out != text:
            open(path, "w").write(out)
            print(f"{os.path.normpath(path)}: written again")
        else:
            print(f"{os.path.normpath(path)}: unchanged")


def render(records, out):
    os.makedirs(out, exist_ok=True)
    pages = {"README.md": summary_page(records)}
    for suite in ("app", "flutter", "compose"):
        for p in ("android", "ios"):
            pages[f"{suite}-{p}.md"] = suite_page(records, suite, p)
    for p in ("android", "ios"):
        pages[f"journey-{p}.md"] = journey_page(records, p)
    pages["web.md"] = web_page(records)
    for name, text in pages.items():
        if text:
            with open(os.path.join(out, name), "w") as f:
                f.write(text)


# ---- CI: a run of Speedrun on each push to main -------------------------------------------

def ci_page(records):
    """CI's history, a push at a time: a row per commit, a column per benchmark."""
    cols = []
    for r in records:
        k = (r["suite"], r["platform"])
        if k not in cols:
            cols.append(k)
    commits = []
    for r in records:
        if r.get("commit") and r["commit"] not in commits:
            commits.append(r["commit"])
    commits = list(reversed(commits))[:40]
    by = {(r.get("commit"), r["suite"], r["platform"]): r for r in records}
    head = ["Commit", "Date"] + [f"{SUITES[s]}, {PLATFORMS.get(p, p)}" for s, p in cols]
    rows = []
    for c in commits:
        first = next(r for r in records if r.get("commit") == c)
        row = [f"[`{c[:7]}`](https://github.com/hubastard/speedrun/commit/{c}) {first.get('subject', '')[:60]}", first["date"][:16].replace("T", " ")]
        for s, p in cols:
            r = by.get((c, s, p))
            if not r:
                row.append("")
                continue
            t = total(r)
            ok, n = passed(r)
            before = [total(x) for x in previous(records, r, 5) if passed(x)[0] == passed(x)[1]]
            mark = change(t, statistics.median(before), s) if before and ok == n else ""
            row.append(secs(t, s) + ("" if ok == n else f" ✗ {ok}/{n}") + (f" {mark}" if mark else ""))
        rows.append(row)
    lines = ["# Speedrun's CI, push by push", "", GENERATED, "",
             "The journey and the web flows as Speedrun's CI ran them after each push to `main` "
             "(the `Journey` workflow), on GitHub's runners: their times vary more from run to run "
             "than a local machine's. ▲/▼: at least "
             f"{CHANGE:.0%} slower/faster than the median of the 5 runs before. Each benchmark's page "
             "has its flows' or steps' times.", "",
             table(head, rows), ""]
    for s, p in cols:
        lines.append(f"- [{SUITES[s]}, {PLATFORMS.get(p, p)}](ci-{s}-{p}.md)")
    return "\n".join(lines) + "\n", cols


def ci_detail(records, suite, platform):
    recs = [r for r in records if r["suite"] == suite and r["platform"] == platform]
    if not recs:
        return None
    last = recs[-1]
    use_steps = bool(last.get("steps"))
    if use_steps:
        flow = next(iter(last["steps"]))

        def rows_of(runs):
            names = [c[0] for c in last["steps"][flow]]
            out = []
            for i, n in enumerate(names):
                def get(r, i=i, n=n):
                    st = (r.get("steps") or {}).get(flow) or []
                    if i < len(st) and st[i][0] == n:
                        return st[i][1] / 1000, bool(st[i][2])
                    return None, True
                out.append((f"{i + 1}. {n}", get))
            out.append(("**Total**", lambda r: (total(r), all(flow_time(x)[1] for x in r["flows"].values()))))
            return out
    else:
        rows_of = flow_rows
    text = trend(records, last, rows_of, run_label, suite, first="Step" if use_steps else "Flow")
    what = "each step" if use_steps else "each flow"
    return (f"# {SUITES[suite]}, {PLATFORMS.get(platform, platform)}, on Speedrun's CI\n\n{GENERATED}\n\n"
            f"{what[0].upper() + what[1:]}'s time, the last {TREND_RUNS} pushes, newest first ({where(last)}). "
            "▲/▼: at least "
            f"{CHANGE:.0%} slower/faster than the push before.\n\n" + text + "\n")


def ci_render(records, out):
    os.makedirs(out, exist_ok=True)
    page, cols = ci_page(records)
    with open(os.path.join(out, "README.md"), "w") as f:
        f.write(page)
    for s, p in cols:
        text = ci_detail(records, s, p)
        if text:
            with open(os.path.join(out, f"ci-{s}-{p}.md"), "w") as f:
                f.write(text)


def steps_of(commands_json):
    """A flow's top-level commands: [command, ms, passed]. Nested commands start within their
    runFlow / repeat / retry."""
    out, end = [], -1
    for c in json.load(open(commands_json)):
        cmd = next(iter(c["command"]))
        m = c["metadata"]
        if cmd in ("defineVariablesCommand", "applyConfigurationCommand"):
            continue
        ts, ms = m.get("timestamp", 0), m.get("duration") or 0
        if m.get("depth", 0) > 0 or ("depth" not in m and ts < end):
            continue
        desc = next(iter(c["command"].values())).get("description") or cmd
        out.append([desc, ms, m.get("status") == "COMPLETED"])
        if cmd in ("runFlowCommand", "repeatCommand", "retryCommand"):
            end = ts + ms
    return out


def junit_flows(path):
    flows = {}
    for tc in ET.parse(path).getroot().iter("testcase"):
        failed = tc.find("failure") is not None or tc.find("error") is not None
        flows[tc.get("name")] = [[round(float(tc.get("time") or 0), 3), not failed]]
    return flows


def ci_env(args):
    """bench-env.json, next to a CI job's reports: what `ci` records them with."""
    reports = []
    for r in args.report:
        path, suite, platform, *debug = r.split(":")
        reports.append([path, suite, platform, debug[0] if debug else None])
    env = {"date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M"),
           "machine": this_machine(), "version": tool_version("speedrun"), "bench": bench_commit(),
           "device": args.device or (this_device("ios", args.simulator) if args.simulator else ""),
           "reports": reports}
    with open(args.out_file, "w") as f:
        json.dump(env, f, indent=1)
    print(json.dumps(env))


def ci(args):
    """Records each run found in the Journey workflow's artifacts (each job's folder has its
    reports, debug output and bench-env.json)."""
    found = 0
    for env_path in sorted(glob.glob(os.path.join(args.artifacts, "*", "bench-env.json"))):
        d = os.path.dirname(env_path)
        env = json.load(open(env_path))
        for report, suite, platform, debug in env["reports"]:
            path = os.path.join(d, report)
            if not os.path.exists(path):
                continue
            rec = {"date": env.get("date") or now(), "source": "ci", "machine": env["machine"],
                   "device": env.get("device", ""), "suite": suite,
                   "platform": platform, "tool": "speedrun", "version": env.get("version", ""),
                   "args": "", "commit": args.commit, "subject": args.subject,
                   "bench": env.get("bench", ""), "flows": junit_flows(path)}
            if debug:
                steps = {}
                for n in rec["flows"]:
                    for cj in glob.glob(os.path.join(d, debug, "*", "commands.json")):
                        steps[n] = steps_of(cj)
                        break
                if steps:
                    rec["steps"] = steps
            append(args.history, rec)
            found += 1
            print(f"recorded {suite} {platform}: {secs(total(rec), suite)}, {passed(rec)[0]}/{passed(rec)[1]} passed")
    if not found:
        print("results.py ci: no runs found")
        return
    ci_render(load(args.history), args.out)


# ---- recording a run ----------------------------------------------------------------------

def now():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")


def sh(cmd, cwd=None):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return ""


def this_machine():
    if os.environ.get("GITHUB_ACTIONS"):
        image = os.environ.get("ImageOS", "")  # ubuntu24, macos26
        m = re.fullmatch(r"(ubuntu)(\d+)|(macos)(\d+)", image)
        label = (f"ubuntu-{m[2]}.04" if m[1] else f"macos-{m[4]}") if m else (image or sys.platform)
        return f"GitHub Actions {label} runner ({os.cpu_count()} vCPUs)"
    if sys.platform == "darwin":
        cpu = sh(["sysctl", "-n", "machdep.cpu.brand_string"])
        mem = sh(["sysctl", "-n", "hw.memsize"])
        return f"{cpu} ({int(mem) // 2**30} GB)" if mem.isdigit() else cpu
    return sh(["uname", "-sm"])


def this_device(platform, device):
    if platform == "android":
        serial = ["-s", device] if device else []
        avd = sh(["adb", *serial, "emu", "avd", "name"]).splitlines()
        release = sh(["adb", *serial, "shell", "getprop", "ro.build.version.release"])
        name = f"{avd[0].strip()} emulator" if avd and avd[0].strip() and "error" not in avd[0] else sh(["adb", *serial, "shell", "getprop", "ro.product.model"])
        return f"{name} (Android {release})" if release else name
    if platform == "ios":
        try:
            data = json.loads(sh(["xcrun", "simctl", "list", "devices", "-j"]))
            for runtime, devs in data["devices"].items():
                for x in devs:
                    if x["udid"] == device or (not device and x["state"] == "Booted"):
                        v = re.search(r"iOS-(\d+)-(\d+)", runtime)
                        return f"{x['name']} simulator" + (f" (iOS {v[1]}.{v[2]})" if v else "")
        except Exception:
            pass
        return ""
    return "headless"


def tool_version(tool):
    first = lambda s: s.splitlines()[0].strip() if s else ""
    speedrun = os.environ.get("SPEEDRUN") or os.path.join(BENCH, "..", "speedrun")
    if tool == "speedrun":
        return first(sh([speedrun, "--version"])).replace("speedrun ", "")
    if tool == "maestro":
        return first(sh(["maestro", "--version"]))
    if tool == "appium":
        return first(sh([os.path.join(BENCH, "journey/appium/node_modules/.bin/appium"), "--version"]))
    if tool == "argent":
        return first(sh([os.path.join(BENCH, "agents/node_modules/.bin/argent"), "--version"]))
    if tool == "maestro-runner":
        return first(sh([os.environ.get("MAESTRO_RUNNER", os.path.expanduser("~/.maestro-runner/bin/maestro-runner")), "--version"]))
    if tool == "xcuitest":
        return first(sh(["xcodebuild", "-version"]))
    if tool == "playwright":
        return first(sh(["npx", "playwright", "--version"], cwd=os.path.join(BENCH, "web"))).replace("Version ", "")
    if tool == "cypress":
        m = re.search(r"Cypress package version: (\S+)", sh(["npx", "cypress", "--version"], cwd=os.path.join(BENCH, "web")))
        return m[1] if m else ""
    return ""


def bench_commit():
    rev = sh(["git", "rev-parse", "--short", "HEAD"], cwd=BENCH)
    dirty = sh(["git", "status", "--porcelain", "--untracked-files=no"], cwd=BENCH)
    return rev + ("-dirty" if dirty else "")


def app_flows(results, platform, tool):
    """Speedrun Bench's run in RESULTS (app/bench.sh): per-flow times, wall clock, and each
    flow's top-level commands."""
    path = f"{results}/{platform}-{tool}.xml"
    if not os.path.exists(path):
        return None
    rec = {"flows": junit_flows(path)}
    wall = f"{results}/{platform}-{tool}.wall"
    if os.path.exists(wall):
        rec["wall"] = int(open(wall).read().strip()) / 1000
    return rec


def app_steps(results, platform, tool, name, flows_dir):
    """The flow's top-level commands. Maestro names a flow's debug folder after the flow,
    speedrun after its file."""
    stems = {}
    for f in glob.glob(os.path.join(flows_dir, "*.yaml")):
        m = re.search(r"^name: *(.+)$", open(f).read(), re.M)
        if m:
            stems[m[1].strip()] = os.path.basename(f)[:-5]
    for folder in (name, stems.get(name)):
        path = f"{results}/{platform}-{tool}-debug/{folder}/commands.json"
        if folder and os.path.exists(path):
            return [(c[0], "COMPLETED" if c[2] else "FAILED", c[1]) for c in steps_of(path)]
    return None


def maestro_estimates(results, platform, flows_dir):
    """A flow Maestro fails counts its time up to the failure, which says little: it fails some
    flows early, others after waiting out timeouts. Its estimate: Maestro's time up to the
    failing step, plus speedrun's time for the rest of the flow (that step included) at
    Maestro's pace on the flow so far (its time over speedrun's for the same steps; before 5 s
    of them, its pace on the flows both passed)."""
    ours, theirs = app_flows(results, platform, "speedrun"), app_flows(results, platform, "maestro")
    if not ours or not theirs:
        return {}
    o, t = ours["flows"], theirs["flows"]
    both = [n for n in o if n in t and o[n][0][1] and t[n][0][1]]
    pace_all = sum(t[n][0][0] for n in both) / sum(o[n][0][0] for n in both) if both else None
    est = {}
    for n in t:
        if t[n][0][1] or n not in o or not o[n][0][1]:
            continue
        m, s = app_steps(results, platform, "maestro", n, flows_dir), app_steps(results, platform, "speedrun", n, flows_dir)
        if not m or not s:
            continue
        k = next((i for i, c in enumerate(m) if c[1] == "FAILED"), None)
        # The same commands up to the failure, or the runs went different ways.
        if k is None or len(s) <= k or any(m[i][0] != s[i][0] for i in range(k + 1)):
            continue
        m_before, s_before = sum(c[2] for c in m[:k]), sum(c[2] for c in s[:k])
        pace = m_before / s_before if s_before >= 5000 else pace_all
        if pace:
            est[n] = round(t[n][0][0] - sum(c[2] for c in m[k:]) / 1000 + sum(c[2] for c in s[k:]) / 1000 * pace, 1)
    return est


def app_table(platform, results):
    """The table for the run in RESULTS, as app/bench.sh prints it (results/<platform>.md)."""
    flows_dir = os.path.join(BENCH, "app", "flows")
    ours, theirs = app_flows(results, platform, "speedrun"), app_flows(results, platform, "maestro")
    for r, tool in ((ours, "speedrun"), (theirs, "maestro")):
        if r:
            r.update(tool=tool, suite="app", platform=platform)
    if theirs:
        theirs["est"] = maestro_estimates(results, platform, flows_dir)
    out = suite_table(ours, theirs, "app", flows_label=f"Flow ({platform})") + "\n\n" + passed_line(ours, theirs)
    open(os.path.join(results, f"{platform}.md"), "w").write(out + "\n")
    print(out)


def parse_runs(text):
    """'20.8:1 20.1:1 89.4:0' -> [[20.8, True], [20.1, True], [89.4, False]]"""
    out = []
    for item in text.split():
        s, ok = item.split(":")
        out.append([round(float(s), 3), ok == "1"])
    return out


def record(args):
    rec = {"date": now(), "source": "local", "machine": args.machine or this_machine(),
           "device": args.device_name if args.device_name is not None else this_device(args.platform, args.device),
           "suite": args.suite, "platform": args.platform, "tool": args.tool,
           "version": args.version or tool_version(args.tool), "args": args.args.strip(), "bench": bench_commit()}
    if args.results:  # Speedrun Bench and Flutter Bench: app/bench.sh's results folder
        found = app_flows(args.results, args.platform, args.tool)
        if not found:
            raise SystemExit(f"results.py: no {args.platform}-{args.tool}.xml in {args.results}")
        rec.update(found)
        if args.tool == "maestro" and args.suite == "app":
            rec["est"] = maestro_estimates(args.results, args.platform, os.path.join(BENCH, "app", "flows"))
    elif args.runs is not None:
        rec["flows"] = {args.flow: parse_runs(args.runs)}
        if args.tests:
            rec["tests"] = args.tests
    else:
        raise SystemExit("results.py record: --results or --runs")
    append(args.history, rec)
    records = load(args.history)
    render(records, args.out)
    p, n = passed(rec)
    before = previous(records, records[-1])
    vs = ""
    if before and args.suite in ("app", "flutter", "compose"):
        vs = f" (the run before: {secs(total(before[0]), args.suite)}, {passed(before[0])[0]}/{passed(before[0])[1]})"
    out = os.path.abspath(args.out)
    shown = os.path.relpath(out, BENCH) if out.startswith(BENCH + os.sep) else out
    print(f"== recorded {args.suite} {args.platform} {args.tool}: {secs(total(rec), args.suite)}, {p}/{n} passed{vs}; "
          f"its pages written again ({shown}/)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--history", default=os.path.join(RESULTS, "history.jsonl"))
    ap.add_argument("--out", default=RESULTS, help="where the pages go")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("suite", choices=list(SUITES))
    r.add_argument("platform")
    r.add_argument("tool")
    r.add_argument("--results", help="app/bench.sh's results folder (Speedrun Bench, Flutter Bench)")
    r.add_argument("--runs", help="timed runs of the whole command: 'seconds:passed ...' (journey, web)")
    r.add_argument("--flow", default="Journey", help="with --runs: the flow's name")
    r.add_argument("--tests", type=int, help="with --runs: tests in a run (the Real World App's 7)")
    r.add_argument("--device", default="", help="the adb serial or simulator UDID")
    r.add_argument("--device-name", help="the device as the tables say it (else read from the device)")
    r.add_argument("--machine")
    r.add_argument("--version", help="the tool's version (else asked from the tool)")
    r.add_argument("--args", default="", help="the tool's options for the run")
    sub.add_parser("render")
    rd = sub.add_parser("readme")
    rd.add_argument("files", nargs="*")
    im = sub.add_parser("import")
    im.add_argument("file")
    t = sub.add_parser("app-table")
    t.add_argument("platform")
    t.add_argument("results")
    e = sub.add_parser("ci-env")
    e.add_argument("out_file")
    e.add_argument("--report", action="append", default=[], help="FILE:SUITE:PLATFORM[:DEBUG_FOLDER]")
    e.add_argument("--device", default="")
    e.add_argument("--simulator", help="the simulator's UDID (its name and iOS version are read)")
    c = sub.add_parser("ci")
    c.add_argument("artifacts")
    c.add_argument("--commit", required=True)
    c.add_argument("--subject", default="")
    args = ap.parse_args()
    if args.cmd == "record":
        record(args)
    elif args.cmd == "render":
        render(load(args.history), args.out)
    elif args.cmd == "readme":
        files = args.files or [f for f in [os.path.join(BENCH, "..", "README.md")] if os.path.exists(f)] + [
            os.path.join(BENCH, d, "README.md") for d in ("app", "flutter", "compose", "journey", "web")]
        readme(files, load(args.history))
    elif args.cmd == "import":
        have = {json.dumps(r, sort_keys=True) for r in load(args.history)}
        new = [r for r in load(args.file) if json.dumps(r, sort_keys=True) not in have]
        for r in sorted(new, key=lambda r: r["date"]):
            append(args.history, r)
        print(f"{len(new)} runs added")
        render(load(args.history), args.out)
    elif args.cmd == "app-table":
        app_table(args.platform, args.results)
    elif args.cmd == "ci":
        ci(args)
    elif args.cmd == "ci-env":
        ci_env(args)


if __name__ == "__main__":
    main()
