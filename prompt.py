PARTY_LIST_PROMPT = """This is one page from a Thai election document (แบบ สส.6/1) — party-list type (แบบบัญชีรายชื่อ).

The page may contain a table or list showing political parties and their vote counts.

Vote counts typically appear as Thai digits with Thai text in parentheses, or as Arabic numerals with Thai text.

READING STRATEGY for each vote count:
1. Read the Thai TEXT description in parentheses. This is the most reliable source.
2. Use the printed digits only as a cross-check.
3. Thai digit key: ๐=0 ๑=1 ๒=2 ๓=3 ๔=4 ๕=5 ๖=6 ๗=7 ๘=8 ๙=9
4. If the text and digits disagree, use the Thai text.

IMPORTANT DIGIT CONFUSIONS:
- ๔ vs ๘
- ๑ vs ๓
- ๖ vs ๐

Extract vote counts only for these parties if they appear on this page:

{party_lines}

Return a JSON object using the exact names above:
{{"party_name": vote_count}}

If none appear, return {{}}
Return valid JSON only."""

CONSTITUENCY_PROMPT = """This is one page from a Thai election document (แบบ สส.6/1) — constituency type (แบบแบ่งเขต).

Focus only on section ๕, where candidate/party vote counts are listed.

READING STRATEGY for each vote count:
1. Read the Thai TEXT description in parentheses. This is the most reliable source.
2. Use the printed digits only as a cross-check.
3. Thai digit key: ๐=0 ๑=1 ๒=2 ๓=3 ๔=4 ๕=5 ๖=6 ๗=7 ๘=8 ๙=9
4. If the text and digits disagree, use the Thai text.

IMPORTANT DIGIT CONFUSIONS:
- ๔ vs ๘
- ๑ vs ๓
- ๖ vs ๐

Ignore summary sections. Extract only the vote counts for these parties if visible:

{party_lines}

Return a JSON object using the exact names above:
{{"party_name": vote_count}}

If none appear, return {{}}
Return valid JSON only."""


def build_prompt(document_kind: str, party_names: list[str]) -> str:
    selected = CONSTITUENCY_PROMPT if document_kind == "constituency" else PARTY_LIST_PROMPT
    joined_names = "\n".join(f"- {name}" for name in party_names)
    return selected.format(party_lines=joined_names)