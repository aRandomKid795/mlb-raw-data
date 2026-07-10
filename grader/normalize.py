import re
import unicodedata


def normalize(name: str) -> str:
    """
    Normalize a player name so boxscore names and slip names match reliably.
    Strips accents, punctuation (Jr., periods, apostrophes), extra whitespace,
    and lowercases everything.

    Examples:
        "José Ramírez"      -> "jose ramirez"
        "Luis Robert Jr."   -> "luis robert jr"
        "O'Neill, Tyler"    -> "tyler oneill" (if you pass "Tyler O'Neill")
    """
    if not name:
        return ""

    # Strip accents (é -> e, í -> i, etc.)
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))

    # Lowercase
    ascii_name = ascii_name.lower()

    # Remove periods, commas, apostrophes
    ascii_name = re.sub(r"[.,']", "", ascii_name)

    # Collapse whitespace
    ascii_name = re.sub(r"\s+", " ", ascii_name).strip()

    return ascii_name
