# crud/main.py
from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
import models
from database import engine, sessionlocal
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    """Gestionnaire de contexte qui renvoie une session de base de données.

    Renvoie :
        Generator : Un générateur qui renvoie une session de base de données.
            La session est automatiquement fermée après utilisation.
    """
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """
    Gère les requêtes GET à l'URL principale.

    Args:
        request (Request): l'objet de requête entrant.
        db (Session): la session de base de données, obtenue à partir d'une dépendance.

    Returns:
        TemplateResponse: l'objet de réponse avec le modèle "index.html" et un dictionnaire
        contenant la requête et la liste des utilisateurs, triés par identifiant dans l'ordre décroissant.
    """
    users = db.query(models.User).order_by(models.User.id.desc())
    return templates.TemplateResponse("index.html", {"request": request, "users": users})


@app.post("/add")
async def add(request: Request, name: str = Form(...), position: str = Form(...), office: str = Form(...), db: Session = Depends(get_db)):
    """
    Ajoute un nouvel utilisateur à la base de données.

    Args:
        request (Request): La requête HTTP entrante.
        name (str): Le nom de l'utilisateur (obligatoire).
        position (str): La position de l'utilisateur (obligatoire).
        office (str): Le bureau de l'utilisateur (obligatoire).
        db (Session): La session de base de données (fournie par Depends).

    Returns:
        RedirectResponse: Une réponse de redirection vers la page d'accueil.

    Raises:
        HTTPException: Si les données du formulaire sont invalides.
    """
    print(name)
    print(position)
    print(office)
    users = models.User(name=name, position=position, office=office)
    db.add(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@app.get("/addnew")
async def addnew(request: Request):
    """
    Gère les requêtes GET sur l'endpoint "/addnew".

    Paramètres :
    ------------
    request: Request
        L'objet de requête qui contient des informations sur la requête entrante.

    Retours :
    ---------
    TemplateResponse
        Un objet de réponse qui rend le template "addnew.html" en utilisant la variable "request".
    """
    return templates.TemplateResponse("addnew.html", {"request": request})


@app.get("/edit/{user_id}")
async def edit(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Récupère un utilisateur depuis la base de données par son ID et renvoie le template edit.html.

    Args:
        request (Request): La requête HTTP entrante.
        user_id (int): L'ID de l'utilisateur à récupérer dans la base de données.
        db (Session, optionnel): La session de base de données à utiliser. Par défaut, la fonction utilise la fonction get_db pour récupérer une nouvelle session.

    Returns:
        TemplateResponse: Une réponse HTTP contenant le contenu du template edit.html et les données de l'utilisateur récupérées depuis la base de données.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "user": user})


@app.post("/update/{user_id}")
async def update(request: Request, user_id: int, name: str = Form(...), position: str = Form(...), office: str = Form(...), db: Session = Depends(get_db)):
    """Met à jour les informations d'un utilisateur dans la base de données.

    Args:
        request (Request): L'objet Request de FastAPI.
        user_id (int): L'ID de l'utilisateur à mettre à jour.
        name (str): Le nouveau nom de l'utilisateur.
        position (str): La nouvelle position de l'utilisateur.
        office (str): Le nouveau bureau de l'utilisateur.
        db (Session): La session de base de données.

    Returns:
        RedirectResponse: Une réponse de redirection vers la page d'accueil.
    """
    users = db.query(models.User).filter(models.User.id == user_id).first()
    users.name = name
    users.position = position
    users.office = office
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@app.get("/delete/{user_id}")
async def delete(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Supprime un utilisateur de la base de données.

    Args:
        request (Request): L'objet de requête FastAPI.
        user_id (int): L'ID de l'utilisateur à supprimer.
        db (Session, facultatif): La session de base de données à utiliser (par défaut : dépend de get_db).

    Returns:
        RedirectResponse: Une réponse de redirection vers la page d'accueil.
    """
    users = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
