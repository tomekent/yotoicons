from fastapi import FastAPI, Request, Form, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import io
import zipfile
import os

app = FastAPI()

app.mount("/yoto_icons", StaticFiles(directory="yoto_icons"), name="yoto_icons")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
df = pd.read_csv("yotoicons_metadata.csv", dtype=str).fillna("")

@app.get("/", response_class=HTMLResponse)
def search_form(request: Request):
    return templates.TemplateResponse("search.html", {"request": request, "query": ""})

@app.post("/", response_class=HTMLResponse)
def search(
    request: Request,
    query: str = Form("")
):
    # Search across category, tag_1, and tag_2 (case-insensitive)
    mask = (
        df['category'].str.contains(query, case=False, na=False) |
        df['tag_1'].str.contains(query, case=False, na=False) |
        df['tag_2'].str.contains(query, case=False, na=False)
    )
    results = df[mask].to_dict(orient="records")
    return templates.TemplateResponse("search.html", {"request": request, "results": results, "query": query})

@app.get("/api/search")
def api_search(
    query: str = Query(""),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100)
):
    mask = (
        df['category'].str.contains(query, case=False, na=False) |
        df['tag_1'].str.contains(query, case=False, na=False) |
        df['tag_2'].str.contains(query, case=False, na=False)
    ) if query else pd.Series([True] * len(df))
    results = df[mask].iloc[offset:offset+limit].to_dict(orient="records")
    # Convert all values to str or int for JSON serialization
    for row in results:
        for k, v in row.items():
            if pd.isna(v):
                row[k] = ""
            elif isinstance(v, (int, float)):
                row[k] = int(v) if isinstance(v, int) or v.is_integer() else float(v)
            else:
                row[k] = str(v)
    total = int(mask.sum())
    return JSONResponse({"results": results, "total": total})

@app.post("/download")
async def download_icons(data: dict = Body(...)):
    ids = data.get("ids", [])
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for icon_id in ids:
            filename = f"{icon_id}.png"
            filepath = os.path.join("yoto_icons", filename)
            if os.path.isfile(filepath):
                zipf.write(filepath, arcname=filename)
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=yoto_icons.zip"}
    )