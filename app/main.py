"""SnapChef web server: serves the page and the /api/recipes endpoint."""

import hmac
import os
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .demo import suggest_demo_recipes
from .limits import UsageLimiter
from .recipes import RecipeError, suggest_recipes

MAX_PHOTOS = 5
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB per photo
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# Optional protection for a public deployment (set as environment variables):
#   APP_ACCESS_CODE        - visitors must type this code before getting recipes
#   RATE_LIMIT_PER_HOUR    - max recipe requests per visitor (IP) per hour
#   MAX_REQUESTS_PER_DAY   - max recipe requests for the whole app per day
ACCESS_CODE = os.getenv("APP_ACCESS_CODE", "")
limiter = UsageLimiter(
    per_ip_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "10")),
    total_per_day=int(os.getenv("MAX_REQUESTS_PER_DAY", "100")),
)

app = FastAPI(title="SnapChef")


def error(message: str, status: int) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status)


def client_ip(request: Request) -> str:
    # Behind a hosting proxy (Render, etc.) the visitor's IP is the first X-Forwarded-For entry
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "mode": "ai" if os.getenv("ANTHROPIC_API_KEY") else "demo",
        "api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "access_code_required": bool(ACCESS_CODE),
    }


@app.post("/api/recipes")
async def recipes(
    request: Request,
    ingredients: str = Form(""),
    utensils: list[str] = Form([]),
    notes: str = Form(""),
    photos: list[UploadFile] = File([]),
    x_access_code: str = Header(""),
):
    if ACCESS_CODE and not hmac.compare_digest(x_access_code.encode(), ACCESS_CODE.encode()):
        return error("Wrong or missing access code.", 401)

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
        # Demo mode: built-in recipes, no API key or cost
        return suggest_demo_recipes(ingredients[:2000], utensils[:30], has_photos=bool(photo_data))

    limit_message = limiter.check(client_ip(request))
    if limit_message:
        return error(limit_message, 429)

    try:
        return await suggest_recipes(ingredients[:2000], utensils[:30], notes[:500], photo_data)
    except RecipeError as e:
        return error(e.message, e.status)


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
