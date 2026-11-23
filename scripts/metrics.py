"""Summarize verified, comparable exam scores from normalized JSON."""
import argparse
import json
import math
from pathlib import Path
from statistics import mean


def number(value, limit, label):
    if value is None:
        return None
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= limit:
        raise ValueError(f"{label}: expected a score from 0 to {limit}")
    return value


def full_mark(value, label):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label}: expected a positive maximum")
    return value


def summarize(values, maximum):
    return {
        "n": len(values),
        "mean": mean(values) if values else None,
        "rate": sum(values) / (maximum * len(values)) if values else None,
        "zero": values.count(0),
        "full": values.count(maximum),
        "partial": sum(0 < value < maximum for value in values),
    }


def group_summary(items, field, cohort_size):
    marks = [(item["max"], item[field]) for item in items]
    possible = sum(maximum * part["n"] for maximum, part in marks)
    earned = sum(maximum * part["n"] * part["rate"] for maximum, part in marks if part["n"])
    return {
        "rate": earned / possible if possible else None,
        "possible": possible,
        "scored_entries": sum(part["n"] for _, part in marks),
        "cohort_size": cohort_size,
    }


def student_groups(groups, row):
    output = {}
    for group, items in groups.items():
        observed = [item for item in items if row.get(item["id"]) is not None]
        available = sum(item["max"] for item in observed)
        scored = sum(row[item["id"]] for item in observed)
        output[group] = {
            "score": round(scored, 8) if observed else None,
            "scored_max": available,
            "mapped_max": sum(item["max"] for item in items),
            "loss": round(available - scored, 8) if observed else None,
        }
    return output


def analyze(source, student_id=None, subject_filter=None):
    students = source["students"]
    target = source.get("target_class")
    by_id = {}
    for student in students:
        sid = student["id"]
        if not isinstance(sid, str) or not sid or sid != sid.strip() or sid in by_id:
            raise ValueError(f"Invalid or duplicate student ID: {sid!r}")
        by_id[sid] = student

    if student_id is not None:
        if student_id not in by_id:
            raise ValueError(f"Student ID not found: {student_id}")
        student_class = by_id[student_id]["class"]
        if target is not None and target != student_class:
            raise ValueError("Student is outside the supplied target class")
        target = student_class
    if subject_filter is not None and subject_filter not in source["subjects"]:
        raise ValueError(f"Subject not found: {subject_filter}")

    class_ids = {s["id"] for s in students if s["class"] == target}
    if target is not None and not class_ids:
        raise ValueError(f"Class has no matched students: {target}")
    output = {"target_class": target, "subjects": {}, "students": {}}
    report_ids = {student_id} if student_id is not None else class_ids
    for sid in sorted(report_ids):
        output["students"][sid] = {"name": by_id[sid]["name"], "subjects": {}}

    for subject, definition in source["subjects"].items():
        if subject_filter is not None and subject != subject_filter:
            continue
        maximum = full_mark(definition["max"], subject)
        scores = {}
        for sid, student in by_id.items():
            value = number(student["scores"].get(subject), maximum, f"{subject}/{sid}")
            if value is not None:
                scores[sid] = value
        class_valid = class_ids.intersection(scores)
        items = definition.get("items", [])
        raw_rows = definition.get("rows", {})
        rows = {}
        ids = set()
        for item in items:
            if not isinstance(item["id"], str) or not item["id"] or item["id"] in ids:
                raise ValueError(f"{subject}: invalid or duplicate question ID {item['id']!r}")
            ids.add(item["id"])
            full_mark(item["max"], f"{subject}/{item['id']}")
        if sum(item["max"] for item in items) > maximum + 1e-8:
            raise ValueError(f"{subject}: question maxima exceed subject maximum")
        for sid, row in raw_rows.items():
            if sid not in scores:
                raise ValueError(f"{subject}/{sid}: question row has no valid matched subject score")
            if extras := row.keys() - ids:
                raise ValueError(f"{subject}/{sid}: question IDs not listed in items: {sorted(extras)}")
            rows[sid] = row

        report_valid = report_ids.intersection(scores)
        losses = {sid: [] for sid in report_valid}
        missing = {sid: [] for sid in report_valid}
        details = []
        groups = {}
        for item in items:
            key = item["id"]
            full = item["max"]
            valid = {}
            for sid, row in rows.items():
                value = number(row.get(key), full, f"{subject}/{sid}/{key}")
                if value is not None:
                    valid[sid] = value
            grade = summarize(list(valid.values()), full)
            cls = summarize([v for sid, v in valid.items() if sid in class_valid], full)
            gap = None if cls["rate"] is None else 100 * (cls["rate"] - grade["rate"])
            item_result = {**item, "class": cls, "grade": grade, "gap_pp": gap}
            details.append(item_result)
            groups.setdefault(item["group"], []).append(item_result)
            for sid in report_valid:
                value = valid.get(sid)
                if value is None:
                    missing[sid].append(key)
                elif value < full:
                    losses[sid].append({**item, "score": value, "loss": round(full - value, 8)})

        output["subjects"][subject] = {
            "max": maximum,
            "class": summarize([scores[sid] for sid in class_valid], maximum),
            "grade": summarize(list(scores.values()), maximum),
            "items": details,
            "groups": {
                group: {
                    "class": group_summary(parts, "class", len(class_valid)),
                    "grade": group_summary(parts, "grade", len(scores)),
                }
                for group, parts in groups.items()
            },
        }
        for sid in sorted(report_valid):
            detail = {
                "score": scores[sid],
                "max": maximum,
                "losses": losses[sid],
                "missing_items": missing[sid],
                "has_question_scores": bool(rows.get(sid)) and len(missing[sid]) < len(items),
            }
            if student_id is not None:
                detail["groups"] = student_groups(groups, rows.get(sid, {}))
            output["students"][sid]["subjects"][subject] = detail

    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--student-id", help="Only output individual details for this student")
    parser.add_argument("--subject", help="Only analyze this subject when producing a single-student report")
    args = parser.parse_args()
    if (args.student_id is None) != (args.subject is None):
        parser.error("--student-id and --subject must be provided together")
    source = json.loads(args.input.read_text(encoding="utf-8-sig"))
    result = analyze(source, args.student_id, args.subject)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
