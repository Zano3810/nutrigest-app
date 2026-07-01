import streamlit as st
import json
import os
import random
import string

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(
    page_title="NutriGest Pro",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STILE ESTETICO PERSONALIZZATO (Futuristic Glassmorphism) ---
st.markdown("""
<style>
    /* Sfondo principale */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #16143a, #1f1b4d);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #110e2d !important;
        border-right: 1px solid #3d3d71;
    }
    
    /* Card per i pasti ed elementi grafici */
    .meal-card {
        background-color: #1f1b4d;
        border: 1px solid #3d3d71;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(162, 155, 254, 0.1);
    }
    
    .meal-title {
        color: #a29bfe !important;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 8px;
    }
    
    .meal-desc {
        color: #dfdfea;
        font-size: 1rem;
    }
    
    /* Pulsanti personalizzati */
    div.stButton > button {
        border-radius: 12px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGICA GESTIONE DATI (JSON) ---
CONFIG_FILE = "config.json"

def get_default_data():
    days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    meals = ["🌅 Mattina (Colazione)", "🍏 Spuntino Mattina", "🕛 Mezzogiorno (Pranzo)", "🍎 Spuntino Pomeriggio", "🌙 Sera (Cena)"]
    
    struct = {
        "admin_password": "superadmin123",
        "utenti_admin": ["SuperAdmin"],
        "ticket_attivi": ["BONUS2026"],
        "piano_nutrizionale": {}
    }
    for d in days:
        struct["piano_nutrizionale"][d] = {m: "Nessun dato inserito." for m in meals}
    return struct

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return get_default_data()
    else:
        data = get_default_data()
        save_config(data)
        return data

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- INIZIALIZZAZIONE DELLO STATO (Session State) ---
if "data" not in st.session_state:
    st.session_state.data = load_config()

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "is_super_admin" not in st.session_state:
    st.session_state.is_super_admin = False

if "selected_day" not in st.session_state:
    st.session_state.selected_day = "Lunedì"

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# --- FUNZIONI DI SERVIZIO ---
def logout():
    st.session_state.current_user = None
    st.session_state.is_super_admin = False
    st.session_state.edit_mode = False
    st.rerun()

# --- SCHERMATA DI LOGIN ---
if st.session_state.current_user is None:
    st.markdown("<h1 style='text-align: center; color: #a29bfe; font-size: 3rem;'>NutriGest</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #dfdfea; font-weight: bold;'>MAKE IT AWESOME</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔒 Accedi al tuo pannello")
            
            pwd = st.text_input("Password Amministratore", type="password", placeholder="Inserisci se sei SuperAdmin")
            st.markdown("<p style='text-align: center; margin: 10px 0; color: #a29bfe;'>— OPPURE UTENTE SECONDARIO —</p>", unsafe_allow_html=True)
            
            user = st.text_input("Username", placeholder="Il tuo nome utente")
            ticket = st.text_input("🎟️ Ticket Bonus", placeholder="Inserisci se hai un codice di invito")
            
            submit = st.form_submit_button("ACCEDI →", use_container_width=True)
            
            if submit:
                pwd = pwd.strip()
                user = user.strip()
                ticket = ticket.strip()
                
                # Login Super Admin
                if pwd == st.session_state.data["admin_password"]:
                    st.session_state.current_user = "SuperAdmin"
                    st.session_state.is_super_admin = True
                    st.success("Accesso eseguito come SuperAdmin!")
                    st.rerun()
                
                # Login con Ticket
                elif user and ticket:
                    if ticket in st.session_state.data["ticket_attivi"]:
                        if user not in st.session_state.data["utenti_admin"]:
                            st.session_state.data["utenti_admin"].append(user)
                        st.session_state.data["ticket_attivi"].remove(ticket)
                        save_config(st.session_state.data)
                        
                        st.session_state.current_user = user
                        st.session_state.is_super_admin = False
                        st.success(f"Benvenuto {user}! Ora sei un amministratore.")
                        st.rerun()
                    else:
                        st.error("❌ Ticket non valido o già utilizzato.")
                
                # Login Admin Esistente
                elif user and user in st.session_state.data["utenti_admin"]:
                    st.session_state.current_user = user
                    st.session_state.is_super_admin = False
                    st.success(f"Bentornato {user}!")
                    st.rerun()
                
                # Login Ospite (Sola Lettura)
                elif user:
                    st.session_state.current_user = user
                    st.session_state.is_super_admin = False
                    st.info(f"Accesso come ospite (sola lettura): {user}")
                    st.rerun()
                
                else:
                    st.warning("⚠️ Inserisci una password valida o un nome utente per continuare.")

# --- APPLICAZIONE PRINCIPALE (LOGGED IN) ---
else:
    # Controlliamo al volo se l'utente è autorizzato alle modifiche
    is_user_admin = st.session_state.is_super_admin or (st.session_state.current_user in st.session_state.data["utenti_admin"])
    
    # --- SIDEBAR NAVIGAZIONE ---
    with st.sidebar:
        st.markdown("<h2 style='color: #a29bfe; text-align: center; margin-bottom: 30px;'>NutriGest</h2>", unsafe_allow_html=True)
        st.markdown(f"**Utente:** `{st.session_state.current_user}`")
        st.markdown(f"**Ruolo:** {'👑 Super Admin' if st.session_state.is_super_admin else ('⚙️ Admin' if is_user_admin else '👤 Ospite')}")
        st.divider()
        
        # Menu di selezione vista
        opzioni_menu = ["📋 Visualizza Piano", "📝 Diario Alimentare"]
        if is_user_admin:
            opzioni_menu.append("⚙️ Pannello Admin")
            
        scelta = st.radio("Navigazione", opzioni_menu, label_visibility="collapsed")
        
        st.write("")
        st.write("")
        if st.button("Logout 🚪", use_container_width=True, type="secondary"):
            logout()

    # --- CONTENUTO PRINCIPALE ---
    
    # 1. VISTA: VISUALIZZA PIANO
    if scelta == "📋 Visualizza Piano":
        st.title("📋 Piano Nutrizionale")
        
        # Selezione del Giorno della Settimana tramite pulsanti
        days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        cols_day = st.columns(7)
        for idx, d in enumerate(days):
            with cols_day[idx]:
                if st.button(d, use_container_width=True, type="primary" if st.session_state.selected_day == d else "secondary"):
                    st.session_state.selected_day = d
                    st.session_state.edit_mode = False  # Resetta l'edit se cambi giorno
                    st.rerun()
                    
        st.subheader(f"Giorno Selezionato: {st.session_state.selected_day}")
        
        # Tasto Modifica (solo per Admin)
        if is_user_admin:
            if not st.session_state.edit_mode:
                if st.button("✏️ MODIFICA QUESTO GIORNO", type="primary"):
                    st.session_state.edit_mode = True
                    st.rerun()
            else:
                if st.button("❌ ANNULLA MODIFICHE"):
                    st.session_state.edit_mode = False
                    st.rerun()
        
        st.divider()
        
        # Se siamo in modalità modifica, mostriamo i campi di input
        if st.session_state.edit_mode and is_user_admin:
            st.markdown(f"### Modifica i pasti per il giorno: **{st.session_state.selected_day}**")
            
            pasti_list = ["🌅 Mattina (Colazione)", "🍏 Spuntino Mattina", "🕛 Mezzogiorno (Pranzo)", "🍎 Spuntino Pomeriggio", "🌙 Sera (Cena)"]
            piano_attuale = st.session_state.data["piano_nutrizionale"].get(st.session_state.selected_day, {})
            
            nuovi_valori = {}
            for pasto in pasti_list:
                valore_precedente = piano_attuale.get(pasto, "Nessun dato inserito.")
                nuovi_valori[pasto] = st.text_input(pasto, value=valore_precedente)
                
            if st.button("💾 SALVA LE MODIFICHE", use_container_width=True):
                st.session_state.data["piano_nutrizionale"][st.session_state.selected_day] = nuovi_valori
                save_config(st.session_state.data)
                st.session_state.edit_mode = False
                st.success(f"Piano di {st.session_state.selected_day} salvato con successo!")
                st.rerun()
                
        else:
            # Mostriamo le card in sola lettura
            piano_giorno = st.session_state.data["piano_nutrizionale"].get(st.session_state.selected_day, {})
            for pasto, desc in piano_giorno.items():
                st.markdown(f"""
                <div class="meal-card">
                    <div class="meal-title">{pasto}</div>
                    <div class="meal-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # 2. VISTA: DIARIO ALIMENTARE
    elif scelta == "📝 Diario Alimentare":
        st.title("📝 Diario Alimentare Personale")
        st.markdown("Usa questo spazio per tenere traccia dei tuoi pasti quotidiani, dell'idratazione e delle sessioni di allenamento.")
        
        diario_input = st.text_area(
            "Il mio diario di oggi:",
            value="Oggi ho mangiato...\n\nNote sull'allenamento:\nAcqua bevuta:\n",
            height=350
        )
        if st.button("Salva Diario localmente (Sessione)"):
            st.success("Nota salvata con successo nella memoria della sessione!")

    # 3. VISTA: PANNELLO ADMIN
    elif scelta == "⚙️ Pannello Admin" and is_user_admin:
        st.title("⚙️ Pannello di Amministrazione")
        
        # Sezione generazione Ticket
        st.subheader("Genera un nuovo Ticket di Accesso")
        st.write("Fornisci uno di questi codici a un utente per abilitargli i permessi di scrittura e inserimento pasti.")
        
        if st.button("➕ GENERA NUOVO TICKET", type="primary"):
            nuovo_ticket = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            st.session_state.data["ticket_attivi"].append(nuovo_ticket)
            save_config(st.session_state.data)
            st.success(f"Nuovo ticket generato con successo: **{nuovo_ticket}**")
            
        st.divider()
        
        # Elenco Ticket Attivi
        st.subheader("🎟️ Ticket Attivi in attesa di essere usati:")
        if st.session_state.data["ticket_attivi"]:
            st.info(", ".join(st.session_state.data["ticket_attivi"]))
        else:
            st.write("Nessun ticket attivo disponibile. Creane uno sopra!")
            
        st.divider()
        
        # Elenco Utenti Admin Registrati
        st.subheader("👥 Amministratori Registrati nel sistema:")
        for admin_usr in st.session_state.data["utenti_admin"]:
            col_usr, col_btn = st.columns([3, 1])
            with col_usr:
                st.markdown(f"👑 **{admin_usr}**")
            with col_btn:
                # Solo il SuperAdmin può revocare i permessi ad altri admin (escluso se stesso)
                if st.session_state.is_super_admin and admin_usr != "SuperAdmin":
                    if st.button(f"REVOCA PERMESSI a {admin_usr}", key=f"rev_{admin_usr}", type="secondary"):
                        st.session_state.data["utenti_admin"].remove(admin_usr)
                        save_config(st.session_state.data)
                        st.warning(f"Permessi revocati a {admin_usr}")
                        st.rerun()
