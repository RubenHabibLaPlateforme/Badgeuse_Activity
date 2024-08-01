import tkinter as tk
from PIL import Image, ImageTk

import requests
import main
import google_auth_script
from smartcard.System import readers
from smartcard.util import toHexString
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
import time
import os


students_list = []
students_presents = []


def get_student_by_badge(data_listing, card):
    student = ""
    # print("----------- DATA LISTING ------------")
    # for ligne in data_listing:
    #     print("\t".join(map(str, ligne)))
    # print("----------- FIN DATA LISTING ------------")
    # print("OK")
    # print(data_listing[1])
    if data_listing:
        print(len(data_listing))
        index = 0
        while index < len(data_listing):
            row = data_listing[index]
            badge_number = row[1]
            if (badge_number):
                # print(int(badge_number))
                # print("BADGE == " + badge_number)
                if int(badge_number) == card:
                    try:
                        # badge_number = int(row[1])
                        badge_number = int(badge_number)
                        print(type(badge_number))
                        if badge_number == card:
                            print("TROUVE")
                            student = row[0]
                            break
                    except ValueError:
                        pass
            index += 1

    return student


def lire_fichier_gsheets(url):
    # Définir les scopes et les informations d'identification
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    # Remplacez 'credentials.json' par votre fichier JSON de clés
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scope)

    # Authentification et ouverture de la feuille de calcul
    gc = gspread.authorize(credentials)
    try:
        # Ouvrir la feuille de calcul à partir de l'URL
        workbook = gc.open_by_url(url)
        # Accéder à une feuille spécifique (la première feuille dans cet exemple)
        worksheet = workbook.sheet1
        # Récupérer les données de la feuille de calcul
        data = worksheet.get_all_values()
        # print("GSHEET === ")
        # print(data)
        return data
    except gspread.exceptions.APIError as e:
        print(
            f"Une erreur s'est produite lors de la lecture de la feuille de calcul : {e}")
        return None


def start_rfid_thread(part2_frame, canvas, part3_frame, data_badges):
    thread = threading.Thread(target=read_rfid, args=(
        part2_frame, canvas, part3_frame, data_badges))
    # Le thread s'exécutera en arrière-plan et se terminera lorsque l'application principale se fermera
    thread.daemon = True
    thread.start()


def read_rfid(part2_frame, canvas, part3_frame, data_badges):
    while True:

        # print("READ RFID")
        card_id = 0

        # Recherche des lecteurs de cartes
        card_readers = readers()

        if len(card_readers) == 0:
            return

        reader = card_readers[0]

        try:
            connection = reader.createConnection()
            connection.connect()

            # Lire le numéro de série de la carte RFID
            READ_SERIAL = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            response, sw1, sw2 = connection.transmit(READ_SERIAL)
            if sw1 == 0x90 and sw2 == 0x00:
                # Inverser l'ordre des octets dans la variable response
                response_reversed = response[::-1]
                card_id = int(toHexString(
                    response_reversed).replace(" ", ""), 16)
                print(card_id)
                student_email = get_student_by_badge(data_badges, card_id)
                print(student_email)
                if student_email:
                    on_email_click(student_email, part2_frame,
                                   part3_frame, canvas, -1)  # -1, pour dire que la fonction est appelée via la lecture de carte. De ce fait, l'étudiant ne sera pas rebasculé de la liste de présents à la liste des absents
                    # student_by_badge = get_student_by_badge(data_badges, card_id)

                    # if student_by_badge:
                    #     if student_by_badge in students:
                    #         update_students_valid(
                    #             frame_zone2, frame_zone3, student_by_badge, students, students_valid)

        except Exception as e:
            pass

        finally:
            connection.disconnect()

    # root.after(10000, read_rfid, root)


def display_part_3(part2_frame, canvas, part3_frame):
    global students_presents
    # Vider la partie 2 de la fenêtre
    for widget in part3_frame.winfo_children():
        widget.destroy()
    # Ajouter les student_email à la partie 2
    for entry in students_presents:
        email_frame = tk.Frame(part3_frame, bg="white", pady=5)
        email_frame.pack(fill=tk.X, pady=5)
        label = tk.Label(
            email_frame, text=entry, bg="white", padx=10)
        label.pack(side=tk.LEFT)
        v_button = tk.Button(email_frame, text="V", bg="green", fg="white",
                             command=lambda email=entry: on_email_click(email, part2_frame, part3_frame, canvas, 0))
        v_button.pack(side=tk.RIGHT, padx=10)
    # Mettre à jour le canvas pour s'adapter à la nouvelle taille du contenu
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


