import re
import unicodedata
from typing import List


STOPWORDS_PT = {
    "a","o","os","as","de","da","do","das","dos","e","em","para","por","no","na","nos","nas",
    "um","uma","uns","umas","ao","à","até","após","com","sem","sob","sobre","entre","ou"
}


def normalize_text(text: str) -> str:
    x = text.lower()
    x = unicodedata.normalize("NFD", x)
    x = x.encode("ascii", "ignore").decode("utf-8")
    x = re.sub(r"[^a-z0-9\s>]+", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def tokenize(text: str) -> List[str]:
    x = normalize_text(text)
    toks = x.split()
    return [t for t in toks if t not in STOPWORDS_PT and len(t) > 1]


def join_title_description(title: str, description: str) -> str:
    if not title and not description:
        return ""
    if not description:
        return title or ""
    if not title:
        return description or ""
    return title.strip() + " " + description.strip()

