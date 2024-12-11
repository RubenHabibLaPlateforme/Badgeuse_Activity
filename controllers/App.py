import os
import tkinter as tk
import requests
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import messagebox
import customtkinter as ctk
from controllers.RfidReader import RfidReader
from controllers.Tools import Tools
from controllers.ApiPlateforme import ApiPlateforme
from plyer import notification


class App:

    students_list = []
    students_presents = []
    units = []
    rfiReader = RfidReader()
    tokenPlateforme = ''
    part2_frame = ""
    part3_frame = ""
    list_student_widgets = {}
    present_students_widgets = {}

    def create_window(self, data_badges, token, userInfos):
        

        self.units = self.get_units(
            "https://api.laplateforme.io/unit?unit_code=&unit_id&is_active=1",
            token)
        if self.units != None:
            for unit_code in self.units:
                print(unit_code)
            units_code = [unit["name"] for unit in self.units]
            units_id = [unit["id"] for unit in self.units]

            root = ctk.CTk()
            root.call('tk', 'scaling', 1.0)
            root.title("Gestion des Unités")
            root.configure(bg="#f0f0f0")
            logo = Tools.loadLogo()
            
            # Mettre l'application au premier plan + maximized
            root.state('zoomed')
            root.attributes("-topmost", True)
            
            # Enlève l'attribut après le lancement
            root.after(0, root.attributes, "-topmost", False)            

            root.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(root))

            # Obtenir la taille de l'écran
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # Partie 1 : 10% de la hauteur, toute la largeur
            part1_height = int(screen_height * 0.1)
            part1 = tk.Frame(
                root,
                bg='#2c3e50',
                width=screen_width,
                height=part1_height
            )
            part1.pack(side=tk.TOP, fill=tk.X)

            image_label = tk.Label(part1, image=logo)
            image_label.pack(side=tk.LEFT,  padx=(20, 0))

            # Widgets pour la partie 1
            label_accompagnateur = ctk.CTkLabel(
                part1,
                text="Accompagnateur : " + userInfos.user_name,
                padx=10,
                fg_color='#2c3e50',
                text_color='white',
                font=("Roboto", 14)
            )
            label_accompagnateur.pack(side=tk.LEFT)

            # Case à cocher "obligatoire"
            is_mandatory_var = tk.BooleanVar(value=True)
            mandatory_checkbox = ctk.CTkCheckBox(
                part1,
                text="Obligatoire",
                variable=is_mandatory_var,
                fg_color='#747d8c',
                hover_color='#009432',
                border_color='grey',
                border_width=1,
                text_color='white',
            )

            mandatory_checkbox.pack(side=tk.LEFT, padx=30)

            # Menu déroulant pour les options
            options = ["Activite", "Consultation technique", "How to", "Kick-off", "Soutenance",
                       "Suivi de projet", "Coaching", "Anglais", "Relation\nEntreprises", "Autre"]

            # Pré-sélection de "Activité"
            option_var = tk.StringVar(value=options[0])

            option_menu = ctk.CTkOptionMenu(part1,
                                            values=options,
                                            variable=option_var,
                                            fg_color="#747d8c",
                                            text_color="white",
                                            button_color="#57606f",
                                            button_hover_color="#2f3542"
                                            )

            # Positionner le menu dans la navbar
            option_menu.pack(side=tk.LEFT, padx=10, pady=10)
            # option_menu.pack(side=tk.LEFT, padx=10)

            # Menu déroulant pour les units
            unit_var = tk.StringVar(value=units_code[0])

            unit_menu = ctk.CTkOptionMenu(
                part1,
                variable=unit_var,
                values=units_code,
                fg_color="#aaa69d",
                text_color="white",
                button_color="#84817a",
                button_hover_color="#84817a"
            )

            unit_menu.pack(side=tk.LEFT, padx=10, pady=10)

            unit_menu.pack(side=tk.LEFT, padx=10)

            btn_filtre = ctk.CTkButton(
                part1,
                fg_color="#3498db",
                hover_color="#2980b9",
                text="Filtrer",
                command=lambda:
                    self.on_filter_click(
                        unit_var.get(),
                        canvas
                    )
            )

            btn_filtre.pack(side=tk.LEFT, padx=10)

            btn_valider = ctk.CTkButton(
                part1,
                fg_color="#44bd32",
                hover_color="#009432",
                text="Valider",
                text_color="white",
                command=lambda:
                    self.on_validate_click(
                        unit_var.get(),
                        int(is_mandatory_var.get()),
                        option_var.get(),
                        canvas,
                        userInfos
                    )
            )

            btn_valider.pack(side=tk.LEFT, padx=10, pady=20)

            # Partie 2 : 50% de la largeur, 90% de la hauteur avec barre de défilement
            part2_width = int(screen_width * 0.5)
            part2_height = int(screen_height * 0.9)

            part2_container = ctk.CTkFrame(
                root,
                width=part2_width,
                height=part2_height,
                fg_color="#bdc3c7",
            )
            part2_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(
                part2_container,
                bg='#bdc3c7',
                width=part2_width,
                height=part2_height
            )

            scrollbar = ctk.CTkScrollbar(
                part2_container, orientation="vertical", command=canvas.yview
            )

            scrollbar.pack(side="right", fill="y")

            self.part2_frame = ctk.CTkFrame(canvas, fg_color='#bdc3c7')
            canvas.create_window((10, 0), window=self.part2_frame, anchor="nw")

            def update_scrollregion(event):
                canvas.configure(scrollregion=canvas.bbox("all"))

            def onMouseWheel(event, canvas):
                # Permet de faire défiler la vue en fonction de la molette
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            self.part2_frame.bind("<Configure>", update_scrollregion)

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            canvas.bind_all(
                "<MouseWheel>", lambda event: onMouseWheel(event, canvas))

            # Partie 3 : 50% de la largeur, 90% de la hauteur
            part3_width = int(screen_width * 0.5)
            part3_height = int(screen_height * 0.9)
            self.part3_frame = tk.Frame(root, bg='#7f8c8d', width=part3_width,
                                        height=part3_height, bd=0, relief=tk.GROOVE, pady=10, padx=10)
            self.part3_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            # Empêcher part3 de s'adapter à la taille de ses enfants
            self.part3_frame.pack_propagate(False)

            self.rfiReader.start_rfid_thread(
                self, self.part2_frame, canvas, self.part3_frame, data_badges, self.on_email_click)

            # Lets goo
            root.mainloop()

        else:
            os.remove("temp/auth_token_laplateforme")
            os.remove("temp/token_laplateforme")

            token_google_id = Tools.read_in_file("temp/token_google_id")
            if token_google_id != -1:

                self.tokenPlateforme = ApiPlateforme.get_laplateforme_token(
                    Tools.read_in_file("temp/token_google_id")
                )

                self.create_window(data_badges, Tools.read_in_file(
                    "temp/token_laplateforme"), userInfos)

    def get_student_by_badge(data_listing, card):

        student = ""

        if data_listing:
            
            
            print(len(data_listing))

            index = 0

            while index < len(data_listing):

                row = data_listing[index]
                badge_number = row[1]

                if (badge_number):

                    if int(badge_number) == card:

                        try:
                            badge_number = int(badge_number)
                            print(type(badge_number))
                            if badge_number == card:
                                print("TROUVE APP")
                                student = row[0]
                                break
                        except ValueError:
                            pass
                index += 1

        return student

    def get_units(self, url, token):

        print("-------------")
        print("Token pour la requête : ", token)
        print("-------------")

        headers = {"token": token}
        
        notification.notify(
                title = "Liste des étudiants",
                message = "Chargée avec succès !",
                timeout = 5,
                app_name="Badgeuse la plateforme", 
                app_icon=Tools.get_resource_path("assets/logo_laplateforme_icon.ico"),
        )

        try:
            response = requests.get(url, headers=headers)

            while response.status_code == 402:
                ApiPlateforme.refreshTokenPlateforme()
                headers = {
                    "token": Tools.read_in_file("../temp/token_laplateforme")
                }
                response = requests.request("POST", url, headers=headers)

            if response.status_code == 200:

                response_data = response.json()

                units = [{"id": entry["unit_id"], "name": entry["unit_code"]}
                         for entry in response_data]

                return units

            else:
                notification.notify(
                    title = " ⚠️La requête a échoué avec le statut",
                    message=str(response.text)+": Status " + str(response.status_code),
                    timeout = 5,
                    app_name="Badgeuse la plateforme", 
                    app_icon=Tools.get_resource_path("assets/logo_laplateforme_icon.ico"),
                                
                )

        except requests.exceptions.RequestException as e:
            notification.notify(
                title = " ⚠️Une erreur est survenue lors dela requête :",
                message= e,
                timeout = 5,
                app_name="Badgeuse la plateforme", 
                app_icon=Tools.get_resource_path("assets/logo_laplateforme_icon.ico"),
                                
            )

        return None

    def display_part_2(self,  canvas):
        # Vider la partie 2 de la fenêtre
        for widget in self.part2_frame.winfo_children():
            widget.destroy()

        # Désactiver temporairement la propagation de la taille pendant la création des widgets
        self.part2_frame.pack_propagate(False)

        # Créer une liste pour stocker les frames, afin de les afficher toutes d'un coup
        frames = []

        # Ajouter les student_email à la partie 2
        for entry in self.students_list:
            # email_frame = tk.Frame(self.part2_frame, bg="white", pady=5)
            email_frame = ctk.CTkFrame(self.part2_frame, fg_color='white')
            label = ctk.CTkLabel(email_frame, text=entry,
                                 fg_color='white', text_color='black')
            label.pack(side=tk.LEFT, pady=5, padx=10)

            # Créer une fonction qui capture la valeur actuelle d'entry
            def create_button(email):
                return ctk.CTkButton(
                    email_frame,
                    fg_color="#6ab04c",
                    hover_color="#44bd32",
                    text="Ajouter",
                    text_color="white",
                    command=lambda: self.on_email_click(email)
                )

            v_button = create_button(entry)
            v_button.pack(side=tk.RIGHT, padx=10)
            frames.append(email_frame)
            self.list_student_widgets[entry] = email_frame

        # Afficher tous les frames après leur création
        for frame in frames:
            frame.pack(fill=tk.X, pady=5)

        # Activer à nouveau la propagation de la taille une fois tout ajouté
        self.part2_frame.pack_propagate(True)

        # Mettre à jour le canvas pour s'adapter à la nouvelle taille du contenu
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def on_email_click(self, email, byCard=False):
        if email in self.students_presents:  # Si l'étudiant est déjà dans la liste

            if not byCard:
                self.students_presents.remove(email)
                if email in self.present_students_widgets:

                    self.present_students_widgets[email].destroy()
                    del self.present_students_widgets[email]

                    # Créer un widget pour l'étudiant dans Partie 2
                    self.students_list.append(email)
                    self.add_student_widget_part2(email)
        else:
            self.students_presents.append(email)

            # Créer un widget pour l'étudiant dans Partie 3
            self.add_student_widget_part3(email)

    def on_filter_click(self, selected_option,  canvas):

        selected_id = None
        for unit in self.units:
            if unit["name"] == selected_option:
                selected_id = unit["id"]
                self.students_list = ApiPlateforme.feed_students_list(
                    selected_id)
                self.display_part_2(canvas)
                break

        if selected_id is not None:
            # notification.notify(
            #         title = " ⚠️Une erreur est survenue lors de la requête :",
            #         message= e,
            #         timeout = 10
                                
            # )
            print(f"Nom de l'unité sélectionnée: {selected_option}")
            print(f"ID de l'unité sélectionnée: {selected_id}")
        else:
            print(f"Aucun ID trouvé pour l'unité: {selected_option}")

    def on_validate_click(self, selected_option_unit, is_mandatory, selected_option_activity,  canvas, userInfos):

        print(is_mandatory)

        if selected_option_activity == "Activite":
            messagebox.showinfo(
                "Attention", "Veuillez sélectionner  une activité")
            return

        confirmation = messagebox.askyesno(
            "Confirmation", "Êtes-vous sûr de vouloir valider votre appel ?")

        if not confirmation:
            print("Opération annulée par l'utilisateur.")
            return

        selected_id = None
        for unit in self.units:
            if unit["name"] == selected_option_unit:
                selected_id = unit["id"]
                break

        # print(f"Students présents: {self.students_presents}")
        # print(f"ID de l'unité sélectionnée: {selected_id}")
        # print(f"Nom de l'activité: {selected_option_activity}")
        # print(f"Nom du mail: {userInfos.user_email}")
        
        

        Tools.csv_save(selected_option_unit,
                       selected_option_activity, self.students_presents)
        
        notification.notify(
            title = "Le PDF récapitulatif a été généré",
            message= 'Avec succès',
            timeout = 5,
            app_name="Badgeuse la plateforme", 
            app_icon=Tools.get_resource_path("assets/logo_laplateforme_icon.ico"),
                                
        )

        url = "https://api.laplateforme.io/activity"

        payload = (
            f'activity_type={selected_option_activity}'
            f'&unit_id={selected_id}'
            f'&author={userInfos.user_email}'
            f'&is_mandatory={int(is_mandatory)}'
            f'{Tools.formate_students_list(self.students_presents)}'
        )

        headers = {
            "token": Tools.read_in_file("temp/token_laplateforme")
        }

        print("----------------")
        print(payload)
        print("----------------")

        response = requests.request("POST", url, headers=headers, data=payload)

        while response.status_code == 402:
            ApiPlateforme.refreshTokenPlateforme()
            headers = {
                "token": Tools.read_in_file("temp/token_laplateforme")
            }
            response = requests.request(
                "POST", url, headers=headers, data=payload)

        try:
            response_data = response.json()
            print(f"Réponse de l'API : {response_data}")

            if isinstance(response_data, int):
                # Success pop-up
                messagebox.showinfo(
                    "Succès", "La validation a été faite avec succès !")

                # Vider les listes des étudiants
                self.students_list.clear()
                self.students_presents.clear()

                # Vider les parties part2 et part3
                for widget in self.part2_frame.winfo_children():
                    widget.destroy()
                for widget in self.part3_frame.winfo_children():
                    widget.destroy()

                # Mettre à jour le canvas pour refléter les changements
                canvas.update_idletasks()
                canvas.config(scrollregion=canvas.bbox("all"))

            else:
                messagebox.showerror(
                    "Erreur", "Erreur lors de la validation, quittez le programme et relancez le"
                )
        except ValueError:

            print("Erreur: La réponse de l'API n'est pas au format JSON.")

            messagebox.showerror(
                "Erreur", "Erreur lors de la validation, réponse non JSON. Quittez le programme et relancez le"
            )

    def add_student_widget_part2(self, email):

        student_frame = ctk.CTkFrame(self.part2_frame, fg_color='white')
        student_label = ctk.CTkLabel(
            student_frame, text=email, fg_color='white', text_color='black')
        student_label.pack(side="left", padx=10, pady=5)

        addButton = ctk.CTkButton(student_frame, text="Ajouter", text_color="white", command=lambda: self.on_email_click(
            email), fg_color="#6ab04c", hover_color="#44bd32")
        addButton.pack(side="right", padx=10, pady=5)

        student_frame.pack(fill="x", padx=0, pady=5)

        # Sauvegarder la référence du widget pour suppression future
        self.list_student_widgets[email] = student_frame

    def add_student_widget_part3(self, email):
        # Création d'un label et d'un bouton pour retirer l'étudiant
        student_frame = ctk.CTkFrame(self.part3_frame, fg_color='white')
        student_label = ctk.CTkLabel(
            student_frame, text=email, fg_color='white', text_color='black')
        student_label.pack(side="left", padx=10, pady=5)

        remove_button = ctk.CTkButton(
            student_frame,
            fg_color="#eb4d4b",
            hover_color="#ff7979",
            text="Retirer",
            text_color="white",
            command=lambda: self.on_email_click(email)
        )
        remove_button.pack(side="right", padx=10, pady=5)

        student_frame.pack(fill="x", padx=10, pady=5)

        # Sauvegarder la référence du widget pour suppression future
        self.present_students_widgets[email] = student_frame

        self.remove_student_widget_part2(email)

   

    def remove_student_widget_part2(self, email):
        if email in self.list_student_widgets:
            widget = self.list_student_widgets[email]
            widget.destroy()
            del self.list_student_widgets[email]

    def remove_all_student_widget_part3(self):
        # Créer une liste des emails à supprimer
        emails_to_remove = list(self.present_students_widgets.keys())

        # Itérer sur la liste des emails
        for email in emails_to_remove:
            widget = self.present_students_widgets[email]
            widget.destroy()
            del self.present_students_widgets[email]

    def on_closing(self, root):
        os.remove("temp/auth_token_laplateforme")
        os.remove("temp/token_laplateforme")
        os.remove("temp/token.json")
        os.remove("temp/token_google_id")
        root.destroy()
