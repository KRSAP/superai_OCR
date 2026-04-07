import json
import re

from google.genai import types


def clean_and_parse_json(raw_text: str) -> dict | None:
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = re.sub(r",\s*([}\]])", r"\1", text)

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    fallback = re.search(r"\{[^{}]+\}", text, re.DOTALL)
    if fallback:
        try:
            parsed = json.loads(fallback.group(0))
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None

    return None


def request_page_extraction(
    client,
    model_name: str,
    image_bytes: bytes,
    prompt_text: str,
    *,
    temperature: float,
    max_output_tokens: int,
    thinking_budget: int,
) -> str | None:
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                types.Part.from_text(text=prompt_text),
            ],
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget),
            ),
        )
        return response.text.strip() if response.text else None
    except Exception as exc:
        print(f"\n  [API ERROR] {exc}")
        return None