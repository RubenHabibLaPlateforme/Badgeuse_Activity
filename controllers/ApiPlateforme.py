from controllers.Tools import Tools
import requests
import os
from plyer import notification


class ApiPlateforme:   
 

    @staticmethod
    def get_laplateforme_token(token):

        url = "https://auth.laplateforme.io/oauth"

        print("Token pour la requête : ", token)

        # Corps de la requête
        formdata = {"token_id": token}

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:

            response = requests.post(url, data=formdata, headers=headers)

            if response.status_code == 200:

                response_data = response.json()

                if 'error' not in response_data:
                    print("token plateforme récup avec succès !")
                    Tools.write_in_file(
                        "temp/auth_token_laplateforme", response_data.get("authtoken"))
                    Tools.write_in_file(
                        "temp/token_laplateforme", response_data.get("token"))
                else:
                    notification.notify(
                                title = "Erreur dans la réponse de API plateforme",
                                message = response_data["error"],
                                timeout = 6,
                                app_name="Badgeuse la plateforme", 
                                app_icon=Tools.get_resource_path("assets/logo_laplateforme.jpg"),
                                
                    )
                    
                    return 0
            else:
                notification.notify(
                    title = "La requête a échoué avec le statut",
                    message=str(response.text)+": Status " + str(response.status_code),
                    timeout = 6,
                    app_name="Badgeuse la plateforme", 
                    app_icon=Tools.get_resource_path("assets/logo_laplateforme.jpg"),
                                
                )
                
                return 0
        except requests.exceptions.RequestException as e:
            
            notification.notify(
                title = "Une erreur est survenue lors de la requête de récupération du token",
                message = e,
                timeout = 6,
                app_name="Badgeuse la plateforme", 
                app_icon=Tools.get_resource_path("assets/logo_laplateforme.jpg"),
                            
            )
        return 1

    @staticmethod
    def get_data_badges():

        token = Tools.read_in_file("temp/token_laplateforme")
        url = f"https://api.laplateforme.io/student?badge=&email="
        headers = {"token": token}
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                
                print("Réponse reçue get_data_badges:")
                response_data = response.json()                
                data_badges = []
                for item in response_data:
                    print(item)
                    ligne = [item["student_email"], item["student_badge"]]
                    data_badges.append(ligne)
                return data_badges
            else:
                notification.notify(
                    title = " ⚠️La requête a échoué avec le statut",
                    message=str(response.text)+": Status " + str(response.status_code),
                    timeout = 6,
                    app_name="Badgeuse la plateforme", 
                    app_icon=Tools.get_resource_path("assets/logo_laplateforme.jpg"),
                                
                )
                
        except requests.exceptions.RequestException as e:
            
            notification.notify(
                title = "⚠️ Une erreur est survenue lors de la requête de get_data_badges",
                message = e,
                timeout = 6,
                app_name="Badgeuse la plateforme", 
                app_icon=Tools.get_resource_path("assets/logo_laplateforme.jpg"),
                            
            )

    @staticmethod
    def get_student_by_badge(data_listing, card):

        student = ""

        if data_listing:

            index = 0
            while index < len(data_listing):
                row = data_listing[index]
                badge_number = row[1]

                if badge_number:
                    try:
                        badge_number = int(badge_number)
                        if badge_number == card:
                            student = row[0]
                            break
                    except ValueError:
                        pass
                index += 1

            return student    
        else :        
            notification.notify(
                title = "⚠️ Erreur",
                message= "Informations sur l'étudiant vide .",
                timeout = 10 ,
                app_name="Badgeuse la plateforme", 
                app_icon=Tools.get_resource_path("assets/logo_laplateforme.jpg"),                               
            )
        

    def feed_students_list(unit_id):
        students_list = []

        token = Tools.read_in_file("temp/token_laplateforme")
        url = f"https://api.laplateforme.io/unit/student?student_email=&unit_id={unit_id}"
        # print("Token pour la requête : ", token)

        headers = {"token": token}

        try:
            response = requests.get(url, headers=headers)

            while response.status_code == 402:
                ApiPlateforme.refreshTokenPlateforme()
                headers = {
                    "token": Tools.read_in_file("temp/token_laplateforme")
                }
                response = requests.get(url, headers=headers)
                
            if response.status_code == 200:
                # print("feed_students_list / Réponse reçue :")
                response_data = response.json()
                students_list = [entry['student_email']
                                 for entry in response_data]
                return students_list
            else:
                notification.notify(
                    title = " ⚠️La requête a échoué avec le statut",
                    message=str(response.text)+": Status " + str(response.status_code),
                    timeout = 6,
                    app_name="Badgeuse la plateforme", 
                    app_icon=Tools.get_resource_path("assets/logo_laplateforme.jpg"),
                                
                )
        except requests.exceptions.RequestException as e:
            
            notification.notify(
                title = " ⚠️Une erreur est survenue lors dela requête :",
                message= e,
                timeout = 6,
                app_name="Badgeuse la plateforme", 
                app_icon=Tools.get_resource_path("assets/logo_laplateforme.jpg"),
                                
            )

    @staticmethod
    def refreshTokenPlateforme():
        print("------------REFRESH TOKEN START-----------------")
        authtoken = Tools.read_in_file("temp/auth_token_laplateforme")
        url = "https://auth.laplateforme.io/refresh"
        data = {
            'authtoken': authtoken
        }
        try:
            response = requests.post(url, data=data)

            if response.status_code == 200:
                response_json = response.json()
                print(response_json)
                os.remove("temp/token_laplateforme")
                Tools.write_in_file(
                    "temp/token_laplateforme",  response_json.get('token', None))
                print("------------REFRESH TOKEN END-----------------")

                return 1
            else:
                return f"Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            return f"Request failed: {str(e)}"
