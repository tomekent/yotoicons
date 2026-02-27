from sqlalchemy import create_engine, Column, Integer, String, select, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./yotoicons.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

class YotoIcon(Base):
    __tablename__ = "yotoicons"
    id = Column(String, primary_key=True, index=True)
    category = Column(String, index=True)
    tag_1 = Column(String, index=True)
    tag_2 = Column(String, index=True)
    # Add other columns as needed

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()