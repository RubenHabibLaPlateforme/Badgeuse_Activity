from controllers.Tools import Tools
import requests
import os


class ApiPlateforme:
    @staticmethod
    def get_laplateforme_token(token):
        url = "https://auth.laplateforme.io/oauth"

        print("Token pour la requête : ", token)

        # Corps de la requête
        formdata = {"token_id": token}

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(url, data=formdata, headers=headers)

            if response.status_code == 200:
                response_data = response.json()

                if "error" not in response_data:
                    Tools.write_in_file(
                        "temp/auth_token_laplateforme", response_data.get("authtoken")
                    )
                    Tools.write_in_file(
                        "temp/token_laplateforme", response_data.get("token")
                    )
                else:
                    print(
                        "erreur dans la réponse de API plateforme"
                        + response_data["error"]
                    )
                    return 0
            else:
                print("La requête a échoué avec le statut", response.status_code)
                print(response.text)
                return 0
        except requests.exceptions.RequestException as e:
            print("Une erreur est survenue lors de la requête :", e)
        return 1

    @staticmethod
    def get_data_badges():
        token = Tools.read_in_file("temp/token_laplateforme")
        url = f"https://api.laplateforme.io/student?badge=&email="
        headers = {"token": token}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print("Réponse reçue :")
                response_data = response.json()
                response_data.sort(key=lambda x: x["student_email"])
                print(response_data)
                # data_badges = [entry['student_email'] for entry in response_data]
                # print("Students List updated:", students_list)

                return [[item["student_email"], item["student_badge"]] for item in response_data]

            else:
                print("La requête a échoué avec le statut", response.status_code)
                print(response.text)
        except requests.exceptions.RequestException as e:
            print("Une erreur est survenue lors de la requête :", e)

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
                            print("TROUVE API")
                            student = row[0]
                            break
                    except ValueError:
                        pass
                index += 1

        return student

    def feed_students_list(unit_id):
        students_list = []

        token = Tools.read_in_file("temp/token_laplateforme")
        url = (
            f"https://api.laplateforme.io/unit/student?student_email=&unit_id={unit_id}"
        )
        print("Token pour la requête : ", token)

        headers = {"token": token}
        try:
            response = requests.get(url, headers=headers)

            while response.status_code == 402:
                ApiPlateforme.refreshTokenPlateforme()
                headers = {"token": Tools.read_in_file("temp/token_laplateforme")}
                response = requests.get(url, headers=headers)
                print(response.status_code)
            if response.status_code == 200:
                print("Réponse reçue :")
                response_data = response.json()
                response_data.sort(key=lambda x: x["student_email"])
                students_list = [entry["student_email"] for entry in response_data]
                return students_list
            else:
                print("La requête a échoué avec le statut", response.status_code)
                print(response.text)
        except requests.exceptions.RequestException as e:
            print("Une erreur est survenue lors de la requête :", e)

    @staticmethod
    def refreshTokenPlateforme():
        print("------------REFRESH TOKEN START-----------------")
        authtoken = Tools.read_in_file("temp/auth_token_laplateforme")
        url = "https://auth.laplateforme.io/refresh"
        data = {"authtoken": authtoken}
        try:
            response = requests.post(url, data=data)

            if response.status_code == 200:
                response_json = response.json()
                print(response_json)
                os.remove("temp/token_laplateforme")
                Tools.write_in_file(
                    "temp/token_laplateforme", response_json.get("token", None)
                )
                print("------------REFRESH TOKEN END-----------------")

                return 1
            else:
                return f"Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            return f"Request failed: {str(e)}"
