"""SnapChef web server: serves the page and the /api/recipes endpoint."""

import os
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .recipes import RecipeError, suggest_recipes

MAX_PHOTOS = 5
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB per photo
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

app = FastAPI(title="SnapChef")


def error(message: str, status: int) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status)


@app.get("/api/health")
async def health():
    return {"ok": True, "api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY"))}


@app.post("/api/recipes")
async def recipes(
    ingredients: str = Form(""),
    utensils: list[str] = Form([]),
    notes: str = Form(""),
    photos: list[UploadFile] = File([]),
):
    photos = [p for p in photos if p.filename]
    if not ingredients.strip() and not photos:
        return error("Add some ingredients or at least one photo.", 400)
    if len(photos) > MAX_PHOTOS:
        return error(f"You can send up to {MAX_PHOTOS} photos.", 400)

    photo_data: list[tuple[str, bytes]] = []
    for photo in photos:
        if photo.content_type not in ALLOWED_TYPES:
            return error(f"'{photo.filename}' isn't a supported image (use JPG, PNG, WEBP or GIF).", 400)
        data = await photo.read()
        if len(data) > MAX_PHOTO_BYTES:
            return error(f"'{photo.filename}' is larger than 5 MB.", 400)
        photo_data.append((photo.content_type, data))

    if not os.getenv("ANTHROPIC_API_KEY"):
        return error("No Anthropic API key is set. Add ANTHROPIC_API_KEY to your .env file and restart.", 500)

    try:
        return await suggest_recipes(ingredients[:2000], utensils[:30], notes[:500], photo_data)
    except RecipeError as e:
        return error(e.message, e.status)


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
