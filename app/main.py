from fastapi import FastAPI, Request, Form, Query, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.backend.db import YotoIcon, get_db

import io
import zipfile
import os
import re
from sqlalchemy import or_, and_
import random
from sqlalchemy.sql.expression import func

ICONS_DIR = "data/icons"
STATIC_DIR = "app/frontend/static"
TEMPLATES_DIR = "app/frontend/templates"
app = FastAPI()

app.mount("/yoto_icons", StaticFiles(directory=ICONS_DIR), name="yoto_icons")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)



@app.get("/", response_class=HTMLResponse)
def search_form(request: Request, db=Depends(get_db)):
    # Show random icons if no search
    random_icons = db.query(YotoIcon).order_by(func.random()).limit(12).all()
    results = [row.__dict__ for row in random_icons]
    for r in results:
        r.pop('_sa_instance_state', None)
    return templates.TemplateResponse("search.html", {"request": request, "results": results, "query": ""})

@app.post("/", response_class=HTMLResponse)
def search(request: Request, query: str = Form(""), db=Depends(get_db)):
    if not query.strip():
        # Show random icons if no search
        random_icons = db.query(YotoIcon).order_by(func.random()).limit(12).all()
        results = [row.__dict__ for row in random_icons]
    else:
        terms = [t.strip() for t in re.split(r'[;,]', query) if t.strip()]
        filters = []
        for term in terms:
            filters.append(
                or_(
                    YotoIcon.category.ilike(f"%{term}%"),
                    YotoIcon.tag_1.ilike(f"%{term}%"),
                    YotoIcon.tag_2.ilike(f"%{term}%")
                )
            )
        q = db.query(YotoIcon).filter(or_(*filters))
        results = [row.__dict__ for row in q.all()]
    for r in results:
        r.pop('_sa_instance_state', None)
    return templates.TemplateResponse("search.html", {"request": request, "results": results, "query": query})

@app.get("/api/search")
def api_search(
    query: str = Query(""),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db=Depends(get_db)
):
    if not query.strip():
        # Show random icons if no search
        q = db.query(YotoIcon).order_by(func.random())
        total = db.query(YotoIcon).count()
    else:
        terms = [t.strip() for t in re.split(r'[;,]', query) if t.strip()]
        filters = []
        for term in terms:
            filters.append(
                or_(
                    YotoIcon.category.ilike(f"%{term}%"),
                    YotoIcon.tag_1.ilike(f"%{term}%"),
                    YotoIcon.tag_2.ilike(f"%{term}%")
                )
            )
        q = db.query(YotoIcon).filter(or_(*filters))
        total = q.count()
    results = [row.__dict__ for row in q.offset(offset).limit(limit).all()]
    for r in results:
        r.pop('_sa_instance_state', None)
    return JSONResponse({"results": results, "total": total})

@app.post("/download")
async def download_icons(data: dict = Body(...)):
    tracks = data.get("tracks", [])
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for track in tracks:
            icon_id = track.get("id")
            name = track.get("name", "").strip()
            if not icon_id or not name:
                continue
            filename = f"{icon_id}.png"
            safe_name = re.sub(r'[^a-zA-Z0-9_\- ]', '_', name)  # sanitize filename
            outname = f"{safe_name}.png"
            filepath = os.path.join(ICONS_DIR, filename)
            if os.path.isfile(filepath):
                zipf.write(filepath, arcname=outname)
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=track_icons.zip"}
    )

@app.get("/tracklist", response_class=HTMLResponse)
def tracklist(request: Request):
    return templates.TemplateResponse("tracklist.html", {"request": request})