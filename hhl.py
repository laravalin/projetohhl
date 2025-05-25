#hhl ou app.py depende de como ta no documento apresentado pelo prof
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Configuracoes
from app.routes.scraper import scraper_bp

app.register_blueprint(scraper_bp)

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Configuracoes': Configuracoes}