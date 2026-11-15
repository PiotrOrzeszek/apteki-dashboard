"""💊 Polski rynek apteczny — pokazowy dashboard Streamlit, stan 15.11.2026.

Uruchomienie:
    pip install streamlit pandas plotly
    streamlit run apteki_streamlit_research.py

Trzy wykresy są zawsze widoczne w głównym widoku:
1) struktura placówek (pie chart),
2) historyczne przychody WYBRANEJ SPÓŁKI powiązanej z marką,
3) ranking liczby placówek.

Metodologia: wielkość sieci = rozpoznana marka w publicznym katalogu;
przychody = RÓŻNE, KONKRETNE PODMIOTY KRS, a NIE skonsolidowane
przychody marek czy sumy przychodów wszystkich ich aptek.
Żadne brakujące lata nie są interpolowane.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Apteki w Polsce | Data Science", page_icon="💊", layout="wide")

st.caption("💡 Przykład dydaktyczny Python + Pandas + Plotly + Streamlit.")
st.caption("💊 dane statyczne, nie pobierane na żywo")
st.caption("👨🏻‍🎓 prowadzący: Piotr Orzeszek, przedmiot Data Science dla kierunków Matematka i Kognitywistyka")
# Dane: https://raportyapteczne.pl/apteki (spis 20 największych marek)
# Pozostałe nazwy: indywidualne strony sieci katalogu, stan listopad 2026.
SIECI = {
    "DOZ": 1160,
    "Dr.Max": 547,
    "Słoneczna": 425,
    "Gemini": 366,
    "Ziko": 208,
    "Cefarm 36,6": 173,
    "Zdrowit": 164,
    "Prima": 97,
    "Cosmedica": 74,
    "Nowa Farmacja": 70,
    "Super-Pharm": 69,
    "Centrum Zdrowia": 67,
    "Dom Leków": 59,
    "Rodzinna": 59,
    "Hygieia": 59,
    "Wracam do Zdrowia": 50,
    "Stylowe": 45,
    "Zdrowe Ceny": 40,
    "Codzienna": 37,
    "Alba": 37,
    "Dr Zdrowie": 34,
    "Farmacja 24": 32,
    "Hibiskus": 32,
    "Amica": 31,
    "Syrenka": 24,
    "Galen": 16,
    "Medicover": 15,
    "Od Serca": 12,
    "Namex": 10,
}

PLACOWKI_OGOLEM = 12042
# Raporty Apteczne: katalog /apteki oraz strona główna. Na stronie /rankingi
# serwis podaje inne, sprzeczne podsumowanie: 4966 (41,2%). Zachowujemy
# wersję katalogową dla spójności z poprzednim dashboardem: 5417 (45%).
PLACOWKI_SIECIOWE = 5417
assert sum(SIECI.values()) <= PLACOWKI_SIECIOWE <= PLACOWKI_OGOLEM

# Poniżej: przychody OGÓŁEM, w złotych, konkretnej spółki, nie sieci.
# Wszystkie serie: publiczne dane sprawozdawcze KRS zestawione przez BizRaport.
# Nie sumujemy spółek jednej grupy — to wymagałoby konsolidacji i eliminacji
# wzajemnych rozliczeń. Nigdy nie uzupełniamy lat brakujących ekstrapolacją.
# "uwaga": specyficzne ograniczenie interpretacji danej serii.
FINANSE = {
    "Ziko": {
        "spolka": "ZIKO APTEKA sp. z o.o.", "krs": "0000256037",
        "url": "https://www.bizraport.pl/krs/0000256037/ziko-apteka-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 446255327.93, 2020: 479299514.67, 2021: 506013286.27,
                 2022: 584431422.06, 2023: 648312778.42, 2024: 718508248.83,
                 2025: 784885431.03},
        "uwaga": "W grupie ZIKO funkcjonują również inne spółki i franczyzobiorcy.",
    },
    "DOZ": {
        "spolka": "DOZ S.A.", "krs": "0000058632",
        "url": "https://www.bizraport.pl/krs/0000058632/doz-spolka-akcyjna",
        "lata": {2019: 151648022.16, 2020: 293749772.21, 2021: 221973502.07,
                 2022: 277034959.45, 2023: 355509701.54, 2024: 410950506.08,
                 2025: 491831887.25},
        "uwaga": "DOZ S.A. nie wykazuje sprzedaży detalicznej wszystkich placówek pod marką DOZ.",
    },
    "Dr.Max": {
        "spolka": "DR. MAX sp. z o.o.", "krs": "0000237142",
        "url": "https://www.bizraport.pl/krs/0000237142/dr-max-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 93966307.31, 2020: 74922160.61, 2021: 103685019.89,
                 2022: 121671162.67, 2023: 138491739.50, 2024: 173016437.71,
                 2025: 184428035.67},
        "uwaga": "Spółka DR. MAX ma profil zarządczy; nie są to obroty całej sieci aptek Dr.Max.",
    },
    "Słoneczna": {
        "spolka": "APTEKA SŁONECZNA KWIECIEŃ sp.j.", "krs": "0000092547",
        "url": "https://www.bizraport.pl/krs/0000092547/apteka-sloneczna-kwiecien-spolka-jawna",
        "lata": {2019: 158032407.51, 2020: 170968862.56, 2021: 207776954.99,
                 2022: 249800275.25, 2023: 283583789.18, 2024: 315669015.74,
                 2025: 342195073.65},
        "uwaga": "Jedna ze spółek związanych z marką; pod nazwą Słoneczna działa więcej podmiotów.",
    },
    "Gemini": {
        "spolka": "APTEKA GEMINI HÜTTER sp. z o.o.", "krs": "0000582683",
        "url": "https://www.bizraport.pl/krs/0000582683/apteka-gemini-hutter-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 432679052.72, 2020: 450308216.85, 2021: 492587473.81,
                 2022: 555973126.55, 2023: 594010651.24, 2024: 628973273.61,
                 2025: 674873652.54},
        "uwaga": "Tylko jedna ze spółek obsługujących markę Gemini.",
    },
    "Cefarm 36,6": {
        "spolka": "PZF CEFARM-WARSZAWA S.A.", "krs": "0000034561",
        "url": "https://www.bizraport.pl/krs/0000034561/przedsiebiorstwo-zaopatrzenia-farmaceutycznego-cefarm-warszawa-spolka-akcyjna",
        "lata": {2020: 232729000, 2021: 219990000, 2022: 244615000,
                 2023: 249356000, 2024: 266370000, 2025: 305972000},
        "uwaga": "Przychody tej spółki mogą obejmować działalność inną niż sprzedaż detaliczna aptek.",
    },
    "Zdrowit": {
        "spolka": "ZDROWIT S.A.", "krs": "0000704305",
        "url": "https://www.bizraport.pl/krs/0000704305/zdrowit-spolka-akcyjna",
        "lata": {2019: 11239973.51, 2020: 48121238.78, 2021: 71130721.32,
                 2022: 102730805.41, 2023: 139492765.99, 2024: 212974965.26},
        "uwaga": "Spółka holdingowa/usługowa; to NIE jest suma utargów 164 aptek.",
    },
    "Cosmedica": {
        "spolka": "COSMEDICA sp. z o.o.", "krs": "0000159056",
        "url": "https://www.bizraport.pl/krs/0000159056/cosmedica-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 149957045.75, 2020: 142294051.66, 2021: 149288704.89,
                 2022: 177908684.66, 2023: 174994615.16, 2024: 196976845.65},
        "uwaga": "Wyniki tej osoby prawnej, niekoniecznie wszystkich placówek pod marką.",
    },
    "Nowa Farmacja": {
        "spolka": "NOWA FARMACJA sp. z o.o.", "krs": "0000330606",
        "url": "https://www.bizraport.pl/krs/0000330606/nowa-farmacja-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 95416399.98, 2020: 101575341.12, 2021: 108546454.87,
                 2022: 121148692.05, 2023: 125065947.91, 2024: 134284334.48,
                 2025: 140795969.09},
        "uwaga": "Nie są to skonsolidowane przychody całej Grupy Nowa Farmacja.",
    },
    "Super-Pharm": {
        "spolka": "SUPER-PHARM POLAND sp. z o.o.", "krs": "0000083512",
        "url": "https://www.bizraport.pl/krs/0000083512/super-pharm-poland-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2020: 716827718.33, 2021: 733095688.10,
                 2022: 1973673076.62, 2024: 1228116620.22},
        "uwaga": "Seria w tym źródle ma lukę (2023) — nie łączymy punktów przez brakujący rok.",
    },
    "Hygieia": {
        "spolka": "HYGIEIA sp. z o.o.", "krs": "0000244889",
        "url": "https://www.bizraport.pl/krs/0000244889/hygieia-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 31087080.48, 2020: 33074699.49, 2021: 34624397.16,
                 2022: 37396481.05, 2023: 40093051.44, 2024: 42048582.81,
                 2025: 47920052.06},
        "uwaga": "Wybrana spółka o nazwie sieci; katalog marek nie stanowi rejestru grup kapitałowych.",
    },
    "Wracam do Zdrowia": {
        "spolka": "WRACAM DO ZDROWIA 8 sp. z o.o.", "krs": "0000674624",
        "url": "https://www.bizraport.pl/krs/0000674624/wracam-do-zdrowia-8-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 22470425.71, 2020: 25195101.97, 2021: 27355508.82,
                 2022: 31536044.62, 2023: 34284847.22, 2024: 38386806.35,
                 2025: 42000491.56},
        "uwaga": "Spółka prowadząca aptekę internetową pod tą marką, nie łączny obrót sieci.",
    },
    "Dr Zdrowie": {
        "spolka": "DR ZDROWIE S.A.", "krs": "0000010657",
        "url": "https://www.bizraport.pl/krs/0000010657/dr-zdrowie-spolka-akcyjna",
        "lata": {2019: 95712469.76, 2020: 92625524.48, 2021: 106255842.71,
                 2022: 131148633.47, 2023: 145848032.39, 2024: 161298254.40,
                 2025: 174947778.17},
        "uwaga": "Wybrana spółka związana z marką; wynik nie jest udziałem rynkowym sieci.",
    },
    "Syrenka": {
        "spolka": "FARMA SYRENKA sp. z o.o.", "krs": "0000058750",
        "url": "https://www.bizraport.pl/krs/0000058750/farma-syrenka-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 65027743.24, 2020: 62671174.50, 2021: 62469892.38,
                 2022: 68891697.32, 2023: 71387825.69, 2024: 76279330.44},
        "uwaga": "Operator części aptek Syrenka — sieć obejmuje również inne podmioty.",
    },
    "Zdrowe Ceny": {
        "spolka": "ZDROWE CENY sp. z o.o.", "krs": "0000484491",
        "url": "https://www.bizraport.pl/krs/0000484491/zdrowe-ceny-spolka-z-ograniczona-odpowiedzialnoscia",
        "lata": {2019: 43337844.36, 2020: 43809788.83, 2021: 46954760.35,
                 2022: 55307289.91, 2023: 57228267.73, 2024: 60165491.08,
                 2025: 56323959.91},
        "uwaga": "Jedna ze spółek związanych z marką Zdrowe Ceny, a nie pełny obrót franczyzy.",
    },
    "Namex": {
        "spolka": "NAMEX. A. NAMIOTKO. sp.j.", "krs": "0000065338",
        "url": "https://www.bizraport.pl/krs/0000065338/namex-a-namiotko-spolka-jawna",
        "lata": {2019: 67070098.91, 2020: 68868708.45, 2021: 71485821.85,
                 2022: 78995631.84, 2023: 82601809.91},
        "uwaga": "Ostatnie dostępne w tym źródle sprawozdanie: 2023; późniejsze lata pozostają puste.",
    },
}

# Wartości w FINANSE są wielkościami absolutnymi w PLN.
# Podmiot zweryfikowany w materiałach źródłowych pod wskazanym numerem KRS.
# Nie utożsamiaj wyników spółki z obrotami wszystkich aptek pod jej marką.

ZIELONY = "#0AA89E"
GRAFIT = "#18283B"
ZLOTY = "#E9B756"
ROZ = "#EC7388"
FIOLET = "#9478E9"
PALETA = px.colors.qualitative.Dark24 + px.colors.qualitative.Pastel

kolory = {nazwa: PALETA[i] for i, nazwa in enumerate(SIECI)}
kolory.update({
    "Ziko": ZIELONY,
    "Namex": FIOLET,
    "Syrenka": ROZ,
    "Słoneczna": ZLOTY,
    "Pozostałe sieci": "#8496AF",
    "Poza rozpoznanymi sieciami": "#CAD5E2",
})


def liczba(n):
    return f"{n:,.0f}".replace(",", " ")


def kwota_mln(kwota):
    return f"{kwota / 1e6:,.1f}".replace(",", " ").replace(".", ",") + " mln zł"


st.markdown("""
<style>
  .block-container {max-width: 1320px; padding-top: 1.3rem; padding-bottom: 4rem;}
  h1 {letter-spacing: -.035em;}
  h2 {padding-top: 0.4rem; letter-spacing: -.02em;}
  [data-testid="stMetric"] {
    border: 1px solid rgba(108,138,160,.20);
    border-radius: 16px;
    background: rgba(125,145,170,.07);
    padding: 1rem 1.2rem;
  }
  .subtle {color: #8493a5; font-size: .91rem;}
</style>
""", unsafe_allow_html=True)

st.title("💊 Polski rynek apteczny")
st.caption("Od liczby aptek po finanse spółek • przegląd publicznych danych, listopad 2026")

metryka1, metryka2, metryka3 = st.columns(3)
metryka1.metric("Aktywne placówki", liczba(PLACOWKI_OGOLEM))
metryka2.metric("Sieciowe wg katalogu", liczba(PLACOWKI_SIECIOWE))
metryka3.metric("Spółki z danymi finansowymi", len(FINANSE))

# ── 01 / WYKRES KOŁOWY ───────────────────────────────────────────────────────
st.divider()
st.subheader("01 · Struktura rynku aptecznego")
st.caption("Udział liczony według liczby aptek i punktów aptecznych, NIE wartości sprzedaży.")
lewa, prawa = st.columns([1, 2])
with lewa:
    obszar = st.radio(
        "Wybierz punkt odniesienia",
        ["Cały rynek", "Tylko apteki sieciowe"],
        horizontal=False,
    )
with prawa:
    ile = st.slider("Ile sieci pokazać osobno?", 5, len(SIECI), len(SIECI),
                    help="Mniejsze sieci niewidoczne osobno trafiają do kategorii Pozostałe sieci.")

ranking = (pd.DataFrame(SIECI.items(), columns=["Sieć", "Placówki"])
           .sort_values(["Placówki", "Sieć"], ascending=[False, True])
           .reset_index(drop=True))
wybrane = ranking.head(ile).copy()
pozostale = PLACOWKI_SIECIOWE - int(wybrane["Placówki"].sum())
wpisy = wybrane.to_dict("records")
if pozostale > 0:
    wpisy.append({"Sieć": "Pozostałe sieci", "Placówki": pozostale})
if obszar == "Cały rynek":
    wpisy.append({"Sieć": "Poza rozpoznanymi sieciami",
                  "Placówki": PLACOWKI_OGOLEM - PLACOWKI_SIECIOWE})

kolo = pd.DataFrame(wpisy)
kolo["Opis"] = kolo["Placówki"].map(liczba)
suma = PLACOWKI_OGOLEM if obszar == "Cały rynek" else PLACOWKI_SIECIOWE
assert int(kolo["Placówki"].sum()) == suma

fig_kolo = px.pie(kolo, names="Sieć", values="Placówki", color="Sieć",
                  color_discrete_map=kolory, custom_data=["Opis"], hole=0.61)
fig_kolo.update_traces(
    sort=False, textposition="inside", textinfo="percent",
    marker={"line": {"color": "white", "width": 1}},
    hovertemplate="<b>%{label}</b><br>%{customdata[0]} placówek<br>Udział: %{percent}<extra></extra>",
)
fig_kolo.update_layout(
    height=760,
    legend={"title": "Sieci i pozostałe kategorie", "x": 1.02,
            "y": .5, "yanchor": "middle", "font": {"size": 11}},
    margin={"l": 10, "r": 10, "t": 15, "b": 15},
    uniformtext={"minsize": 12, "mode": "hide"},
    annotations=[{"text": f"<b>{liczba(suma)}</b><br>placówek",
                  "x": .5, "y": .5, "showarrow": False,
                  "font": {"size": 20}}],
)
st.plotly_chart(fig_kolo, use_container_width=True, key="rynek_kolowy")
st.caption(
    f"Pozostałe nierozpisane sieci: {liczba(pozostale)} placówek. "
    "Kategoria »poza rozpoznanymi sieciami« nie oznacza, że każda taka apteka "
    "jest niezależna kapitałowo."
)

# ── 02 / HISTORYCZNE PRZYCHODY ───────────────────────────────────────────────
st.divider()
st.subheader("02 · Przychody w czasie")
wybory = ["Ziko"] + [s for s in SIECI if s != "Ziko" and s in FINANSE]
wybrana_siec = st.selectbox("Wybierz sieć apteczną", wybory, index=0,
    help="Lista obejmuje marki, dla których znaleziono dane co najmniej jednej powiązanej spółki.")
sp = FINANSE[wybrana_siec]
serie = pd.DataFrame({"Rok": list(sp["lata"]),
                      "Przychody (mln zł)": [v / 1e6 for v in sp["lata"].values()]})
serie = serie.sort_values("Rok")
start = int(serie["Rok"].min())
koniec = int(serie["Rok"].max())
wszystkie_lata = list(range(start, koniec + 1))
serie_pelne = pd.DataFrame({"Rok": wszystkie_lata}).merge(serie, on="Rok", how="left")

kolor_linii = kolory.get(wybrana_siec, ZIELONY)
fig_przychody = go.Figure()
fig_przychody.add_trace(go.Scatter(
    x=serie_pelne["Rok"], y=serie_pelne["Przychody (mln zł)"],
    mode="lines+markers", connectgaps=False,
    line={"color": kolor_linii, "width": 4, "shape": "linear"},
    marker={"size": 10, "line": {"width": 2, "color": "white"}},
    hovertemplate="<b>%{x}</b><br>%{y:,.1f} mln zł<extra></extra>",
    name="Przychody ogółem",
))
fig_przychody.update_layout(
    height=450, margin={"l": 20, "r": 20, "t": 22, "b": 25},
    showlegend=False, hovermode="x unified",
    xaxis={"title": "Rok sprawozdawczy", "dtick": 1,
           "range": [start - .2, koniec + .2]},
    yaxis={"title": "Przychody ogółem (mln zł)", "rangemode": "tozero", "tickformat": ",.0f"},
)

ostatnia = serie.iloc[-1]
przedostatnia = serie.iloc[-2] if len(serie) >= 2 else None
zmiana_rok = None
if przedostatnia is not None and ostatnia["Rok"] - przedostatnia["Rok"] == 1:
    zmiana_rok = (ostatnia["Przychody (mln zł)"] / przedostatnia["Przychody (mln zł)"] - 1) * 100

metryka_fin1, metryka_fin2 = st.columns([1, 2])
metryka_fin1.metric(f"Przychód za {int(ostatnia['Rok'])}",
                    kwota_mln(ostatnia["Przychody (mln zł)"] * 1e6),
                    delta=f"{zmiana_rok:+.1f}% r/r" if zmiana_rok is not None else None)
with metryka_fin2:
    st.markdown(f"**Podmiot:** {sp['spolka']}")
    st.caption(f"KRS: {sp['krs']} · raportowane lata: {start}–{koniec} · "
               f"Źródło: [BizRaport — dane spółki]({sp['url']})")

st.plotly_chart(fig_przychody, use_container_width=True, key="przychody_czas")
st.warning("⚠️ To przychody **konkretnej spółki (KRS)**, nie przychody całej sieci "
           "aptecznej. Nie porównuj ich bezpośrednio z udziałami w liczbie aptek. "
           + sp["uwaga"], icon="⚠️")

# ── 03 / RANKING LICZBY PLACÓWEK ─────────────────────────────────────────────
st.divider()
st.subheader("03 · Ile placówek mają poszczególne sieci?")
ile_slupkow = st.slider("Sieci w rankingu", 5, len(ranking), 20)
slupki = ranking.head(ile_slupkow).copy()
fig_slupki = px.bar(slupki, x="Placówki", y="Sieć", orientation="h",
                     color="Sieć", color_discrete_map=kolory, text="Placówki")
fig_slupki.update_traces(
    textposition="outside", cliponaxis=False,
    hovertemplate="%{y}: <b>%{x} placówek</b><extra></extra>",
)
fig_slupki.update_layout(
    height=max(520, ile_slupkow * 30 + 110),
    showlegend=False, margin={"l": 10, "r": 65, "t": 15, "b": 20},
    yaxis={"categoryorder": "total ascending", "title": ""},
    xaxis={"title": "Liczba czynnych aptek i punktów aptecznych"},
)
st.plotly_chart(fig_slupki, use_container_width=True, key="ranking_aptek")
st.caption("Dane katalogowe: stan z listopada 2026, klasyfikacja wg marki, a nie właściciela.")

with st.expander("📚 Metodologia, kompletne źródła i tabela do wglądu"):
    st.markdown("""
**Skąd dane o aptekach?**

- [Raporty Apteczne — katalog](https://raportyapteczne.pl/apteki):
  12 042 czynnych placówek, 5 417 sklasyfikowanych jako sieciowe, 20 największych marek;
  dane o pozostałych sieciach pochodzą z podstron poszczególnych marek.
- [Raporty Apteczne — ranking](https://raportyapteczne.pl/rankingi) podaje
  **inne** podsumowanie: 4 966 sieciowych (41,2%). Jest to rozbieżność w serwisie,
  nie pomiar własny; na wykresie przyjmujemy konsekwentnie wariant katalogowy.
- Liczba placówek obejmuje apteki ogólnodostępne i punkty apteczne. Kategoria
  „poza rozpoznanymi sieciami” obejmuje także placówki bez ustalonej marki.

**Skąd dane o przychodach?**

Dane z publicznych sprawozdań KRS, odczytane z serwisu BizRaport.
Zapisane w kodzie wartości to przychody **ogółem** danej osoby prawnej (w PLN),
nie przychody ze sprzedaży wyłącznie leków ani skonsolidowany przychód całej marki.
Nie sumujemy spółek w ramach jednej marki i nie imputujemy brakujących lat.
Jakościowa interpretacja i porównania między różnymi spółkami wymagają ostrożności.

**Źródła danych finansowych dla każdej spółki:**
""")
    for marka, pozycja in FINANSE.items():
        st.markdown(
            f"- **{marka}** — {pozycja['spolka']} "
            f"(KRS {pozycja['krs']}); "
            f"[{min(pozycja['lata'])}–{max(pozycja['lata'])}]({pozycja['url']})"
        )
    st.markdown("**Dodatkowe potwierdzenia związku marka ↔ podmiot:** "
        "[ZIKO — struktura grupy](https://zikoapteka.pl/wp-content/uploads/2022/12/Informacja-o-realizowanej-strategii-podatkowej-Ziko-Apteka.pdf), "
        "[Syrenka — operator](https://www.aptekasyrenka.pl/webpage/kontakt.html), "
        "[Namex — właściciel apteki](https://rejestraptek.pl/apteka/namex-3), "
        "[Cefarm 36,6 — identyfikacja spółki](https://www.rp.pl/biznes/art9776281-sieci-aptek-bronia-sie-placimy-w-polsce-podatki).")
    st.markdown("**Dane do analizy — ostatni dostępny rok dla każdego podmiotu:**")
    tabela = pd.DataFrame([
        {"Marka": marka, "Spółka": info["spolka"], "KRS": info["krs"],
         "Rok": max(info["lata"]),
         "Przychody (mln zł)": round(info["lata"][max(info["lata"])] / 1e6, 2)}
        for marka, info in FINANSE.items()
    ])
    st.dataframe(tabela, hide_index=True, use_container_width=True)
    st.download_button("Pobierz tabelę finansową CSV",
                       data=tabela.to_csv(index=False).encode("utf-8-sig"),
                       file_name="apteki_przychody_podmioty.csv", mime="text/csv")

st.caption("💡 Przykład dydaktyczny Python + Pandas + Plotly + Streamlit · dane statyczne, nie pobierane na żywo")
