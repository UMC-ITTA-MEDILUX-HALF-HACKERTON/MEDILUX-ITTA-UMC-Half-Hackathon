#!/usr/bin/env python3
"""Validate the document bundle and policy examples, NOT a running product.

Run from the repository root: python3 docs/PM/verification/verify_plan.py
Requires PyYAML. Output is JSON on stdout; no files or external services mutated.
The small models below expose boundary cases for the approved policy only.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import json
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[3]
RESULTS = []


def check(case, expected, actual, feature="documents"):
    RESULTS.append(dict(case=case, feature=feature, expected=expected, actual=actual,
                        status="PASS" if expected == actual else "FAIL"))


def read_yaml(path):
    return yaml.safe_load((ROOT / path).read_text())


def snapshot(path):
    raw = (ROOT / path).read_text()
    _, header, content = raw.split("---", 2)
    return yaml.safe_load(header), content[content.index("\n##"):].strip()


config = read_yaml("docs/start/PROJECT_CONFIG.yaml")
sources = read_yaml("docs/start/SOURCES.yaml")["sources"]
manifest = read_yaml("docs/Plan/BACKUP_MANIFEST.yaml")["entries"]
by_source = {x["source_id"]: x for x in sources}
by_backup = {x["source_id"]: x for x in manifest}
meta, body = snapshot("docs/Plan/MVP.md")
check("DOC-01 product name", "너빼고다옴", config["product_name"])
check("DOC-02 map provider", "kakao_maps_javascript_api", config["technology"]["map_provider"])
check("DOC-03 Medical inactive", [False, False], [config["medical_enabled"], "Medical" in config["active_roles"]])
check("DOC-04 source IDs unique", len(sources), len(by_source))
check("DOC-05 source/backup IDs", sorted(by_source), sorted(by_backup))
check("DOC-06 features", [f"F-{i:03}" for i in range(1, 9)], re.findall(r"^\| (F-\d{3}) \|", body, re.M))
check("DOC-07 decisions", [f"DEC-{i:02}" for i in range(1, 24)], re.findall(r"^\| (DEC-\d{2}) \|", body, re.M))
check("DOC-08 screen group IDs", [f"S-{i:03}" for i in range(1, 5)], re.findall(r"^\| (S-\d{3}) \|", body, re.M))
check("DOC-09 cancelled wireframes", "excluded_by_user", config["deliverables"]["wireframe"])
check("DOC-10 no claimed live map", "not_verified", config["technology"]["map_integration_status"])
for sid, entry in by_backup.items():
    if entry["state"] == "snapshot":
        header, text = snapshot(entry["backup_files"][0])
        check(sid + " revision", ["PM-MVP-v2.1"] * 3,
              [header["source_revision"], entry["source_revision"], by_source[sid]["source_revision"]])
        check(sid + " capture time", entry["captured_at"], header["captured_at"])
        check(sid + " declared scope", entry["capture_scope"], header["capture_scope"])
        check(sid + " body scope preserved", True, all(part.strip() in body for part in re.split(r"(?=^### )", text, flags=re.M) if part.strip()))
    else:
        check(sid + " blank slot", ["unregistered_blank", []], [entry["state"], entry["backup_files"]])
check("DOC-11 snapshots", 8, sum(x["state"] == "snapshot" for x in manifest))

broken = []
for path in [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").rglob("*.md"))]:
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
        target = target.split("#", 1)[0]
        if not target or re.match(r"^[A-Za-z][\w+.-]*:", target):
            continue
        if not (path.parent / target).exists():
            broken.append(str(path.relative_to(ROOT)) + ": " + target)
check("DOC-12 local Markdown links", [], broken)

# Reference calculations, using the approved policy; these are not app tests.
def late(actual, scheduled):
    seconds = max(0, actual - scheduled)
    return seconds, "0분" if seconds == 0 else "1분 미만" if seconds < 60 else f"{seconds // 60}분"

for case, actual, expected in [("early", -1, (0, "0분")), ("on time", 0, (0, "0분")),
                               ("one second", 1, (1, "1분 미만")), ("59 seconds", 59, (59, "1분 미만")),
                               ("60 seconds", 60, (60, "1분")), ("corrected to 5 minutes", 300, (300, "5분"))]:
    check("ARRIVAL " + case, expected, late(actual, 0), "F-007")


def gps_off(samples):
    count, seen = 0, set()
    for sample_id, distance, accuracy, age in samples:
        if sample_id in seen:
            continue
        seen.add(sample_id)
        count = count + 1 if distance <= 100 and accuracy <= 50 and age < 60 else 0
        if count >= 2:
            return True
    return False

gps_cases = [
    ("single", [(1, 80, 20, 0)], False),
    ("boundary", [(1, 100, 50, 0), (2, 100, 50, 0)], True),
    ("outside", [(1, 100.1, 20, 0), (2, 100, 20, 0)], False),
    ("inaccurate", [(1, 80, 50.1, 0), (2, 80, 20, 0)], False),
    ("stale", [(1, 80, 20, 60), (2, 80, 20, 0)], False),
    ("same sample", [(1, 80, 20, 0), (1, 80, 20, 0)], False),
    ("consecutive reset", [(1, 80, 20, 0), (2, 120, 20, 0), (3, 80, 20, 0)], False),
    ("after reset", [(1, 120, 20, 0), (2, 80, 20, 0), (3, 80, 20, 0)], True),
]
for name, samples, expected in gps_cases:
    check("GPS " + name, expected, gps_off(samples), "F-002")


def fee(p, score, opponents, arrived_late=True, complete=True):
    if not arrived_late:
        return "정시", 0
    if not complete or not opponents:
        return "승패 미확정", p
    delta = score * len(opponents) - sum(opponents)
    return ("승리", 0) if delta > 0 else ("패배", 2 * p) if delta < 0 else ("무승부", p)

fee_cases = [
    ("win", (3000, 250, [100, 200, 300]), ("승리", 0)),
    ("loss", (3000, 150, [100, 200, 300]), ("패배", 6000)),
    ("tie", (3000, 200, [100, 200, 300]), ("무승부", 3000)),
    ("no rounding tie", (3000, 100, [100, 101]), ("패배", 6000)),
    ("zero base", (0, 1, [10]), ("패배", 0)),
    ("missing score", (3000, 1000, [100], True, False), ("승패 미확정", 3000)),
    ("no opponent", (3000, 1000, []), ("승패 미확정", 3000)),
    ("arrival corrected on time", (3000, 1, [100], False), ("정시", 0)),
    ("still late retains multiplier", (3000, 1, [100], True), ("패배", 6000)),
]
for name, args, expected in fee_cases:
    check("GAME " + name, expected, fee(*args), "F-006/F-007")

# One participant maps to one current candidate; finalization ends changes.
votes = {"A": "C1", "B": "C1"}
votes["A"] = "C2"
check("VOTE replacement counts once", {"C1": 1, "C2": 1}, dict(Counter(votes.values())), "F-004")
for name, author, actor, ever_voted, final, expected in [
    ("owner before votes", "A", "A", False, False, True),
    ("another participant", "A", "B", False, False, False),
    ("received vote", "A", "A", True, False, False),
    ("after final", "A", "A", False, True, False),
]:
    check("CANDIDATE " + name, expected, author == actor and not ever_voted and not final, "F-003")
for host, candidate_exists, expected in [(True, True, True), (False, True, False), (True, False, False)]:
    check(f"FINAL host={host} candidate={candidate_exists}", expected, host and candidate_exists, "F-005")

selected = "lateA"
arrived = ["host", "friend", "lateA", "lateB"]
roster = tuple(p for p in arrived if p != selected)
arrived.append("newArrival")
check("GAME frozen arrived roster excludes selected only", ("host", "friend", "lateB"), roster, "F-006")
check("GAME all scores before deadline", True, 89 <= 90, "F-006")
check("GAME score after deadline", False, 91 <= 90, "F-006")
check("GAME capped duration", 60, min(65, 60), "F-006")

def due_alert(joined_at, due_at, closed, seen):
    return joined_at <= due_at and not closed and not seen

for name, args, expected in [
    ("normal", (0, 10, False, False), True),
    ("joined after alert", (11, 10, False, False), False),
    ("closed gathering", (0, 10, True, False), False),
    ("duplicate event", (0, 10, False, True), False),
]:
    check("ALERT " + name, expected, due_alert(*args), "F-008")
check("ALERT first candidate only nonvoters", ["B", "C"], [u for u in ["A", "B", "C"] if u not in {"A"}], "F-008")
check("ALERT final result all", ["A", "B", "C"], ["A", "B", "C"], "F-008")

# PM-MVP-v2.1: read the approved parameters from the actual Notion snapshot.
def spec_number(label):
    match = re.search(r"^\| " + re.escape(label) + r" \| ([\d.]+)", body, re.M)
    if match is None:
        raise ValueError("Missing policy parameter: " + label)
    return Fraction(match.group(1))


cap = spec_number("지각 시간 상한")
fish_max = spec_number("물고기 크기 최대 배율")
trex_max = spec_number("T-Rex 장애물 수 최대 배율")
check("HANDICAP approved parameters", ["1200", "3/2", "2"], list(map(str, (cap, fish_max, trex_max))), "F-006")
check("HANDICAP formula text", True, all(x in body for x in ["r = min(L / 1200, 1)", "1 + 0.5 × r", "1 + r"]), "F-006")
check("HANDICAP removes uniform-difficulty conflict", False, "동일 난이도·장애물" in body or "같은 난이도·장애물 조건" in body, "F-006")
check("HANDICAP flow and screen contract", True, all(x in body for x in ["시작 시 지각 시간·게임·명단·배율 고정", "주최자의 T-Rex/물고기 점프 선택", "같은 경기의 도착자 평균"]), "F-006")


def handicap(late_seconds):
    ratio = min(Fraction(max(0, late_seconds)) / cap, Fraction(1))
    return ratio, 1 + (fish_max - 1) * ratio, 1 + (trex_max - 1) * ratio


for seconds, expected in [
    (-1, ("0", "1", "1")), (0, ("0", "1", "1")),
    (1, ("1/1200", "2401/2400", "1201/1200")),
    (600, ("1/2", "5/4", "3/2")),
    (1199, ("1199/1200", "3599/2400", "2399/1200")),
    (1200, ("1", "3/2", "2")), (1201, ("1", "3/2", "2")),
    (1800, ("1", "3/2", "2")), (7200, ("1", "3/2", "2")),
]:
    check(f"HANDICAP boundary {seconds}s", list(expected), list(map(str, handicap(seconds))), "F-006")

scales = [handicap(seconds) for seconds in range(0, 3601)]
check("HANDICAP monotonic before and after cap", True, all(a[1] <= b[1] and a[2] <= b[2] for a, b in zip(scales, scales[1:])), "F-006")
check("HANDICAP cap holds across 3601 seconds", True, all(1 <= f <= fish_max and 1 <= t <= trex_max for _, f, t in scales), "F-006")
check("HANDICAP actual lateness remains uncapped", (1800, "30분"), late(1800, 0), "F-006/F-007")


def round_snapshot(is_host, game, target, late_seconds, arrived_people, attempted):
    if not is_host or game not in ("T-Rex", "물고기 점프"):
        raise ValueError("Host and valid game required")
    if target not in arrived_people or late_seconds <= 0 or target in attempted:
        raise ValueError("Confirmed late arrival and unused single attempt required")
    opponents = tuple(person for person in arrived_people if person != target)
    if not opponents:
        raise ValueError("No comparison group")
    _, fish, trex = handicap(late_seconds)
    return dict(game=game, target=target, opponents=opponents, late_seconds=late_seconds,
                target_multiplier=fish if game == "물고기 점프" else trex,
                opponent_multipliers=tuple(Fraction(1) for _ in opponents))


def rejected(call):
    try:
        call()
        return False
    except ValueError:
        return True


people = ["host", "lateA", "lateB"]
arrival = {"late_seconds": 600}
fish_round = round_snapshot(True, "물고기 점프", "lateA", arrival["late_seconds"], people, set())
arrival["late_seconds"] = 1200
people.append("lateC")
check("HANDICAP start snapshot survives later edits", [600, "5/4", ["host", "lateB"]], [fish_round["late_seconds"], str(fish_round["target_multiplier"]), list(fish_round["opponents"])], "F-006/F-007")
check("HANDICAP other late opponent uses baseline", ["1", "1"], list(map(str, fish_round["opponent_multipliers"])), "F-006")
second_round = round_snapshot(True, "T-Rex", "lateB", 1200, people, {"lateA"})
check("HANDICAP separate late player uses own delay", "2", str(second_round["target_multiplier"]), "F-006")
for label, args in [
    ("nonhost", (False, "T-Rex", "lateA", 600, people, set())),
    ("unknown game", (True, "Other", "lateA", 600, people, set())),
    ("not arrived", (True, "T-Rex", "missing", 600, people, set())),
    ("on time", (True, "T-Rex", "lateA", 0, people, set())),
    ("retry in another game", (True, "T-Rex", "lateA", 600, people, {"lateA"})),
    ("zero opponents", (True, "물고기 점프", "lateA", 600, ["lateA"], set())),
]:
    check("GAME selection rejects " + label, True, rejected(lambda args=args: round_snapshot(*args)), "F-006")


def compare_round(round_id, game, expected_people, submissions):
    ids = [x["person"] for x in submissions]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_people):
        raise ValueError("Roster mismatch, duplicate or missing score")
    if any(x["round"] != round_id or x["game"] != game for x in submissions):
        raise ValueError("Mixed game or round")
    return [x["score"] for x in submissions]


scores = [dict(person="host", round="R1", game="물고기 점프", score=100),
          dict(person="lateB", round="R1", game="물고기 점프", score=200)]
check("GAME same round raw scores accepted", [100, 200], compare_round("R1", "물고기 점프", ["host", "lateB"], scores), "F-006")
for label, changed in [("game", [scores[0], dict(scores[1], game="T-Rex")]),
                       ("round", [scores[0], dict(scores[1], round="R2")]),
                       ("missing", scores[:1]), ("duplicate", [scores[0], scores[0]])]:
    check("GAME mixed comparison rejects " + label, True, rejected(lambda changed=changed: compare_round("R1", "물고기 점프", ["host", "lateB"], changed)), "F-006")
check("GAME handicap does not award score bonus", ("패배", 6000), fee(3000, 100, compare_round("R1", "물고기 점프", ["host", "lateB"], scores)), "F-006")

failed = [x for x in RESULTS if x["status"] == "FAIL"]
print(json.dumps({"scope": "document checks and reference policy examples; not product runtime", "total": len(RESULTS), "passed": len(RESULTS)-len(failed), "failed": len(failed), "results": RESULTS}, ensure_ascii=False, indent=2))
sys.exit(bool(failed))
