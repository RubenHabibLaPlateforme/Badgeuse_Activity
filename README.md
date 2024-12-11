# Ma Badgeuse 

## Get started
- Installer les dépendances situées dans le fichier **requirements.txt**
```python
    pip install -r requirements.txt 
```

- Build le **.exe** (avec terminal output)
```python
   pyinstaller --onefile --add-data "config/credentials.json;config" --add-data "config/client_secrets.json;config" --add-data "assets/logo_laplateforme_icon.ico;assets" --add-data "assets/logo_laplateforme.jpg;assets" --hidden-import plyer.platforms.win.notification main.py
```
- Build le **.exe**
```python
   pyinstaller --onefile --add-data "config/credentials.json;config" --noconsole --add-data "config/client_secrets.json;config" --add-data "assets/logo_laplateforme_icon.ico;assets" --add-data "assets/logo_laplateforme.jpg;assets"  --hidden-import plyer.platforms.win.notification main.py


```
-  Lancer le serveur en utilisant la commande `python main.py`
  


## Git 