import hashlib
import re
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_digest(text: str, prompt_text: str, chunk_size: int) -> str:
    """Creăm un hash unic combinând textul, promptul curent și dimensiunea chunk-ului."""
    combined = f"{text}|{prompt_text}|{chunk_size}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def clean_transcript(text: str) -> str:
    if not text:
        return ""
    timestamp_pattern = r"\(\d{1,2}:\d{2}(?::\d{2})?\)"
    text = re.sub(timestamp_pattern, " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_text_into_chunks(text: str, max_chars: int) -> list[str]:
    if not text:
        return []
    
    words = text.split()
    chunks = []
    current = ""

    for w in words:
        if len(w) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            for start in range(0, len(w), max_chars):
                chunks.append(w[start : start + max_chars])
            continue

        candidate = w if not current else f"{current} {w}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            current = w

    if current:
        chunks.append(current)
        
    logger.info(f"Split text into {len(chunks)} chunks using max_chars={max_chars}")
    return chunks

def build_prompt(idx: int, total: int, chunk: str, system_prompt: str) -> str:
    """Construiește promptul final folosind instrucțiunile personalizate ale utilizatorului."""
    if idx == 1:
        return (
            f"{system_prompt}\n\n"
            f"INPUT TEXT (PART {idx}/{total}):\n"
            f"{chunk}\n\n"
            "INSTRUCTIONS FOR THIS PART:\n"
            "- Start writing the textbook chapter now based ONLY on this part.\n"
            "- Use H2/H3 headings, bold key terms, and keep a clean textbook style.\n"
            "- Do not invent information.\n"
            "- If the content feels incomplete, stop naturally and continue in the next parts.\n"
        )
    return (
        f"{system_prompt}\n\n"
        "CONTEXT:\n"
        "We are continuing the SAME textbook chapter. Previous parts have already been processed.\n\n"
        f"INPUT TEXT (PART {idx}/{total}):\n"
        f"{chunk}\n\n"
        "INSTRUCTIONS FOR THIS PART:\n"
        "- CONTINUE from where you left off.\n"
        "- Do NOT create a new Title or a new Introduction.\n"
        "- Maintain the SAME formatting (H2/H3, bolding, bullet rules).\n"
        "- Treat this as a direct continuation of the same chapter.\n"
        "- Do not repeat already-covered content unless needed for clarity.\n"
    )
