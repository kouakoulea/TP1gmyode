"""
Calcul automatique des résultats des étudiants.
Version 2 : coefficients par matière, moyenne pondérée et saisies sécurisées.
"""

NB_ETUDIANTS = 5
NOTE_MIN = 0
NOTE_MAX = 20
SEUIL_ADMISSION = 10


# =========================================================
# Fonctions de saisie sécurisée
# =========================================================
def saisir_texte(message):
    """Demande un texte non vide (les espaces seuls sont refusés)."""
    while True:
        texte = input(message).strip()
        if texte == "":
            print("  ⚠ Saisie vide. Veuillez entrer une valeur.")
        elif not any(c.isalpha() for c in texte):
            print("  ⚠ Le texte doit contenir au moins une lettre.")
        else:
            return texte


def saisir_texte_unique(message, deja_saisis):
    """Demande un texte non vide qui n'est pas déjà dans la liste (sans tenir compte des majuscules)."""
    deja_minuscules = [t.lower() for t in deja_saisis]
    while True:
        texte = saisir_texte(message)
        if texte.lower() in deja_minuscules:
            print(f"  ⚠ « {texte} » a déjà été saisi. Choisissez un autre nom.")
        else:
            return texte


def saisir_entier(message, minimum, maximum=None):
    """Demande un nombre entier compris entre minimum et maximum."""
    while True:
        saisie = input(message).strip()
        try:
            valeur = int(saisie)
        except ValueError:
            print(f"  ⚠ « {saisie} » n'est pas un nombre entier valide.")
            continue
        if valeur < minimum:
            print(f"  ⚠ La valeur doit être supérieure ou égale à {minimum}.")
        elif maximum is not None and valeur > maximum:
            print(f"  ⚠ La valeur doit être inférieure ou égale à {maximum}.")
        else:
            return valeur


def saisir_reel(message, minimum, maximum):
    """Demande un nombre décimal entre minimum et maximum (accepte la virgule : 12,5)."""
    while True:
        saisie = input(message).strip().replace(",", ".")
        try:
            valeur = float(saisie)
        except ValueError:
            print(f"  ⚠ « {saisie} » n'est pas un nombre valide.")
            continue
        if valeur != valeur or valeur in (float("inf"), float("-inf")):  # rejette nan et inf
            print("  ⚠ Valeur non autorisée.")
        elif valeur < minimum or valeur > maximum:
            print(f"  ⚠ La valeur doit être comprise entre {minimum} et {maximum}.")
        else:
            return valeur


# =========================================================
# Fonctions de calcul et d'affichage
# =========================================================
def calculer_moyenne(notes, coefs):
    """Retourne la moyenne pondérée : somme(note x coef) / somme(coefs)."""
    if len(notes) == 0 or len(notes) != len(coefs):
        raise ValueError("Les listes de notes et de coefficients sont incohérentes.")
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


def afficher_resultat(nom, moyenne):
    mention = obtenir_mention(moyenne)
    decision = "Admis" if moyenne >= SEUIL_ADMISSION else "Ajourné"
    print(f"{nom:<15} | {moyenne:>7.2f} | {mention:<10} | {decision}")


# =========================================================
# Programme principal
# =========================================================
def main():
    print("=== CALCUL DES RÉSULTATS DES ÉTUDIANTS ===\n")

    # 1. Matières et coefficients
    nb_matieres = saisir_entier("Combien de matières : ", 1, 30)
    matieres = []
    coefs = []
    for i in range(nb_matieres):
        matiere = saisir_texte_unique(f"Nom de la matière {i + 1} : ", matieres)
        coef = saisir_entier(f"Coefficient de {matiere} : ", 1, 20)
        matieres.append(matiere)
        coefs.append(coef)

    print("\nRécapitulatif des matières :")
    for matiere, coef in zip(matieres, coefs):
        print(f"  - {matiere} (coef {coef})")

    # 2. Noms des étudiants
    print()
    nom_etudiants = []
    for i in range(NB_ETUDIANTS):
        nom = saisir_texte_unique(f"Nom de l'étudiant {i + 1} : ", nom_etudiants)
        nom_etudiants.append(nom)

    # 3. Notes
    notes = []
    for nom in nom_etudiants:
        print(f"\nNotes de {nom} :")
        notes_etudiant = []
        for matiere in matieres:
            note = saisir_reel(f"  {matiere} : ", NOTE_MIN, NOTE_MAX)
            notes_etudiant.append(note)
        notes.append(notes_etudiant)

    # 4. Résultats
    nb_admis = 0
    nb_ajournes = 0
    print("\n" + "=" * 52)
    print(f"{'Nom':<15} | {'Moyenne':>7} | {'Mention':<10} | Décision")
    print("-" * 52)
    for nom, notes_etudiant in zip(nom_etudiants, notes):
        moyenne = calculer_moyenne(notes_etudiant, coefs)
        afficher_resultat(nom, moyenne)
        if moyenne >= SEUIL_ADMISSION:
            nb_admis += 1
        else:
            nb_ajournes += 1
    print("=" * 52)

    # 5. Bilan
    print(f"Nombre d'étudiants admis   : {nb_admis}")
    print(f"Nombre d'étudiants ajournés : {nb_ajournes}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nSaisie interrompue. Programme arrêté.")
