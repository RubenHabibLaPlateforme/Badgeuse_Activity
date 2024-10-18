from controllers.GoogleAuth import GoogleAuth
from controllers.Tools import Tools
from controllers.ApiPlateforme import ApiPlateforme
from controllers.App import App
import os

def main():

    token_google_id = Tools.read_in_file("./temp/token_google_id")
    app = App()
    googleAuth = GoogleAuth()
    creds = googleAuth.authenticate()

    if token_google_id != -1:
        # A FINIR BOUCLE !!
        get_laplateforme_token_result = ApiPlateforme.get_laplateforme_token(
            Tools.read_in_file("./temp/token_google_id")
        )

        if get_laplateforme_token_result != 0 :
            
            data_badges = ApiPlateforme.get_data_badges()
            tokenPlateforme = Tools.read_in_file("./temp/token_laplateforme")

            if tokenPlateforme != '':
                app.create_window(data_badges, Tools.read_in_file("./temp/token_laplateforme"), creds)
        else: 
            
            os.remove("temp/token_laplateforme")
            os.remove("temp/token.json")
            os.remove("temp/token_google_id")
            main()        
                
            

            
    else:
        
        
        token_google_id = Tools.read_in_file("./temp/token_google_id")

        if token_google_id != -1:

            get_laplateforme_token_result = ApiPlateforme.get_laplateforme_token(
                Tools.read_in_file("./temp/token_google_id")
            )

            if get_laplateforme_token_result:

                # import menu
                data_badges = ApiPlateforme.get_data_badges()
                print(data_badges)                
                

                app.create_window(data_badges, Tools.read_in_file("./temp/token_laplateforme"), creds)



if __name__ == "__main__":
    main()