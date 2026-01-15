import re
from wordfreq import zipf_frequency
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


    @staticmethod
    def _is_word(word: str, langs: List[str] = ["en", "de"], threshold: float = 2.2) -> bool:
        """
        Return True if 'word' is common enough in at least one language.
        """
        return any(zipf_frequency(word, lang) >= threshold for lang in langs)

    def _fix_intraword_spaces(self, text: str, langs: List[str] = ["en", "de"]) -> str:
        """
        Replace spurious spaces inside words using dictionary check.
        Example: "cur rent" -> "current", but "new york" stays.
        Works with multiple languages.
        """
        tokens = text.split()
        fixed_tokens: List[str] = []
        i = 0

        while i < len(tokens):
            if i < len(tokens) - 1:
                merged = tokens[i] + tokens[i + 1]
                if self._is_word(merged, langs=langs):  # ✅ check all languages
                    fixed_tokens.append(merged)
                    i += 2
                    continue
            fixed_tokens.append(tokens[i])
            i += 1

        return " ".join(fixed_tokens)


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


    def _normalize_spacing(self, text: str, langs: List[str] = ["en", "de"]) -> str:
        """
        Normalize spacing and punctuation. 
        Uses dictionary-driven intraword space fix for multiple languages.
        """
        re_multi_spaces = re.compile(r'[ \t]{2,}')
        re_space_before_punct = re.compile(r'\s+([,.;:!?%)\]\}])')
        re_space_after_open = re.compile(r'([(\[\{])\s+')
        re_parens_number = re.compile(r'\(\s*(\d+)\s*\)')

        # Intraword spaces using dictionary across languages
        text = self._fix_intraword_spaces(text, langs=langs)

        # Punctuation/spacing normalization
        text = re_space_before_punct.sub(r'\1', text)
        text = re_space_after_open.sub(r'\1', text)
        text = re_parens_number.sub(r'(\1)', text)

        # Collapse multiple spaces inside paragraphs, preserve paragraph breaks
        paragraphs = [re_multi_spaces.sub(' ', p) for p in text.split('\n\n')]
        return '\n\n'.join(p.strip() for p in paragraphs)


    def clean_chunk_text(self, text: str) -> str:
        cleaned = self._fix_hyphenation(text)
        cleaned = self._normalize_spacing(cleaned)
        return cleaned


    def clean_pages(self, pages: List[str]) -> List[str]:
        """Clean a list of page texts."""
        headers = self._detect_running_lines(pages, "head")
        footers = self._detect_running_lines(pages, "foot")
        cleaned: List[str] = []
        for text in pages:
            txt = self._strip_running(text, headers, footers)
            txt = self._fix_hyphenation(txt)
            txt = self._normalize_spacing(txt)
            cleaned.append(txt)
        return cleaned
