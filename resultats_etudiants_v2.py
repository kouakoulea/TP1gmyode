"""
Calcul automatique des résultats des étudiants - version Streamlit.
Lancer en local : streamlit run app.py
"""

import pandas as pd
import streamlit as st

NB_ETUDIANTS = 5
NOTE_MIN = 0.0
NOTE_MAX = 20.0
COEF_MIN = 1
COEF_MAX = 20
SEUIL_ADMISSION = 10


# =========================================================
# Logique métier (identique à la version console)
# =========================================================
def calculer_moyenne(notes, coefs):
    """Moyenne pondérée : somme(note x coef) / somme(coefs)."""
    if len(notes) == 0 or len(notes) != len(coefs):
        raise ValueError("Notes et coefficients incohérents.")
    total_points = 0
    total_coefs = 0
    for note, coef in zip(notes, coefs):
        total_points += note * coef
        total_coefs += coef
    return total_points / total_coefs


def obtenir_mention(moyenne):
    if moyenne >= 16:
        return "Très bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez bien"
    elif moyenne >= 10:
        return "Passable"
    else:
        return "Ajourné"


def obtenir_decision(moyenne):
    return "Admis" if moyenne >= SEUIL_ADMISSION else "Ajourné"


# =========================================================
# Fonctions de validation (remplacent les boucles while de la console)
# =========================================================
def nettoyer_texte(valeur):
    if valeur is None or (isinstance(valeur, float) and pd.isna(valeur)):
        return ""
    return str(valeur).strip()


def valider_noms(noms, quoi):
    """Retourne la liste des erreurs : vide, sans lettre, doublon."""
    erreurs = []
    vus = []
    for i, nom in enumerate(noms, start=1):
        if nom == "":
            erreurs.append(f"{quoi} {i} : le nom est vide.")
        elif not any(c.isalpha() for c in nom):
            erreurs.append(f"{quoi} {i} : « {nom} » doit contenir au moins une lettre.")
        elif nom.lower() in vus:
            erreurs.append(f"{quoi} {i} : « {nom} » est en double.")
        vus.append(nom.lower())
    return erreurs


def valider_matieres(df):
    erreurs = []
    matieres = [nettoyer_texte(m) for m in df["Matière"]]
    if len(matieres) == 0:
        return ["Ajoutez au moins une matière."], [], []
    erreurs += valider_noms(matieres, "Matière")

    coefs = []
    for matiere, coef in zip(matieres, df["Coefficient"]):
        if coef is None or pd.isna(coef):
            erreurs.append(f"Coefficient manquant pour « {matiere or '?'} ».")
            coefs.append(None)
        elif coef != int(coef) or not COEF_MIN <= coef <= COEF_MAX:
            erreurs.append(f"Coefficient de « {matiere} » : entier entre {COEF_MIN} et {COEF_MAX}.")
            coefs.append(None)
        else:
            coefs.append(int(coef))
    return erreurs, matieres, coefs


# =========================================================
# Interface
# =========================================================
st.set_page_config(page_title="Résultats des étudiants", page_icon="🎓", layout="centered")
st.title("🎓 Résultats des étudiants")
st.caption(f"Moyenne pondérée, mention et décision pour {NB_ETUDIANTS} étudiants.")

# ---------- 1. Matières et coefficients ----------
st.header("1. Matières et coefficients")
matieres_defaut = pd.DataFrame({"Matière": ["Mathématiques", "Français"], "Coefficient": [3, 2]})
df_matieres = st.data_editor(
    matieres_defaut,
    num_rows="dynamic",
    width="stretch",
    hide_index=True,
    key="matieres",
    column_config={
        "Matière": st.column_config.TextColumn("Matière", required=True, max_chars=40),
        "Coefficient": st.column_config.NumberColumn(
            "Coefficient", min_value=COEF_MIN, max_value=COEF_MAX, step=1, format="%d", required=True
        ),
    },
)
erreurs_matieres, matieres, coefs = valider_matieres(df_matieres)
for e in erreurs_matieres:
    st.error(e)

