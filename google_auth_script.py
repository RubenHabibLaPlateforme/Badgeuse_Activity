import os
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.oauth2.id_token

# Chemin vers le fichier client_secrets.json
CLIENT_SECRETS_FILE = "client_secrets.json"

# Scopes d'accès (modifiez en fonction de vos besoins)
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile']

# Déclaration des variables globales
token_google_id = ''
user_email = ''


def write_in_file(nom_fichier, texte):
    """
    Cette fonction écrit le texte donné dans le fichier spécifié.
    Si le fichier n'existe pas, il est créé.

    :param nom_fichier: Nom du fichier où écrire le texte.
    :param texte: Texte à écrire dans le fichier.
    """
    try:
        # Obtenir le chemin absolu du fichier
        chemin_absolu = os.path.abspath(nom_fichier)

        # Vérifier si le répertoire existe, sinon le créer
        dossier_parent = os.path.dirname(chemin_absolu)
        if not os.path.exists(dossier_parent):
            os.makedirs(dossier_parent)

        # Ouvrir le fichier en mode écriture
        with open(chemin_absolu, 'w', encoding='utf-8') as fichier:
            fichier.write(texte)

        if os.path.exists(chemin_absolu):
            print(
                f"Le fichier {chemin_absolu} a été créé et le texte a été écrit avec succès.")
        else:
            print(
                f"Le fichier {chemin_absolu} n'a pas pu être créé ou le texte n'a pas été écrit.")

    except Exception as e:
        print(
            f"Une erreur est survenue lors de l'écriture dans le fichier {chemin_absolu}: {e}")


# Exemple d'utilisation de la fonction

def authenticate():
    print("Début Auth Google")
    global user_email  # Indiquer que user_email est une variable globale

    creds = None

    # Vérifiez si les informations d'identification existent déjà
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Si aucune information d'identification valide n'existe, effectuez le flux OAuth 2.0
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)  # Spécifiez le port ici

        # Enregistrez les informations d'identification pour les réutiliser ultérieurement
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    user_info_service = build('oauth2', 'v2', credentials=creds)
    user_info = user_info_service.userinfo().get().execute()

    user_email = user_info['email']
    write_in_file("token_google_id", creds.id_token)
    print("Fin Auth Google")

    return creds
