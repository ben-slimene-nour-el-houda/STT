import re

def postprocess_text(raw_result: str) -> str:
    """Lightweight Arabic‑friendly post‑processing.
    - Capitalise the first character.
    - Ensure sentence ends with a period.
    - Replace English commas with Arabic commas.
    - Remove any Unicode bidi markers that may have been added elsewhere.
    """
    text = raw_result.strip()
    if not text:
        return text
    # Capitalise first character (Arabic letters are unaffected by .upper())
    text = text[0].upper() + text[1:]
    # Ensure a period at the end (you can replace with Arabic full stop if desired)
    if text[-1] not in ".!?":
        text += "."
    # Replace English commas with Arabic commas and ensure a space after
    text = re.sub(r",\s*", "، ", text)
    # Remove any stray bidi control characters
    text = text.replace("\u202B", "").replace("\u202C", "").replace("\u200F", "")
    # Strip any existing bidi markers that might have been added elsewhere
    text = text.replace("\u202B", "").replace("\u202C", "").replace("\u200F", "")
    # Wrap with RTL embedding markers so left‑to‑right terminals render correctly
    return "\u202B" + text + "\u202C"
    """Lightweight rule‑based post‑processing.
    • Capitalise the first character.
    • Ensure the text ends with a terminal punctuation mark.
    • Insert a comma before common conjunctions (and, but, or) for readability.
    This keeps the pipeline fast and has zero external model dependencies.
    """
    text = raw_result.strip()
    if not text:
        return text
    # Capitalise first character
    text = text[0].upper() + text[1:]
    # Add a period if missing
    if text[-1] not in ".!?":
        text += "."
    # Remove any leftover bidi markers that may have been added elsewhere
    text = text.replace("\u202B", "").replace("\u202C", "").replace("\u200F", "")
    # Replace English comma with Arabic comma and ensure spacing
    text = text.replace(", ", "، ")
    # Replace a trailing period with Arabic full stop (optional – keep dot if preferred)
    if text.endswith("."):
        text = text[:-1] + "."
    return text
