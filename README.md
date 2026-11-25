# 🍳 SnapChef

A web app that turns **what's in your kitchen into recipes**.

Give SnapChef:
- the **ingredients** you have (typed in), and/or
- **photos** of your fridge, pantry or ingredients, and
- the **utensils** you'll use (oven, pan, microwave, blender, air fryer…)

…and it suggests 3 recipes you can cook right now, with quantities, step-by-step
instructions, and a clear "you need this" label on anything you're missing.

The recipes and the photo recognition come from **Claude** (Anthropic's AI model, `claude-opus-5-5`).

## Run it with Docker

You need **Docker Desktop** and an **Anthropic API key**
(create one at https://console.anthropic.com/settings/keys; the API is paid per use).

1. Copy the example settings file and add your key:
   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```
   Put your key after `ANTHROPIC_API_KEY=` and save. `.env` is git-ignored, so the key never goes to GitHub.

2. Start the app:
   ```powershell
   docker compose up -d --build
   ```

3. Open **http://localhost:8000**

Stop it with `docker compose down`. See the logs with `docker compose logs -f`.

## Deploy online (Render, free)

1. Sign in at https://render.com with GitHub and allow access to the `snapchef` repo.
2. **New → Blueprint**, pick `snapchef`. Render reads `render.yaml`.
3. Fill in the secrets it asks for:
   - `ANTHROPIC_API_KEY`: your key
   - `APP_ACCESS_CODE`: a code you give to people you demo to (leave empty for an open app)
4. Click **Apply**. After a few minutes the app is live at `https://snapchef-xxxx.onrender.com`.

Every push to `main` redeploys automatically. On the free plan the app sleeps after
15 minutes without visitors and takes about a minute to wake up, so open it shortly
before a demo.

**Protecting your API budget:** the app limits each visitor to 10 requests per hour and
the whole app to 100 per day (change with `RATE_LIMIT_PER_HOUR` / `MAX_REQUESTS_PER_DAY`).
Also set a monthly spend limit in the Anthropic Console (Settings → Limits).

## How it works

```
Browser (app/static)  ──photos + ingredients + utensils──►  FastAPI (app/main.py)
                                                              │  validates input
                                                              ▼
                                                     app/recipes.py ──► Claude API
                                                              │  (vision + JSON schema)
Browser renders recipe cards  ◄──────── recipes as JSON ──────┘
```

| File | What it does |
|---|---|
| `app/main.py` | Web server: serves the page, `POST /api/recipes`, `GET /api/health` |
| `app/recipes.py` | Builds the prompt (with photos), calls Claude, returns structured recipes |
| `app/static/` | The web page: `index.html`, `style.css`, `app.js` |
| `Dockerfile` / `compose.yaml` | Container setup |

Limits: up to 5 photos per request, 5 MB each (JPG, PNG, WEBP or GIF).

## Run without Docker (optional)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY = "your-key"
uvicorn app.main:app --reload
```
