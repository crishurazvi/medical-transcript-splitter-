import json
import re
import streamlit.components.v1 as components

def copy_button_custom(text_to_copy: str, label: str, dom_id: str) -> None:
    """Buton custom HTML/JS optimizat vizual pentru aspect modern, cu fallback pentru iFrames."""
    # Serializăm textul în siguranță pentru JavaScript
    payload = json.dumps(text_to_copy)
    safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "_", dom_id)

    html = f"""
    <div style="display:flex;align-items:center;gap:12px;margin:0;padding:0; font-family: sans-serif;">
      <button id="{safe_id}"
              style="
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                background: #2E86C1;
                color: #FFFFFF;
                font-weight: 600;
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
              "
              onmouseover="this.style.background='#1B4F72'; this.style.transform='translateY(-1px)';"
              onmouseout="this.style.background='#2E86C1'; this.style.transform='translateY(0)';"
              onmousedown="this.style.transform='translateY(1px)';"
      >
        <svg style="width:16px;height:16px;vertical-align:middle;margin-right:6px;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
        {label}
      </button>
      <span id="{safe_id}_msg" style="font-size:14px;font-weight:600;transition: opacity 0.3s;"></span>
    </div>

    <script>
      (function() {{
        const btn = document.getElementById("{safe_id}");
        const msg = document.getElementById("{safe_id}_msg");
        if (!btn) return;

        btn.addEventListener("click", async () => {{
          const textToCopy = {payload};
          let success = false;

          // Metoda 1: Încercăm API-ul modern (va eșua probabil în iFrame Streamlit)
          try {{
            if (navigator.clipboard && window.isSecureContext) {{
              await navigator.clipboard.writeText(textToCopy);
              success = true;
            }}
          }} catch (err) {{
            console.warn("Modern clipboard API failed, trying fallback...", err);
          }}

          // Metoda 2: Fallback la execCommand (Ocolește restricțiile iFrame-ului)
          if (!success) {{
            try {{
              const textArea = document.createElement("textarea");
              textArea.value = textToCopy;
              
              // Ascundem textarea
              textArea.style.position = "fixed";
              textArea.style.top = "-9999px";
              textArea.style.left = "-9999px";
              
              document.body.appendChild(textArea);
              textArea.focus();
              textArea.select();
              
              success = document.execCommand("copy");
              document.body.removeChild(textArea);
            }} catch (fallbackErr) {{
              console.error("Fallback failed", fallbackErr);
              success = false;
            }}
          }}

          // Afișăm rezultatul
          if (success) {{
            msg.textContent = "✅ Copiat!";
            msg.style.color = "#27AE60";
            msg.style.textShadow = "0px 0px 8px rgba(39, 174, 96, 0.4)"; // Efect de strălucire
            msg.style.transform = "scale(0.9)"; // Îl face cu 5% mai mare când apare
          }} else {{
            msg.textContent = "❌ Deschide caseta de mai jos și copiază manual.";
            msg.style.color = "#E74C3C";
          }}
        }});
      }})();
    </script>
    """
    # Am mărit puțin înălțimea la 60px pentru a nu tăia shadow-ul butonului
    components.html(html, height=60)
