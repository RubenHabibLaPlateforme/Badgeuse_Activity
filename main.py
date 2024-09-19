import google_auth_script
import requests
import atexit
import os
import threading
import time

def read_in_file(nom_fichier):
    """
    Cette fonction lit le texte du fichier spécifié et le renvoie.

    :param nom_fichier: Nom du fichier à lire.
    :return: Contenu du fichier sous forme de chaîne de caractères.
    """
    try:
        # Ouvrir le fichier en mode lecture
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            contenu = fichier.read()
        # print("contenu =", contenu)
        return contenu
    except FileNotFoundError:
        return -1
    except Exception as e:
        return -1


def get_laplateforme_token(token, refresh=False):
    if refresh:
        url = "https://auth.laplateforme.io/refresh"
    else:
        url = "https://auth.laplateforme.io/oauth"


    print("Token pour la requête : ", token)

    # Corps de la requête
    formdata = {"token_id": token}

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        # Faire la requête POST en utilisant form data
        response = requests.post(url, data=formdata, headers=headers)

        if response.status_code == 200:
            print("Réponse reçue :")
            response_data = response.json()
            google_auth_script.write_in_file(
                "auth_token_laplateforme", response_data.get("authtoken"))
            google_auth_script.write_in_file(
                "token_laplateforme", response_data.get("token"))

            print(response.json())
        else:
            print("La requête a échoué avec le statut", response.status_code)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print("Une erreur est survenue lors de la requête :", e)
    return 1


def refresh_token_periodically(interval=15 * 60):
    while True:
        print("Rafraîchissement du token...")
        token_google_id = read_in_file("token_google_id")
        if token_google_id != -1:
            get_laplateforme_token(token_google_id, refresh=True)
        else:
            print(f"Erreur: Token Google ID {token_google_id} introuvable.")

        time.sleep(interval)


def get_data_badges():
    token = read_in_file("token_laplateforme")
    url = f"https://api.laplateforme.io/student?badge=&email="
    headers = {"token": token}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Réponse reçue :")
            response_data = response.json()
            print(response_data)
            # data_badges = [entry['student_email'] for entry in response_data]
            # print("Students List updated:", students_list)
            data_badges = []
            for item in response_data:
                ligne = [item["student_email"], item["student_badge"]]
                data_badges.append(ligne)
            return data_badges
        else:
            print("La requête a échoué avec le statut", response.status_code)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print("Une erreur est survenue lors de la requête :", e)


def delete_tokens():
    # Liste des noms de fichiers à supprimer
    fichiers_a_supprimer = ['token_google_id',
                            'token_laplateforme', 'token.json', 'auth_token_laplateforme']

    # Parcourir chaque fichier dans la liste
    for fichier in fichiers_a_supprimer:
        # Vérifier si le fichier existe
        if os.path.isfile(fichier):
            try:
                os.remove(fichier)  # Supprimer le fichier
                print(f"Le fichier '{fichier}' a été supprimé.")
            except Exception as e:
                print(
                    f"Erreur lors de la suppression du fichier '{fichier}': {e}")
        else:
            print(f"Le fichier '{fichier}' n'existe pas.")


def main():
    # Démarre un thread pour rafraîchir le token toutes les 15 minutes
    refresh_thread = threading.Thread(target=refresh_token_periodically)
    refresh_thread.daemon = True
    refresh_thread.start()

    token_google_id = read_in_file("token_google_id")
    if token_google_id != -1:
        get_laplateforme_token_result = get_laplateforme_token(read_in_file("token_google_id"))
        if get_laplateforme_token_result:
            import menu
            data_badges = get_data_badges()
            print(data_badges)
            menu.create_window(data_badges, read_in_file("token_laplateforme"))
    else:
        google_auth_script.authenticate()
        token_google_id = read_in_file("token_google_id")
        if token_google_id != -1:
            get_laplateforme_token_result = get_laplateforme_token(read_in_file("token_google_id"))
            if get_laplateforme_token_result:
                import menu
                data_badges = get_data_badges()
                print(data_badges)
                menu.create_window(data_badges, read_in_file("token_laplateforme"))

if __name__ == "__main__":
    delete_tokens()
    main()
