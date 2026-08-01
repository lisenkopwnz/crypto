from app.api.database import engine
from app.api.v1.models import Base

Base.metadata.create_all(bind=engine, checkfirst=True)