import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.backend.db import Base, YotoIcon, DATABASE_URL
from pathlib import Path



engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def import_csv(csv_path: Path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            icon = YotoIcon(
                id=row["id"],
                category=row.get("category", ""),
                tag_1=row.get("tag_1", ""),
                tag_2=row.get("tag_2", "")
                # Add other fields as needed
            )
            session.merge(icon)  # merge avoids duplicates by primary key
        session.commit()
    print("Import complete.")

if __name__ == "__main__":
    CSV_PATH = Path("data/yotoicons_metadata.csv") 
    Base.metadata.create_all(bind=engine)
    import_csv(CSV_PATH)