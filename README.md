# Smart Restaurant Management System

## 🎨 Interfață Web Interactivă

### Instalare

```bash
pip3 install -r requirements.txt
```

### Rulare

#### Opțiunea 1: Interfață Web (RECOMANDAT) 🌐
```bash
python3 web_interface.py
```
Apoi deschide în browser: **http://localhost:5000**

#### Opțiunea 2: Consolă
```bash
python3 main_simulation.py
```

## 🖥️ Caracteristici Interfață Web

### Stânga: 💬 Communication Log
- Vezi în timp real toate mesajele dintre agenți
- Culori diferite pentru fiecare tip de agent:
  - 🔵 Client (albastru)
  - 🟢 Host (verde)
  - 🟡 Waiter (galben)
  - ✅ Success (verde deschis)
  - ⚠️ Warning (roșu)

### Centru: 🪑 Restaurant Tables
- 10 mese afișate vizual
- ✅ Verde = liber
- 🍽️ Galben = ocupat
- Vezi ID-ul clientului la fiecare masă

### Dreapta: ⏳ Waiting List
- Lista clienților care așteaptă
- Actualizare în timp real
- Se șterge automat când primesc masă

## 🎮 Controale

- **➕ Add Customer** - Adaugă un client nou
- **▶️ Start** - Pornește simularea automată
- **⏸️ Stop** - Oprește simularea
- **🔄 Reset** - Resetează tot

## 📊 Statistici Live

- Total Customers
- Seated (câți mănâncă)
- Available Tables
- Waiting (în waiting list)

## Ce face?

Simulează un restaurant cu 3 tipuri de agenți:
- **HostAgent** - gestionează mesele și alocă clienților
- **CustomerAgent** - vin clienți, cer mese, mănâncă, pleacă
- **WaiterAgent** - iau comenzi, servesc mâncarea

## Fișiere

- `web_interface.py` - Server Flask pentru interfață
- `restaurant_agents.py` - Definițiile agenților
- `restaurant_model.py` - Modelul MESA
- `main_simulation.py` - Varianta consolă
- `templates/index.html` - Interfața web
- `requirements.txt` - Dependențe
