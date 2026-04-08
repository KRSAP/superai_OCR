import time
from pathlib import Path

from llm_client import clean_and_parse_json, request_page_extraction
from prompts import build_prompt


def _edit_distance(a: str, b: str) -> int:
    if len(a) < len(b):
        return _edit_distance(b, a)
    if len(b) == 0:
        return len(a)

    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a):
        current = [i + 1]
        for j, char_b in enumerate(b):
            current.append(
                min(
                    previous[j + 1] + 1,
                    current[j] + 1,
                    previous[j] + (char_a != char_b),
                )
            )
        previous = current
    return previous[-1]


def _is_constituency_doc(doc_id: str) -> bool:
    return doc_id.startswith("constituency")


def _merge_page_results(result_store: dict, page_result: dict) -> None:
    for name, vote_value in page_result.items():
        try:
            result_store[name] = int(vote_value)
        except (TypeError, ValueError):
            result_store[name] = 0


def _match_expected_parties(expected_parties: list[str], detected_votes: dict) -> list[int]:
    final_votes = [0] * len(expected_parties)

    exact_hit_indexes = set()
    for idx, party_name in enumerate(expected_parties):
        if party_name in detected_votes:
            try:
                final_votes[idx] = int(detected_votes[party_name])
            except (TypeError, ValueError):
                final_votes[idx] = 0
            exact_hit_indexes.add(idx)

    leftovers = {k: v for k, v in detected_votes.items() if k not in expected_parties}

    for idx, party_name in enumerate(expected_parties):
        if idx in exact_hit_indexes or not leftovers:
            continue

        best_name = None
        best_score = float("inf")

        for candidate_name in leftovers:
            score = _edit_distance(party_name, candidate_name)
            if score < best_score:
                best_score = score
                best_name = candidate_name

        if best_name is not None and best_score <= max(3, len(party_name) // 3):
            try:
                final_votes[idx] = int(leftovers[best_name])
            except (TypeError, ValueError):
                final_votes[idx] = 0
            del leftovers[best_name]

    return final_votes


def collect_votes_for_document(
    client,
    model_name: str,
    doc_id: str,
    page_paths: list[Path],
    expected_parties: list[str],
    *,
    row_numbers: list[int] | None = None,
    temperature: float = 0.0,
    max_output_tokens: int = 8192,
    thinking_budget: int = 4096,
    max_retries: int = 3,
) -> list[int]:
    document_kind = "constituency" if _is_constituency_doc(doc_id) else "party_list"
    prompt_text = build_prompt(document_kind, expected_parties)

    collected_votes: dict[str, int] = {}

    for page_idx, page_path in enumerate(page_paths, start=1):
        image_bytes = page_path.read_bytes()

        parsed_result = None

        for attempt in range(1, max_retries + 1):
            raw_text = request_page_extraction(
                client=client,
                model_name=model_name,
                image_bytes=image_bytes,
                prompt_text=prompt_text,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                thinking_budget=thinking_budget,
            )

            if raw_text is None:
                time.sleep(2 ** attempt)
                continue

            parsed_result = clean_and_parse_json(raw_text)
            if parsed_result is None:
                print(f"\n  [WARN] {doc_id} page={page_idx}: invalid JSON on try {attempt}")
                time.sleep(2 ** attempt)
                continue

            break

        if parsed_result is None:
            print(f"\n  [WARN] {doc_id} page={page_idx}: failed after retries")
        else:
            _merge_page_results(collected_votes, parsed_result)

        if page_idx < len(page_paths):
            time.sleep(1)

    if not collected_votes:
        return [0] * len(expected_parties)

    return _match_expected_parties(expected_parties, collected_votes)
