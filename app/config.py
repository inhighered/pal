import os
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, PackageLoader


SECRET_KEY = os.getenv('ADMIN_SECRET_KEY')
TEMPLATES = Jinja2Templates(directory="app/templates")
TEMPLATES_SIMPLE_ENV =  Environment(loader=FileSystemLoader("app/templates"))

app_session = {}
users = {}
