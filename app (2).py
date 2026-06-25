"""
APLICATIE SIMPLA - Monitorizare productie panouri fotovoltaice
================================================================

Ce face aplicatia (in cuvinte simple):
1. Genereaza (simuleaza) date despre cat de multa energie produce un panou
   fotovoltaic, zi de zi, in functie de cate ore a fost soare.
   ALTERNATIV: poti incarca un fisier CSV cu date reale/proprii.
2. Calculeaza media, valoarea minima/maxima si o eroare (diferenta) intre
   energia "ideala" (teoretica) si energia produsa efectiv.
3. Afiseaza un grafic cu evolutia productiei de energie.
4. Face o predictie simpla pentru ziua urmatoare, folosind media ultimelor
   7 zile (asa numita "medie mobila").

Cum se ruleaza:
    pip install -r requirements.txt
    streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------
# Configurare pagina
# -----------------------------------------------------------------------
st.set_page_config(page_title="Monitorizare panouri fotovoltaice", page_icon="☀️")

st.title("☀️ Monitorizare panouri fotovoltaice")
st.write(
    "Aplicatie simpla de monitorizare a productiei de energie a unui panou "
    "fotovoltaic: date simulate sau dintr-un fisier, statistici, grafic si "
    "o predictie simpla pentru ziua urmatoare."
)


# -----------------------------------------------------------------------
# PASUL 1: Obtinerea datelor (simulate sau dintr-un fisier CSV)
# -----------------------------------------------------------------------
st.sidebar.header("1. Sursa de date")
sursa = st.sidebar.radio("Alege sursa de date:", ["Date simulate", "Incarca fisier CSV"])

if sursa == "Date simulate":
    # Parametri simpli, alesi de utilizator
    nr_zile = st.sidebar.slider("Numar de zile simulate", 10, 60, 30)
    putere_panou_kw = st.sidebar.number_input("Puterea panoului (kW)", 0.5, 20.0, 5.0, 0.5)

    # Simulam, pentru fiecare zi, un numar aleator de "ore de soare" (intre 2 si 10)
    np.random.seed(1)  # pentru ca rezultatele sa fie aceleasi de fiecare data
    ore_de_soare = np.random.uniform(2, 10, nr_zile)

    # Energia teoretica ("ideala") = ore de soare x puterea panoului
    energie_teoretica = ore_de_soare * putere_panou_kw

    # Energia reala produsa este mai mica decat cea teoretica, din cauza
    # pierderilor (praf pe panou, caldura, cabluri, etc.) -> simulam ~10-15% pierderi
    pierderi = np.random.uniform(0.10, 0.20, nr_zile)
    energie_reala = energie_teoretica * (1 - pierderi)

    zile = pd.date_range(end=pd.Timestamp.today(), periods=nr_zile)
    df = pd.DataFrame({
        "data": zile,
        "ore_soare": np.round(ore_de_soare, 1),
        "energie_teoretica_kwh": np.round(energie_teoretica, 2),
        "energie_reala_kwh": np.round(energie_reala, 2),
    })

else:
    fisier = st.sidebar.file_uploader("Incarca fisier CSV", type=["csv"])
    st.sidebar.caption(
        "Fisierul trebuie sa aiba coloanele: data, ore_soare, "
        "energie_teoretica_kwh, energie_reala_kwh"
    )
    if fisier is None:
        st.info("Incarca un fisier CSV din bara laterala pentru a continua.")
        st.stop()
    df = pd.read_csv(fisier)
    df["data"] = pd.to_datetime(df["data"])


# -----------------------------------------------------------------------
# PASUL 2: Afisarea datelor
# -----------------------------------------------------------------------
st.subheader("📋 Datele monitorizate")
st.dataframe(df, use_container_width=True)


# -----------------------------------------------------------------------
# PASUL 3: Calcule simple - medie, minim, maxim, eroare
# -----------------------------------------------------------------------
st.subheader("📊 Statistici")

medie = df["energie_reala_kwh"].mean()
minim = df["energie_reala_kwh"].min()
maxim = df["energie_reala_kwh"].max()

# Eroarea = cat de mult difera, in medie, energia reala fata de cea teoretica
eroare_medie = (df["energie_teoretica_kwh"] - df["energie_reala_kwh"]).mean()
eroare_procent = (eroare_medie / df["energie_teoretica_kwh"].mean()) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Energie medie produsa", f"{medie:.2f} kWh")
col2.metric("Minim", f"{minim:.2f} kWh")
col3.metric("Maxim", f"{maxim:.2f} kWh")
col4.metric("Eroare medie (pierderi)", f"{eroare_medie:.2f} kWh ({eroare_procent:.1f}%)")

st.caption(
    "Eroarea reprezinta diferenta medie dintre energia teoretica (ideala) si "
    "cea produsa efectiv - arata cat de eficient functioneaza sistemul."
)


# -----------------------------------------------------------------------
# PASUL 4: Grafic cu evolutia productiei
# -----------------------------------------------------------------------
st.subheader("📈 Grafic - evolutia productiei de energie")

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(df["data"], df["energie_teoretica_kwh"], label="Energie teoretica (ideala)", linestyle="--", color="tab:blue")
ax.plot(df["data"], df["energie_reala_kwh"], label="Energie reala produsa", color="tab:orange")
ax.set_xlabel("Data")
ax.set_ylabel("Energie (kWh)")
ax.legend()
ax.grid(alpha=0.3)
fig.autofmt_xdate()
st.pyplot(fig)


# -----------------------------------------------------------------------
# PASUL 5: Predictie simpla pentru ziua urmatoare (medie mobila)
# -----------------------------------------------------------------------
st.subheader("🔮 Predictie pentru ziua urmatoare")

n_zile_medie = 7 if len(df) >= 7 else len(df)
predictie = df["energie_reala_kwh"].tail(n_zile_medie).mean()

st.success(
    f"Pe baza mediei ultimelor {n_zile_medie} zile, energia estimata pentru "
    f"ziua urmatoare este de **{predictie:.2f} kWh**."
)
st.caption(
    "Metoda folosita se numeste 'medie mobila': presupunem ca ziua urmatoare "
    "va fi asemanatoare cu media zilelor recente."
)
