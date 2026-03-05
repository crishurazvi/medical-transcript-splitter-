import streamlit as st
import time

from app.core.processor import (
    clean_transcript,
    split_text_into_chunks,
    build_prompt,
    generate_digest
)
from app.core.prompts import DEFAULT_SYSTEM_PROMPT
from app.components.ui_elements import copy_button_custom

# Configurare Pagină
st.set_page_config(page_title="MedSplit | Script to Course", page_icon="⚕️", layout="wide")

# --- STATE MANAGEMENT ---
def init_state():
    defaults = {
        "last_digest": "",
        "generated": False,
        "chunks": [],
        "prompts": [],
        "raw_text": "",
        "custom_prompt": DEFAULT_SYSTEM_PROMPT,
        "chunk_size": 6000
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# --- CALLBACKS ---
def process_data():
    raw_text = st.session_state.raw_text.strip()
    if not raw_text:
        st.toast("⚠️ Introdu textul brut înainte de a genera.", icon="⚠️")
        return
        
    current_prompt = st.session_state.custom_prompt
    current_chunk_size = st.session_state.chunk_size
    
    # Digest inteligent: dacă se schimbă textul, promptul SAU lungimea, se regenerează
    current_digest = generate_digest(raw_text, current_prompt, current_chunk_size)

    if current_digest == st.session_state.last_digest and st.session_state.generated:
        st.toast("✅ Datele sunt deja procesate și la zi.", icon="✅")
        return

    with st.spinner("🧠 Procesăm și feliem transcriptul..."):
        time.sleep(0.3) # Micro-interaction
        cleaned = clean_transcript(raw_text)
        chunks = split_text_into_chunks(cleaned, current_chunk_size)
        
        # Aici transmitem promptul customizat
        prompts = [build_prompt(i + 1, len(chunks), ch, current_prompt) for i, ch in enumerate(chunks)]

        st.session_state.chunks = chunks
        st.session_state.prompts = prompts
        st.session_state.last_digest = current_digest
        st.session_state.generated = True
    
    st.toast("Generare completă!", icon="🎉")

def reset_state():
    st.session_state.generated = False
    st.session_state.chunks = []
    st.session_state.prompts = []
    st.session_state.last_digest = ""
    st.toast("Vizualizare resetată. Datele tale au rămas în input.", icon="🧹")

def reset_prompt():
    st.session_state.custom_prompt = DEFAULT_SYSTEM_PROMPT
    st.toast("Instrucțiunile au fost resetate la varianta implicită.", icon="🔄")


# --- UI: SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Setări")
    
    st.slider(
        "Caractere / Chunk",
        min_value=2000, max_value=20000, value=st.session_state.chunk_size, step=500,
        key="chunk_size",
        help="6000-8000 e ideal pentru a nu pierde detalii în ChatGPT."
    )
    
    show_cleaned_toggle = st.toggle("🔍 Mod Debug (Afișează codul promptului)", value=False)
    
    st.divider()
    st.markdown("""
    **Flux de lucru:**
    1. Lipește textul în tab-ul *Procesare*.
    2. (Opțional) Ajustează instrucțiunile în tab-ul *Setări Prompt*.
    3. Apasă **Generează** și copiază pe rând căsuțele.
    """)

# --- UI: MAIN AREA (TABS) ---
st.title("⚕️ Medical Transcript Splitter")

tab_main, tab_settings = st.tabs(["📝 Procesare Text", "🛠️ Setări Prompt (Instrucțiuni)"])

# TAB 1: Procesarea propriu-zisă
with tab_main:
    # Text input legat de session state
    st.text_area(
        "Lipește Transcriptul Brut Aici:", 
        height=200, 
        key="raw_text",
        placeholder="Ex: (00:01) Alors, bonjour à tous, on va commencer..."
    )

    # Butoane de acțiune
    col_action1, col_action2, col_blank = st.columns([2, 2, 6])
    with col_action1:
        st.button("🚀 Generează Prompturi", type="primary", use_container_width=True, on_click=process_data)
    with col_action2:
        st.button("🧹 Ascunde Rezultatele", on_click=reset_state, use_container_width=True)

    # Afișare rezultate
    if not st.session_state.generated:
        st.write("---")
        st.info("💡 **Aștept datele.** Lipește textul și apasă 'Generează'.", icon="ℹ️")
    else:
        prompts = st.session_state.prompts
        total = len(prompts)
        
        st.divider()
        
        # Metrici
        m1, m2, m3 = st.columns(3)
        raw_len = len(st.session_state.raw_text)
        m1.metric("Caractere Totale", f"{raw_len:,}")
        m2.metric("Tokeni Estimați (~)", f"{raw_len // 4:,}")
        m3.metric("Chunk-uri Generate", f"{total}")

        # Download general
        all_prompts_text = "\n\n=========================\n\n".join(
            [f"--- CHUNK {i+1} ---\n{p}" for i, p in enumerate(prompts)]
        )
        st.download_button(
            label="📥 Descarcă absolut toate prompturile (.txt)",
            data=all_prompts_text,
            file_name="medical_prompts_export.txt",
            mime="text/plain"
        )
        
        st.write("")
        
        # Lista de carduri cu butoanele de Copy perfecte
        for i, prompt in enumerate(prompts):
            idx = i + 1
            with st.container(border=True):
                cols = st.columns([1, 4])
                with cols[0]:
                    st.markdown(f"### 📦 Partea {idx}/{total}")
                with cols[1]:
                    copy_button_custom(
                        text_to_copy=prompt,
                        label=f"Copiază Partea {idx}",
                        dom_id=f"copy_{idx}_{st.session_state.last_digest[:6]}"
                    )
                
                if show_cleaned_toggle:
                    with st.expander("👀 Vezi exact ce va fi trimis către LLM"):
                        st.code(prompt, language="markdown")

# TAB 2: Editarea Prompt-ului (Fără a fi nevoie de modificări de cod)
with tab_settings:
    st.markdown("### ✍️ Editează Instrucțiunile de Bază")
    st.info("Aici poți schimba comportamentul lui ChatGPT. Ce scrii aici va fi adăugat la începutul fiecărui chunk.")
    
    st.text_area(
        "System Prompt (Instrucțiuni LLM):",
        height=400,
        key="custom_prompt"
    )
    
    st.button("🔄 Resetează la varianta implicită", on_click=reset_prompt)
