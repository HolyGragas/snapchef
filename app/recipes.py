"""Talks to Claude: turns ingredients, utensils and photos into recipes."""

import base64
import json

import anthropic

MODEL = "claude-opus-5-5"

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
- Steps must be clear, numbered in order, and beginner-friendly.
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


_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic()  # reads ANTHROPIC_API_KEY
    return _client


def _build_user_content(ingredients: str, utensils: list[str], notes: str,
                        photos: list[tuple[str, bytes]]) -> list[dict]:
    content: list[dict] = []
    for media_type, data in photos:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": base64.standard_b64encode(data).decode("utf-8"),
            },
        })

    lines = []
    if photos:
        lines.append(f"I attached {len(photos)} photo(s) of my ingredients.")
    lines.append(f"Ingredients I have: {ingredients.strip() or '(none typed - use the photos)'}")
    lines.append(f"Utensils / appliances I can use: {', '.join(utensils) if utensils else '(not specified)'}")
    if notes.strip():
        lines.append(f"Extra notes: {notes.strip()}")
    content.append({"type": "text", "text": "\n".join(lines)})
    return content


async def suggest_recipes(ingredients: str, utensils: list[str], notes: str,
                          photos: list[tuple[str, bytes]]) -> dict:
    try:
        response = await _get_client().beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_user_content(ingredients, utensils, notes, photos)}],
            output_config={
                "effort": "medium",
                "format": {"type": "json_schema", "schema": RECIPE_SCHEMA},
            },
            # If Claude's safety filters decline, the API retries on a fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        raise RecipeError("The Anthropic API key is missing or invalid. Check ANTHROPIC_API_KEY in your .env file.", 500)
    except anthropic.PermissionDeniedError:
        raise RecipeError("Your Anthropic API key doesn't have access to this model.", 500)
    except anthropic.RateLimitError:
        raise RecipeError("Too many requests right now - wait a minute and try again.", 429)
    except anthropic.BadRequestError as e:
        raise RecipeError(f"The request was rejected: {e.message}", 400)
    except anthropic.APIStatusError as e:
        raise RecipeError(f"Claude API error ({e.status_code}). Please try again.", 502)
    except anthropic.APIConnectionError:
        raise RecipeError("Couldn't reach the Claude API. Check your internet connection.", 503)

    if response.stop_reason == "refusal":
        raise RecipeError("Sorry, SnapChef can't help with that request.", 422)
    if response.stop_reason == "max_tokens":
        raise RecipeError("The answer was too long and got cut off. Try with fewer ingredients or photos.", 502)

    text = "".join(block.text for block in response.content if block.type == "text")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise RecipeError("Claude returned an unexpected answer. Please try again.", 502)
