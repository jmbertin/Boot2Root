import pexpect
import time
import itertools
import re

# Chemin vers le fichier exécutable "bomb"
chemin_bomb = "./bomb"

# Fonction pour valider une étape
def valider_etape(session, etape, saisie):
    session.expect_exact(etape, timeout=None)
    session.sendline(saisie)
    time.sleep(0.001)  # Attendre une seconde pour être sûr que la sortie est complète

# Générer toutes les permutations des chiffres de 1 à 6 (en excluant le chiffre 4)
chiffres = [1, 2, 3, 5, 6]
permutations = list(itertools.permutations(chiffres))

# Essayer chaque permutation et valider la dernière étape
combinaisons_testees = 0
combinaison_trouvee = False

for permutation in permutations:
    combinaisons_testees += 1
    # Création d'une session pexpect pour exécuter le programme "bomb"
    session = pexpect.spawn(chemin_bomb)

    # Valider les 5 premières étapes
    valider_etape(session, b"Welcome this is my little bomb", b"Public speaking is very easy.")
    valider_etape(session, b"Phase 1 defused. How about the next one?", b"1 2 6 24 120 720")
    valider_etape(session, b"That's number 2.  Keep going!", b"1 b 214")
    valider_etape(session, b"Halfway there!", b"9")
    valider_etape(session, b"So you got that one.  Try this one.", b"opukmq")
    session.expect_exact(b"Good work!  On to the next...", timeout=None)

    # Envoi de la permutation
    saisie = "4 " + " ".join(str(chiffre) for chiffre in permutation)
    session.sendline(saisie)
    try:
        session.expect("(Curses|BOOM!!!|Congratulations! You've defused the bomb!)", timeout=5)
        sortie = session.before.decode() + session.match.group().decode()
        if "Congratulations! You've defused the bomb!" in sortie:
            print("Combinaison correcte trouvée:", saisie)
            combinaison_trouvee = True
            break
        elif "BOOM!!!" in sortie:
            print("Combinaison incorrecte:", saisie)
        else:
            print("Réponse inattendue:", sortie)

    except pexpect.exceptions.TIMEOUT:
        print("Délai d'attente dépassé")

# Afficher les statistiques
print("Nombre de combinaisons testées:", combinaisons_testees)

if combinaison_trouvee:
    print("La combinaison correcte a été trouvée.")
else:
    print("Aucune combinaison correcte trouvée.")