def display_part_2(part2_frame, canvas, part3_frame):
    global students_list
    # Vider la partie 2 de la fenêtre
    for widget in part2_frame.winfo_children():
        widget.destroy()
    # Ajouter les student_email à la partie 2
    for entry in students_list:
        email_frame = tk.Frame(part2_frame, bg="white", pady=5)
        email_frame.pack(fill=tk.X, pady=5)
        label = tk.Label(
            email_frame, text=entry, bg="white", padx=10)
        label.pack(side=tk.LEFT)
        v_button = tk.Button(email_frame, text="V", bg="green", fg="white",
                             command=lambda email=entry: on_email_click(email, part2_frame, part3_frame, canvas, 0))
        v_button.pack(side=tk.RIGHT, padx=10)
    # Mettre à jour le canvas pour s'adapter à la nouvelle taille du contenu
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


def refresh_token():
    print("test")


def get_units(url, token):
    print("-------------")
    print("Token pour la requête : ", token)
    print("-------------")

    headers = {"token": token}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Réponse reçue :")
            response_data = response.json()
            units = [{"id": entry["unit_id"], "name": entry["unit_code"]}
                     for entry in response_data]
            return units
        # elif response.status_code == 402:
            # os.remove("auth_token_laplateforme")
            # os.remove("token_laplateforme")

            # token_google_id = main.read_in_file("token_google_id")
            # if token_google_id != -1:
            #     get_laplateforme_token_result = main.get_laplateforme_token(
            #         main.read_in_file("token_google_id"))

            print("La Nouvelle requête a échoué avec le statut",
                  response.status_code)
            print(response.text)
            # get_units(
            #     url,  main.read_in_file("token_laplateforme"))

        else:
            print("La requête a échoué avec le statut", response.status_code)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print("Une erreur est survenue lors de la requête :", e)
    return None


def on_email_click(email, part2_frame, part3_frame, canvas, signal):
    global students_list
    global students_presents

    print(f"Email cliqué : {email}")

    # Supprimer l'email de students_list
    if email in students_list:
        students_list.remove(email)

    # Ajouter l'email à students_presents
        students_presents.append(email)

        # Supprimer l'email de students_list
    elif email in students_presents and signal != -1:
        students_presents.remove(email)

    # Ajouter l'email à students_presents
        students_list.append(email)

    # Trier les deux listes par ordre alphabétique
    students_list.sort()
    students_presents.sort()
    display_part_2(part2_frame, canvas, part3_frame)
    display_part_3(part2_frame, canvas, part3_frame)


def feed_students_list(unit_id):
    global students_list

    token = main.read_in_file("token_laplateforme")
    url = f"https://preprod-api.laplateforme.io/unit/student?student_email=&unit_id={unit_id}"
    print("Token pour la requête : ", token)

    headers = {"token": token}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Réponse reçue :")
            response_data = response.json()
            students_list = [entry['student_email'] for entry in response_data]
            print("Students List updated:", students_list)
        else:
            print("La requête a échoué avec le statut", response.status_code)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print("Une erreur est survenue lors de la requête :", e)


def on_filter_click(selected_option, units, canvas, part2_frame, part3_frame):
    selected_id = None
    for unit in units:
        if unit["name"] == selected_option:
            selected_id = unit["id"]
            feed_students_list(selected_id)
            display_part_2(part2_frame, canvas, part3_frame)
            break

    if selected_id is not None:
        print(f"Nom de l'unité sélectionnée: {selected_option}")
        print(f"ID de l'unité sélectionnée: {selected_id}")
    else:
        print(f"Aucun ID trouvé pour l'unité: {selected_option}")


def formate_students_list():
    result = ""

    # Parcourir chaque valeur dans le tableau
    for value in students_presents:
        # Ajouter la valeur formatée à la chaîne de caractères résultat
        result += f"&present_students[]={value}"

    return result


def on_validate_click(selected_option_unit, selected_option_activity, units, canvas, scrollable_frame, part3_frame):
    selected_id = None
    for unit in units:
        if unit["name"] == selected_option_unit:
            selected_id = unit["id"]
            # feed_students_list(selected_id)
            # display_part_2(scrollable_frame, canvas, part3_frame)
            break

    print(f"Students présents: {students_presents}")
    print(f"ID de l'unité sélectionnée: {selected_id}")
    print(f"Nom de l'activité: {selected_option_activity}")
    print(f"Nom du mail: {google_auth_script.user_email}")

    url = "https://preprod-api.laplateforme.io/activity"

    # data = {
    #     "present_students": students_presents,  # Obligatoire, chaîne de caractères
    #     "activity_type": selected_option_activity,  # Obligatoire, chaîne de caractères
    #     "is_mandatory": 1,                      # Obligatoire, booléen
    #     "unit_id": selected_id,                    # Obligatoire, nombre
    #     "author": google_auth_script.user_email,   # Obligatoire, chaîne de caractères
    # }
    payload = 'activity_type='+selected_option_activity + \
        '&unit_id='+str(selected_id) + \
        '&author='+google_auth_script.user_email + \
        '&is_mandatory='+str(1) + \
        formate_students_list()
    # En-têtes HTTP (Headers)
    headers = {
        "token": main.read_in_file("token_laplateforme")

    }
    print("----------------")
    print(payload)

    print("----------------")

    response = requests.request("POST", url, headers=headers, data=payload)
    print(f"Réponse de l'API : {response.json()}")