# ---------- 2. Noms des étudiants ----------
st.header("2. Étudiants")
colonnes = st.columns(NB_ETUDIANTS)
noms = []
for i, col in enumerate(colonnes):
    noms.append(col.text_input(f"Étudiant {i + 1}", key=f"etudiant_{i}", max_chars=40).strip())
erreurs_noms = valider_noms(noms, "Étudiant")
if any(noms):  # n'affiche les erreurs qu'après le début de la saisie
    for e in erreurs_noms:
        st.error(e)

# ---------- 3. Notes ----------
st.header("3. Notes (sur 20)")
if erreurs_matieres or erreurs_noms:
    st.info("Corrigez les matières et les noms des étudiants pour saisir les notes.")
    st.stop()

# On reconstruit le tableau des notes en conservant ce qui a déjà été saisi
ancien = st.session_state.get("notes_df")
df_notes = pd.DataFrame(index=noms, columns=matieres, dtype="float")
if ancien is not None:
    for nom in noms:
        for matiere in matieres:
            if nom in ancien.index and matiere in ancien.columns:
                df_notes.loc[nom, matiere] = ancien.loc[nom, matiere]

df_notes = st.data_editor(
    df_notes,
    width="stretch",
    key=f"notes_{'|'.join(noms)}_{'|'.join(matieres)}",
    column_config={
        m: st.column_config.NumberColumn(m, min_value=NOTE_MIN, max_value=NOTE_MAX, step=0.25, format="%.2f")
        for m in matieres
    },
)
st.session_state["notes_df"] = df_notes

# Vérification des notes (sécurité supplémentaire au-delà des bornes du tableau)
erreurs_notes = []
for nom in noms:
    for matiere in matieres:
        note = df_notes.loc[nom, matiere]
        if pd.isna(note):
            erreurs_notes.append(f"Note manquante : {nom} en {matiere}.")
        elif not NOTE_MIN <= note <= NOTE_MAX:
            erreurs_notes.append(f"Note invalide : {nom} en {matiere} ({note}).")

# ---------- 4. Résultats ----------
st.header("4. Résultats")
if erreurs_notes:
    manquantes = sum("manquante" in e for e in erreurs_notes)
    if manquantes:
        st.info(f"Il reste {manquantes} note(s) à saisir.")
    for e in erreurs_notes:
        if "invalide" in e:
            st.error(e)
    st.stop()

resultats = []
for nom in noms:
    notes_etudiant = [float(df_notes.loc[nom, m]) for m in matieres]
    moyenne = calculer_moyenne(notes_etudiant, coefs)
    resultats.append(
        {
            "Nom": nom,
            "Moyenne": round(moyenne, 2),
            "Mention": obtenir_mention(moyenne),
            "Décision": obtenir_decision(moyenne),
        }
    )
df_resultats = pd.DataFrame(resultats)

nb_admis = int((df_resultats["Décision"] == "Admis").sum())
nb_ajournes = len(df_resultats) - nb_admis

c1, c2, c3 = st.columns(3)
c1.metric("Admis", nb_admis)
c2.metric("Ajournés", nb_ajournes)
c3.metric("Moyenne de la classe", f"{df_resultats['Moyenne'].mean():.2f}")


def colorer_decision(valeur):
    return "color: #1a7f37; font-weight: 600" if valeur == "Admis" else "color: #cf222e; font-weight: 600"


st.dataframe(
    df_resultats.style.map(colorer_decision, subset=["Décision"]).format({"Moyenne": "{:.2f}"}),
    width="stretch",
    hide_index=True,
)

st.download_button(
    "📥 Télécharger les résultats (CSV)",
    data=df_resultats.to_csv(index=False, sep=";").encode("utf-8-sig"),
    file_name="resultats_etudiants.csv",
    mime="text/csv",
)
