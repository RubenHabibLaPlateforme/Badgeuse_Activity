
from datetime import datetime
import os
import sys
from PIL import Image, ImageTk
import csv

class Tools : 
    
    @staticmethod
    def get_resource_path(relative_path):
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            return os.path.join(base_path, relative_path) 

    @staticmethod
    def write_in_file(nom_fichier, texte):

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
            
    @staticmethod        
    def read_in_file(nom_fichier):
        
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
        
    @staticmethod    
    def formate_students_list(students_presents):
        result = ""

        # Parcourir chaque valeur dans le tableau
        for value in students_presents:
            # Ajouter la valeur formatée à la chaîne de caractères résultat
            result += f"&present_students[]={value}"

        if result == "":
            result = "&present_students[]=''"

        return result 
        
    @staticmethod
    def loadLogo():
        def get_resource_path(relative_path):
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            return os.path.join(base_path, relative_path)  
        # Remplace 'path_to_image.png' par le chemin de ton image
        image_path = get_resource_path("assets/logo_laplateforme.jpg")
        original_image = Image.open(image_path)
        
        # Redimensionner l'image (facultatif)
        return ImageTk.PhotoImage(original_image.resize((40, 40)))  # Ajuster la taille selon vos besoins    

    def csv_save(selected_option_unit, selected_option_activity, students_presents):
        
        os.makedirs("logs", exist_ok=True)

        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y_%H-%M")
        selected_option_activity_clean = selected_option_activity.replace(
            "\\", "").replace("\n", "-")

        fichier_nom = f"{date_str}_{selected_option_activity_clean}.csv"

        fichier_chemin = os.path.join("./logs/", fichier_nom)

        try:
            with open(fichier_chemin, mode="w", newline="", encoding="utf-8") as fichier_csv:
                writer = csv.writer(fichier_csv)

                writer.writerow([selected_option_unit])
                writer.writerow([selected_option_activity])

                writer.writerow([])
                for student in students_presents:
                    writer.writerow([student])
                    

        except Exception as e:
            print(f"Erreur lors de la création du fichier log : {str(e)}")