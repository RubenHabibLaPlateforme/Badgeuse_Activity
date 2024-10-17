import os
import re
import subprocess
import sys
import pkgutil
import importlib.util


def extraire_dependances(fichier):
    """Extrait les dépendances (modules importés) d'un fichier Python."""
    with open(fichier, 'r') as f:
        contenu = f.read()

    # Regex pour capturer les imports : `import xxx` ou `from xxx import yyy`
    pattern = r'^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)'
    dependances = set(re.findall(pattern, contenu, re.MULTILINE))

    return dependances


def get_version_dependance(dependance):
    """Récupère la version installée d'une dépendance."""
    try:
        # Vérifie d'abord si c'est un module standard Python
        if is_standard_module(dependance):
            return "Module standard (Python)"

        # Utilise `pip show` pour obtenir les infos sur la dépendance
        result = subprocess.run(
            ["pip", "show", dependance], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split()[-1]  # La version est après "Version: "

        # Si `pip show` échoue, essaie de récupérer la version via `pip freeze`
        installed_packages = subprocess.run(
            ["pip", "freeze"], capture_output=True, text=True)
        packages = installed_packages.stdout.splitlines()
        for package in packages:
            if package.lower().startswith(dependance.lower() + "=="):
                return package.split("==")[1]

        return "Version non trouvée"
    except Exception as e:
        return f"Erreur : {str(e)}"


def is_standard_module(module_name):
    """Vérifie si le module est un module standard de Python."""
    if module_name in sys.builtin_module_names:
        return True
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return False
    return spec.origin is None or 'site-packages' not in spec.origin


def generer_fichier_dependances(fichiers):
    """Génère un fichier texte avec les dépendances et leurs versions."""
    all_dependances = set()

    # Extraire les dépendances de chaque fichier
    for fichier in fichiers:
        dependances = extraire_dependances(fichier)
        all_dependances.update(dependances)

    # Ouvrir un fichier texte pour écrire la liste des dépendances
    with open('dependances_versions.txt', 'w') as f:
        for dependance in sorted(all_dependances):
            version = get_version_dependance(dependance)
            f.write(f"{dependance}: {version}\n")

    print("Fichier 'dependances_versions.txt' créé avec succès.")


if __name__ == "__main__":
    # Spécifie les fichiers à analyser
    fichiers_a_analyser = ["main.py", "menu.py"]

    # Génère le fichier des dépendances et de leurs versions
    generer_fichier_dependances(fichiers_a_analyser)
