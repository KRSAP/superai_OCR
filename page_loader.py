from pathlib import Path


def list_document_pages(image_dir: str | Path, doc_id: str) -> list[Path]:
    image_root = Path(image_dir)
    pages: list[Path] = []

    first_page = image_root / f"{doc_id}.png"
    if first_page.exists():
        pages.append(first_page)

    for page_no in range(2, 10):
        candidate = image_root / f"{doc_id}_page{page_no}.png"
        if candidate.exists():
            pages.append(candidate)

    return pages