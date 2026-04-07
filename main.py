from pathlib import Path
import time

from google.genai import Client
from google.genai.types import HttpOptions

from config import load_config
from storage import load_template_rows, load_progress_map, save_progress_map, write_submission_csv
from page_loader import list_document_pages
from vote_extract import collect_votes_for_document


def process_documents() -> None:
    cfg = load_config()

    if not cfg["api_key"]:
        raise ValueError("Missing API key. Set API_KEY in your environment before running.")

    data_dir = Path(cfg["data_dir"])
    image_dir = Path(cfg["image_dir"])
    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    template_csv = data_dir / cfg["template_file"]
    progress_json = output_dir / cfg["progress_file"]
    submission_csv = output_dir / cfg["output_file"]

    client = Client(
        api_key=cfg["api_key"],
        http_options=HttpOptions(timeout=cfg["http_timeout"]),
    )

    all_rows, grouped_docs = load_template_rows(template_csv)
    saved_votes = load_progress_map(progress_json)

    doc_ids = sorted(grouped_docs.keys())

    print(f"Model        : {cfg['model_name']}")
    print(f"Template CSV : {template_csv}")
    print(f"Image folder : {image_dir}")
    print(f"Documents    : {len(doc_ids)}")
    print(f"Rows         : {len(all_rows)}")

    if saved_votes:
        print(f"Resume mode  : {len(saved_votes)} completed rows loaded")

    for index, doc_id in enumerate(doc_ids, start=1):
        rows = grouped_docs[doc_id]

        first_row_id = rows[0]["id"]
        if first_row_id in saved_votes:
            continue

        page_paths = list_document_pages(image_dir, doc_id)
        if not page_paths:
            print(f"[{index}/{len(doc_ids)}] {doc_id} -> no page images, fill zeros")
            for row in rows:
                saved_votes[row["id"]] = 0
            continue

        party_names = [row["party_name"] for row in rows]
        row_numbers = [int(row["row_num"]) for row in rows]

        print(
            f"[{index}/{len(doc_ids)}] {doc_id} | "
            f"pages={len(page_paths)} parties={len(party_names)}",
            end=" ",
            flush=True,
        )

        votes = collect_votes_for_document(
            client=client,
            model_name=cfg["model_name"],
            doc_id=doc_id,
            page_paths=page_paths,
            expected_parties=party_names,
            row_numbers=row_numbers,
            temperature=cfg["temperature"],
            max_output_tokens=cfg["max_output_tokens"],
            thinking_budget=cfg["thinking_budget"],
            max_retries=cfg["max_retries"],
        )

        for row, vote in zip(rows, votes):
            saved_votes[row["id"]] = vote

        non_zero_count = sum(1 for v in votes if v > 0)
        print(f"done nonzero={non_zero_count}/{len(votes)}")

        if index % cfg["save_interval"] == 0:
            save_progress_map(progress_json, saved_votes)
            write_submission_csv(submission_csv, all_rows, saved_votes)

        time.sleep(cfg["rate_limit_delay"])

    save_progress_map(progress_json, saved_votes)
    write_submission_csv(submission_csv, all_rows, saved_votes)

    print(f"\nFinished -> {submission_csv}")
    print(f"Predictions: {len(saved_votes)}")
    print(f"Non-zero   : {sum(1 for v in saved_votes.values() if v > 0)}")


if __name__ == "__main__":
    process_documents()