def create_window(data_badges, token):
    global students_list

    print("DEBUT CREATE WINDOW")

    units = get_units(
        "https://preprod-api.laplateforme.io/unit?unit_code=&unit_id&is_active=1",
        token)
    print(units)
    if units != None:
        for unit_code in units:
            print(unit_code)
        units_code = [unit["name"] for unit in units]
        units_id = [unit["id"] for unit in units]

        root = tk.Tk()
        root.title("Gestion des Unités")
        root.configure(bg="#f0f0f0")
        img = Image.open("logo_laplateforme.jpg")
        tk_img = ImageTk.PhotoImage(img)

        # Obtenir la taille de l'écran
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Partie 1 : 10% de la hauteur, toute la largeur
        part1_height = int(screen_height * 0.1)
        part1 = tk.Frame(root, bg='#2c3e50', width=screen_width,
                         height=part1_height)
        part1.pack(side=tk.TOP, fill=tk.X)

        # Widgets pour la partie 1
        label_accompagnateur = tk.Label(
            part1, text="Accompagnateur : " + google_auth_script.user_email,
            padx=10, bg='#2c3e50', fg='white', font=("Helvetica", 12, "bold"))
        label_accompagnateur.pack(side=tk.LEFT)

        # Menu déroulant pour les options
        options = ["Activite", "Consultation technique", "How to", "Kick-off", "Soutenance",
                   "Suivi de projet", "Coaching", "Anglais", "Relation\nEntreprises", "Autre"]
        # Pré-sélection de "Activité"
        option_var = tk.StringVar(value=options[0])
        option_menu = tk.OptionMenu(part1, option_var, *options)
        option_menu.configure(bg='#34495e', fg='white')
        option_menu.pack(side=tk.LEFT, padx=10)

        # Menu déroulant pour les units
        unit_var = tk.StringVar(value=units_code[0])
        unit_menu = tk.OptionMenu(part1, unit_var, *units_code)
        unit_menu.configure(bg='#34495e', fg='white')
        unit_menu.pack(side=tk.LEFT, padx=10)

        # Bouton Filtrer
        btn_filtre = tk.Button(part1, text="Filtrer", padx=10, command=lambda: on_filter_click(
            unit_var.get(), units, canvas, scrollable_frame, part3), bg='#27ae60', fg='white')
        btn_filtre.pack(side=tk.LEFT, padx=10)

        # Bouton Valider l'appel
        btn_valider = tk.Button(part1, text="Valider", padx=10, command=lambda: on_validate_click(
            unit_var.get(), option_var.get(), units, canvas, scrollable_frame, part3), bg='#27ae60', fg='white')
        btn_valider.pack(side=tk.LEFT, padx=10)

        # Partie 2 : 50% de la largeur, 90% de la hauteur avec barre de défilement
        part2_width = int(screen_width * 0.5)
        part2_height = int(screen_height * 0.9)

        part2_container = tk.Frame(
            root, width=part2_width, height=part2_height, bg="#ecf0f1", bd=2, relief=tk.GROOVE)
        part2_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(part2_container, bg='#ecf0f1',
                           width=part2_width, height=part2_height)
        scrollbar = tk.Scrollbar(
            part2_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", update_scrollregion)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)

        # Partie 3 : 50% de la largeur, 90% de la hauteur
        part3_width = int(screen_width * 0.5)
        part3_height = int(screen_height * 0.9)
        part3 = tk.Frame(root, bg='#bdc3c7', width=part3_width,
                         height=part3_height, bd=2, relief=tk.GROOVE)
        part3.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Empêcher part3 de s'adapter à la taille de ses enfants
        part3.pack_propagate(False)

        start_rfid_thread(scrollable_frame, canvas, part3, data_badges)

        # read_rfid()

        # Lancer la boucle principale

        root.mainloop()
    else:
        os.remove("auth_token_laplateforme")
        os.remove("token_laplateforme")

        token_google_id = main.read_in_file("token_google_id")
        if token_google_id != -1:
            get_laplateforme_token_result = main.get_laplateforme_token(
                main.read_in_file("token_google_id"))
            create_window(data_badges, main.read_in_file("token_laplateforme"))