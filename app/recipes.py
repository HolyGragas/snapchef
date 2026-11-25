"""Talks to Google Gemini: turns ingredients, utensils and photos into recipes."""

import json
import os

from google import genai
from google.genai import errors, types

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

SYSTEM_PROMPT = """You are SnapChef, a friendly home-cooking assistant.

The user tells you what food they have (as a typed list, as photos of their
ingredients / fridge / pantry, or both) and which kitchen utensils and
appliances they can use. Suggest 3 recipes they can realistically cook now.

Rules:
- First identify every usable ingredient you can see in the photos and list
  them in `detected_ingredients` (empty list if there are no photos). Ignore
  things that are not food.
- Build recipes mainly from the user's ingredients. You may assume basic
  pantry staples (salt, pepper, oil, water) without them being listed.
- Any other ingredient a recipe needs must be marked `have: false`. Prefer
  recipes with no missing ingredients; at most 2 missing per recipe.
- Only use the utensils/appliances the user selected (if they selected none,
  assume a basic stovetop kitchen: pan, pot, knife, cutting board).
- Respect the user's extra notes (diet, allergies, time, servings).
- Steps must be clear, in order, and beginner-friendly.
- Write all text in the same language the user wrote in (English if unclear).
- If nothing edible was given, return an empty `recipes` list and explain why
  in `message`."""

RECIPE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["detected_ingredients", "recipes", "message"],
    "properties": {
        "detected_ingredients": {"type": "array", "items": {"type": "string"}},
        "message": {"type": "string", "description": "Short friendly note to the user (one or two sentences)."},
        "recipes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title", "description", "time_minutes", "difficulty",
                    "servings", "ingredients", "utensils", "steps", "tips",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "time_minutes": {"type": "integer"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                    "servings": {"type": "integer"},
                    "ingredients": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["name", "quantity", "have"],
                            "properties": {
                                "name": {"type": "string"},
                                "quantity": {"type": "string"},
                                "have": {"type": "boolean"},
                            },
                        },
                    },
                    "utensils": {"type": "array", "items": {"type": "string"}},
                    "steps": {"type": "array", "items": {"type": "string"}},
                    "tips": {"type": "string"},
                },
            },
        },
    },
}


class RecipeError(Exception):
    """An error with a message that is safe to show to the user."""

    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.message = message
        self.status = status


_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _build_contents(ingredients: str, utensils: list[str], notes: str,
                    photos: list[tuple[str, bytes]]) -> list:
    contents: list = [types.Part.from_bytes(data=data, mime_type=media_type) for media_type, data in photos]

    lines = []
    if photos:
        lines.append(f"I attached {len(photos)} photo(s) of my ingredients.")
    lines.append(f"Ingredients I have: {ingredients.strip() or '(none typed - use the photos)'}")
    lines.append(f"Utensils / appliances I can use: {', '.join(utensils) if utensils else '(not specified)'}")
    if notes.strip():
        lines.append(f"Extra notes: {notes.strip()}")
    contents.append("\n".join(lines))
    return contents


async def suggest_recipes(ingredients: str, utensils: list[str], notes: str,
                          photos: list[tuple[str, bytes]]) -> dict:
    try:
        response = await _get_client().aio.models.generate_content(
            model=MODEL,
            contents=_build_contents(ingredients, utensils, notes, photos),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_json_schema=RECIPE_SCHEMA,
            ),
        )
    except errors.ClientError as e:
        text = f"{e.status} {e.message}".lower()
        if e.code in (401, 403) or "api key" in text or "api_key" in text:
            raise RecipeError("The Gemini API key is missing or invalid. Check the GEMINI_API_KEY setting "
                              "(.env file locally, environment variables when hosted).", 500)
        if e.code == 429:
            raise RecipeError("The free Gemini limit was reached. Wait a minute and try again.", 429)
        if e.code == 404:
            raise RecipeError(f"The Gemini model '{MODEL}' wasn't found. Set GEMINI_MODEL to a current model.", 500)
        raise RecipeError(f"The request was rejected: {e.message}", 400)
    except errors.ServerError:
        raise RecipeError("Gemini is having trouble right now. Please try again.", 502)
    except errors.APIError as e:
        raise RecipeError(f"Gemini API error ({e.code}). Please try again.", 502)
    except OSError:
        raise RecipeError("Couldn't reach the Gemini API. Check your internet connection.", 503)

    if response.prompt_feedback and response.prompt_feedback.block_reason:
        raise RecipeError("Sorry, SnapChef can't help with that request.", 422)
    finish = response.candidates[0].finish_reason if response.candidates else None
    if finish == types.FinishReason.MAX_TOKENS:
        raise RecipeError("The answer was too long and got cut off. Try with fewer ingredients or photos.", 502)
    if not response.text:
        raise RecipeError("Sorry, SnapChef can't help with that request.", 422)

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        raise RecipeError("The AI returned an unexpected answer. Please try again.", 502)
