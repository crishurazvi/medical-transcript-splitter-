from app.core.processor import clean_transcript, split_text_into_chunks

def test_clean_transcript():
    raw = "(01:23) Bonjour   à tous. (02:44) Aujourd'hui..."
    cleaned = clean_transcript(raw)
    assert cleaned == "Bonjour à tous. Aujourd'hui..."

def test_split_text_into_chunks():
    text = "Cuvant unu doi trei patru"
    # Max chars 10 ar trebui să rupă textul corect fără a tăia cuvinte.
    chunks = split_text_into_chunks(text, max_chars=10)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 10
