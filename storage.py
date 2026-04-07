import csv
import json
from collections import defaultdict
from pathlib import Path


def load_template_rows(csv_path: str | Path) -> tuple[list[dict], dict[str, list[dict]]]:
    grouped = defaultdict(list)
    all_rows: list[dict] = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_rows.append(row)
            grouped[row["doc_id"]].append(row)

    return all_rows, grouped


def load_progress_map(progress_path: str | Path) -> dict:
    path = Path(progress_path)
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress_map(progress_path: str | Path, vote_map: dict) -> None:
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(vote_map, f, ensure_ascii=False, indent=2)


def write_submission_csv(output_path: str | Path, rows: list[dict], vote_map: dict) -> None:
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "votes"])
        for row in rows:
            writer.writerow([row["id"], vote_map.get(row["id"], 0)])