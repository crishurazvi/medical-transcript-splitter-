import json
import re
import streamlit.components.v1 as components

def copy_button_custom(text_to_copy: str, label: str, dom_id: str) -> None:
    """Buton custom HTML/JS optimizat vizual pentru aspect modern."""
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
      <span id="{safe_id}_msg" style="font-size:14px;color:#27AE60;font-weight:600;"></span>
    </div>

    <script>
      (function() {{
        const btn = document.getElementById("{safe_id}");
        const msg = document.getElementById("{safe_id}_msg");
        if (!btn) return;

        btn.addEventListener("click", async () => {{
          try {{
            await navigator.clipboard.writeText({payload});
            msg.textContent = "✅ Copiat în clipboard!";
            setTimeout(() => {{ msg.textContent = ""; }}, 3000);
          }} catch (e) {{
            msg.style.color = "#E74C3C";
            msg.textContent = "❌ Eroare. Folosește butonul nativ de mai jos.";
          }}
        }});
      }})();
    </script>
    """
    components.html(html, height=55)
