import re
from collections import Counter
from typing import List, Set


class TextCleaner:
    def __init__(self,
                 take: int,
                 min_ratio: float):
        """
        Utility for cleaning extracted page texts by removing headers/footers
        and fixing common text issues.
        
        :param take: Number of lines from head/foot to consider for running lines.
        :param min_ratio: Minimum fraction of pages where a line must appear to be
                          considered a header/footer.
        """
        self.take = take
        self.min_ratio = min_ratio

    def _fix_hyphenation(self, text: str) -> str:
        """Join hyphenated line breaks, normalize whitespace and newlines."""
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)   # intra-paragraph
        text = re.sub(r"\n{3,}", "\n\n", text)         # collapse 3+ newlines
        text = re.sub(r"[ \t]+", " ", text)            # normalize spaces/tabs
        return text.strip()

    def _detect_running_lines(self, pages: List[str], position: str) -> Set[str]:
        """Detect repeated headers or footers across pages."""
        candidates: List[str] = []
        for page in pages:
            lines = [ln.strip() for ln in page.splitlines() if ln.strip()]
            if not lines:
                continue
            segment = lines[:self.take] if position == "head" else lines[-self.take:]
            candidates.extend(segment)

        counts = Counter(candidates)
        threshold = max(1, int(len(pages) * self.min_ratio))
        running = {
            line for line, cnt in counts.items()
            if cnt >= threshold and 5 <= len(line) <= 120
        }
        return running

    def _strip_running(self, text: str, headers: Set[str], footers: Set[str]) -> str:
        """Remove detected headers and footers from a page."""
        lines = [ln.strip() for ln in text.splitlines()]
        if lines and lines[0] in headers:
            lines = lines[1:]
        if lines and lines[-1] in footers:
            lines = lines[:-1]
        return "\n".join(lines).strip()

    def clean_pages(self, pages: List[str]) -> List[str]:
        """Clean a list of page texts."""
        headers = self._detect_running_lines(pages, "head")
        footers = self._detect_running_lines(pages, "foot")
        cleaned: List[str] = []
        for text in pages:
            txt = self._strip_running(text, headers, footers)
            txt = self._fix_hyphenation(txt)
            cleaned.append(txt)
        return cleaned
