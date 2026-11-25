"""Demo mode: suggests recipes from a built-in collection, no API key needed.

Used automatically when ANTHROPIC_API_KEY is not set. Matches the typed
ingredients and selected utensils against the recipes below and returns the
same JSON shape as the Claude version, so the page works the same way.
"""

# Always assumed to be in the kitchen (matched against ingredient keywords)
STAPLES = {"salt", "oil", "water"}

# Used when the user selects no utensils
DEFAULT_UTENSILS = {"Stovetop", "Frying pan", "Pot / saucepan"}

# Small tools almost every kitchen has: never block a recipe because they weren't ticked
BASIC_TOOLS = {"Knife & cutting board", "Mixing bowl", "Whisk"}

# Ingredients with these quantities are nice-to-have and don't count as missing
OPTIONAL_MARKERS = ("optional", "to serve", "to taste")


def I(name: str, quantity: str, *keywords: str) -> dict:
    """An ingredient. `keywords` are words that count as having it (default: its name)."""
    return {"name": name, "quantity": quantity, "keywords": keywords or (name,)}


RECIPES = [
    {
        "title": "Spinach & Feta Omelette",
        "description": "A fluffy omelette folded around wilted spinach and salty feta.",
        "time_minutes": 15, "difficulty": "easy", "servings": 1,
        "ingredients": [I("eggs", "3", "egg"), I("spinach", "1 handful"), I("feta", "40 g", "feta"),
                        I("butter", "1 tbsp", "butter", "oil"), I("salt and pepper", "to taste", "salt")],
        "utensils": ["Stovetop", "Frying pan", "Whisk"],
        "steps": ["Whisk the eggs with a pinch of salt and pepper.",
                  "Melt the butter in a frying pan over medium heat and wilt the spinach for 1 minute.",
                  "Pour in the eggs and let them set for 2 minutes, gently pulling the edges to the middle.",
                  "Crumble the feta over one half, fold the omelette and slide it onto a plate."],
        "tips": "Keep the heat medium-low so the eggs stay soft and don't brown.",
    },
    {
        "title": "Classic Tomato Pasta",
        "description": "Simple pasta in a garlicky tomato sauce, ready in 20 minutes.",
        "time_minutes": 20, "difficulty": "easy", "servings": 2,
        "ingredients": [I("pasta", "200 g", "pasta", "spaghetti", "penne", "macaroni", "noodle"),
                        I("tomatoes", "4 (or 1 can)", "tomato"), I("garlic", "2 cloves"),
                        I("olive oil", "2 tbsp", "oil"), I("basil or parmesan", "to serve", "basil", "parmesan", "cheese")],
        "utensils": ["Stovetop", "Pot / saucepan", "Frying pan", "Knife & cutting board"],
        "steps": ["Boil the pasta in salted water until al dente, then drain, keeping a cup of the water.",
                  "Meanwhile, chop the tomatoes and slice the garlic.",
                  "Fry the garlic in olive oil for 1 minute, add the tomatoes and a pinch of salt, and simmer for 10 minutes.",
                  "Toss the pasta in the sauce with a splash of pasta water. Top with basil or parmesan."],
        "tips": "Squash the tomatoes with a spoon while they simmer for a smoother sauce.",
    },
    {
        "title": "Egg Fried Rice",
        "description": "The best way to use leftover rice, with egg and any vegetables you have.",
        "time_minutes": 15, "difficulty": "easy", "servings": 2,
        "ingredients": [I("cooked rice", "2 cups", "rice"), I("eggs", "2", "egg"),
                        I("frozen peas or mixed vegetables", "1 cup", "pea", "carrot", "corn", "vegetable"),
                        I("soy sauce", "2 tbsp", "soy"), I("spring onion", "2", "spring onion", "onion", "scallion"),
                        I("oil", "1 tbsp")],
        "utensils": ["Stovetop", "Frying pan"],
        "steps": ["Heat the oil in a large frying pan over high heat.",
                  "Add the vegetables and stir-fry for 2 minutes.",
                  "Push them aside, crack in the eggs and scramble until just set.",
                  "Add the rice and soy sauce and stir-fry for 3 minutes until hot. Top with sliced spring onion."],
        "tips": "Cold, day-old rice works best: fresh rice turns mushy.",
    },
    {
        "title": "Chicken & Vegetable Stir-Fry",
        "description": "Tender chicken strips with crunchy vegetables in a quick soy-garlic sauce.",
        "time_minutes": 25, "difficulty": "easy", "servings": 2,
        "ingredients": [I("chicken breast", "300 g", "chicken"), I("bell pepper", "1", "pepper", "capsicum"),
                        I("onion", "1"), I("garlic", "2 cloves"), I("soy sauce", "3 tbsp", "soy"),
                        I("honey", "1 tsp", "honey", "sugar"), I("oil", "1 tbsp"),
                        I("rice or noodles", "to serve", "rice", "noodle")],
        "utensils": ["Stovetop", "Frying pan", "Knife & cutting board"],
        "steps": ["Cut the chicken into strips and slice the pepper and onion.",
                  "Fry the chicken in hot oil for 5–6 minutes until cooked through, then set aside.",
                  "Stir-fry the vegetables and garlic for 3 minutes.",
                  "Return the chicken, add the soy sauce and honey, toss for 1 minute and serve over rice or noodles."],
        "tips": "Get the pan really hot before adding the chicken so it sears instead of steaming.",
    },
    {
        "title": "Oven-Roasted Chicken & Potatoes",
        "description": "Crispy chicken thighs and golden potatoes from one tray.",
        "time_minutes": 50, "difficulty": "easy", "servings": 2,
        "ingredients": [I("chicken thighs or legs", "4", "chicken"), I("potatoes", "500 g", "potato"),
                        I("garlic", "4 cloves"), I("olive oil", "3 tbsp", "oil"),
                        I("dried herbs (thyme, rosemary or oregano)", "1 tsp", "thyme", "rosemary", "oregano", "herb"),
                        I("lemon", "1", "lemon")],
        "utensils": ["Oven", "Baking tray", "Knife & cutting board"],
        "steps": ["Heat the oven to 200 °C (400 °F).",
                  "Cut the potatoes into chunks and put them on a baking tray with the chicken and whole garlic cloves.",
                  "Drizzle with oil, add herbs, salt and pepper, and toss.",
                  "Roast for 40–45 minutes until the chicken skin is crisp and the potatoes are golden. Squeeze lemon over."],
        "tips": "Chicken is done when the juices run clear, or 75 °C (165 °F) inside.",
    },
    {
        "title": "Air-Fryer Crispy Potato Wedges",
        "description": "Crunchy, seasoned wedges with very little oil.",
        "time_minutes": 25, "difficulty": "easy", "servings": 2,
        "ingredients": [I("potatoes", "2 large", "potato"), I("oil", "1 tbsp"),
                        I("paprika", "1 tsp", "paprika"), I("garlic powder", "1/2 tsp", "garlic")],
        "utensils": ["Air fryer", "Knife & cutting board", "Mixing bowl"],
        "steps": ["Cut the potatoes into wedges (no need to peel).",
                  "Toss them in a bowl with oil, paprika, garlic powder and salt.",
                  "Air-fry at 200 °C (400 °F) for 18–20 minutes, shaking the basket halfway."],
        "tips": "Soak the wedges in cold water for 10 minutes and dry them well for extra crunch.",
    },
    {
        "title": "Cheesy Baked Potato (Microwave)",
        "description": "A fluffy jacket potato in under 10 minutes, no oven needed.",
        "time_minutes": 10, "difficulty": "easy", "servings": 1,
        "ingredients": [I("potato", "1 large", "potato"), I("cheese", "40 g, grated", "cheese", "cheddar"),
                        I("butter", "1 tsp", "butter"), I("beans, tuna or sour cream", "optional topping", "bean", "tuna", "cream")],
        "utensils": ["Microwave", "Knife & cutting board"],
        "steps": ["Prick the potato all over with a fork.",
                  "Microwave on high for 5 minutes, turn it over and cook 3–4 minutes more until soft.",
                  "Cut it open, fluff the inside with butter and salt, and top with cheese.",
                  "Microwave 30 seconds more to melt the cheese and add your topping."],
        "tips": "Wrap it in a clean towel for 2 minutes after cooking: it finishes cooking evenly.",
    },
    {
        "title": "Banana Pancakes",
        "description": "Soft pancakes with just a few basic ingredients.",
        "time_minutes": 20, "difficulty": "easy", "servings": 2,
        "ingredients": [I("banana", "1 ripe", "banana"), I("eggs", "2", "egg"), I("flour", "100 g", "flour"),
                        I("milk", "120 ml", "milk"), I("butter", "for the pan", "butter", "oil"),
                        I("honey or syrup", "to serve", "honey", "syrup", "sugar")],
        "utensils": ["Stovetop", "Frying pan", "Mixing bowl", "Whisk"],
        "steps": ["Mash the banana in a bowl, then whisk in the eggs and milk.",
                  "Add the flour and a pinch of salt and whisk until smooth.",
                  "Cook spoonfuls of batter in a buttered pan over medium heat, about 2 minutes per side.",
                  "Serve with honey or syrup."],
        "tips": "Flip when bubbles appear on the surface and the edges look set.",
    },
    {
        "title": "Grilled Cheese Sandwich",
        "description": "Golden, crunchy bread with melted cheese inside.",
        "time_minutes": 10, "difficulty": "easy", "servings": 1,
        "ingredients": [I("bread", "2 slices", "bread", "toast"), I("cheese", "2 slices", "cheese", "cheddar", "mozzarella"),
                        I("butter", "1 tbsp", "butter"), I("tomato or ham", "optional", "tomato", "ham")],
        "utensils": ["Stovetop", "Frying pan"],
        "steps": ["Butter one side of each bread slice.",
                  "Put one slice butter-side down in a pan, add the cheese (and tomato or ham), and top with the other slice butter-side up.",
                  "Cook on medium-low for 3 minutes per side until golden and melted."],
        "tips": "Cover the pan with a lid for a minute to help the cheese melt.",
    },
    {
        "title": "Tomato & Cucumber Salad",
        "description": "A fresh, crunchy salad with a lemon dressing.",
        "time_minutes": 10, "difficulty": "easy", "servings": 2,
        "ingredients": [I("tomatoes", "3", "tomato"), I("cucumber", "1", "cucumber"), I("red onion", "1/2", "onion"),
                        I("olive oil", "2 tbsp", "oil"), I("lemon", "1/2", "lemon", "vinegar"),
                        I("feta or herbs", "optional", "feta", "parsley", "mint", "herb")],
        "utensils": ["Knife & cutting board", "Mixing bowl"],
        "steps": ["Chop the tomatoes and cucumber into chunks and thinly slice the onion.",
                  "Put everything in a bowl with olive oil, lemon juice, salt and pepper.",
                  "Toss, then top with crumbled feta or chopped herbs."],
        "tips": "Salt the salad just before serving so the vegetables stay crunchy.",
    },
    {
        "title": "Creamy Mushroom Pasta",
        "description": "Rich pasta with garlicky mushrooms in a creamy sauce.",
        "time_minutes": 25, "difficulty": "easy", "servings": 2,
        "ingredients": [I("pasta", "200 g", "pasta", "spaghetti", "penne", "tagliatelle"), I("mushrooms", "250 g", "mushroom"),
                        I("garlic", "2 cloves"), I("cream", "150 ml", "cream"), I("butter", "1 tbsp", "butter", "oil"),
                        I("parmesan", "30 g", "parmesan", "cheese")],
        "utensils": ["Stovetop", "Pot / saucepan", "Frying pan", "Knife & cutting board"],
        "steps": ["Cook the pasta in salted water and drain.",
                  "Slice the mushrooms and fry them in butter over high heat for 5 minutes until golden.",
                  "Add the garlic for 1 minute, then pour in the cream and simmer for 2 minutes.",
                  "Stir in the pasta and parmesan, season and serve."],
        "tips": "Don't crowd the pan: mushrooms brown better in a single layer.",
    },
    {
        "title": "Vegetable Soup",
        "description": "A warming, blended soup that uses up whatever vegetables you have.",
        "time_minutes": 35, "difficulty": "easy", "servings": 4,
        "ingredients": [I("onion", "1"), I("carrots", "2", "carrot"), I("potato", "1", "potato"),
                        I("other vegetables (zucchini, celery, leek…)", "2 cups", "zucchini", "courgette", "celery", "leek", "broccoli", "pumpkin"),
                        I("stock cube", "1", "stock", "broth", "bouillon"), I("oil", "1 tbsp")],
        "utensils": ["Stovetop", "Pot / saucepan", "Knife & cutting board", "Blender"],
        "steps": ["Chop all the vegetables.",
                  "Soften the onion in oil in a pot for 5 minutes.",
                  "Add the rest of the vegetables, the stock cube and 1 litre of water. Simmer for 20 minutes.",
                  "Blend until smooth and season with salt and pepper."],
        "tips": "No blender? Leave it chunky: it's just as good.",
    },
    {
        "title": "Shakshuka",
        "description": "Eggs poached in a spiced tomato and pepper sauce.",
        "time_minutes": 25, "difficulty": "easy", "servings": 2,
        "ingredients": [I("eggs", "4", "egg"), I("tomatoes", "1 can or 5 fresh", "tomato"), I("bell pepper", "1", "pepper", "capsicum"),
                        I("onion", "1"), I("garlic", "2 cloves"), I("cumin or paprika", "1 tsp", "cumin", "paprika"),
                        I("bread", "to serve", "bread")],
        "utensils": ["Stovetop", "Frying pan", "Knife & cutting board"],
        "steps": ["Fry the sliced onion and pepper in oil for 5 minutes.",
                  "Add the garlic and spices for 1 minute, then the tomatoes. Simmer for 10 minutes.",
                  "Make 4 hollows in the sauce and crack an egg into each.",
                  "Cover and cook for 5–7 minutes until the whites are set. Serve with bread."],
        "tips": "Take it off the heat while the yolks still wobble: they keep cooking.",
    },
    {
        "title": "Tuna Rice Bowl",
        "description": "A quick bowl of rice topped with seasoned tuna and fresh vegetables.",
        "time_minutes": 20, "difficulty": "easy", "servings": 2,
        "ingredients": [I("rice", "150 g", "rice"), I("canned tuna", "1 can", "tuna"),
                        I("mayonnaise", "1 tbsp", "mayo"), I("soy sauce", "1 tbsp", "soy"),
                        I("cucumber or avocado", "1", "cucumber", "avocado"), I("sesame seeds", "optional", "sesame")],
        "utensils": ["Rice cooker", "Mixing bowl", "Knife & cutting board"],
        "steps": ["Cook the rice in the rice cooker.",
                  "Mix the tuna with mayonnaise and soy sauce.",
                  "Slice the cucumber or avocado.",
                  "Fill bowls with rice, top with tuna and vegetables, and sprinkle sesame seeds."],
        "tips": "A drop of sriracha in the tuna mix makes it spicy.",
    },
    {
        "title": "Banana Smoothie",
        "description": "A creamy breakfast smoothie in 5 minutes.",
        "time_minutes": 5, "difficulty": "easy", "servings": 1,
        "ingredients": [I("banana", "1", "banana"), I("milk or yogurt", "250 ml", "milk", "yogurt", "yoghurt"),
                        I("berries or other fruit", "1 handful", "berr", "strawberr", "mango", "apple"),
                        I("honey", "1 tsp", "honey"), I("oats", "2 tbsp, optional", "oat")],
        "utensils": ["Blender"],
        "steps": ["Put everything in the blender.", "Blend for 30–60 seconds until smooth.", "Pour and drink right away."],
        "tips": "Use a frozen banana for a thicker, colder smoothie.",
    },
    {
        "title": "Overnight-Style Microwave Oatmeal",
        "description": "Creamy porridge with fruit, made in a mug or bowl.",
        "time_minutes": 5, "difficulty": "easy", "servings": 1,
        "ingredients": [I("oats", "50 g", "oat"), I("milk", "150 ml", "milk"), I("banana or apple", "1", "banana", "apple", "berr"),
                        I("honey or cinnamon", "to taste", "honey", "cinnamon", "sugar")],
        "utensils": ["Microwave"],
        "steps": ["Mix the oats and milk in a large microwave-safe bowl.",
                  "Microwave for 2 minutes, stir, then 30–60 seconds more.",
                  "Top with sliced fruit and honey or cinnamon."],
        "tips": "Use a big bowl: oats bubble up and can overflow.",
    },
    {
        "title": "Beef & Bean Chili",
        "description": "A hearty, mildly spicy chili that's even better the next day.",
        "time_minutes": 45, "difficulty": "medium", "servings": 4,
        "ingredients": [I("minced beef", "400 g", "beef", "mince", "ground meat"), I("kidney beans", "1 can", "bean"),
                        I("tomatoes", "1 can", "tomato"), I("onion", "1"), I("garlic", "2 cloves"),
                        I("chili powder and cumin", "1 tsp each", "chili", "chilli", "cumin"),
                        I("rice or bread", "to serve", "rice", "bread", "tortilla")],
        "utensils": ["Stovetop", "Pot / saucepan", "Knife & cutting board"],
        "steps": ["Soften the chopped onion and garlic in oil for 5 minutes.",
                  "Add the beef and brown it, breaking it up with a spoon.",
                  "Stir in the spices, tomatoes and drained beans. Simmer for 25–30 minutes.",
                  "Season and serve with rice or bread."],
        "tips": "Swap the beef for a second can of beans to make it vegetarian.",
    },
    {
        "title": "Slow-Cooker Chicken Curry",
        "description": "Set it in the morning, come home to a fragrant curry.",
        "time_minutes": 240, "difficulty": "easy", "servings": 4,
        "ingredients": [I("chicken", "600 g", "chicken"), I("onion", "1"), I("garlic", "3 cloves"),
                        I("curry powder or paste", "2 tbsp", "curry"), I("coconut milk", "1 can", "coconut"),
                        I("tomatoes", "1 can", "tomato"), I("rice", "to serve", "rice")],
        "utensils": ["Slow cooker", "Knife & cutting board"],
        "steps": ["Chop the chicken, onion and garlic.",
                  "Put everything except the rice into the slow cooker and stir.",
                  "Cook on low for 6 hours or high for 4 hours.",
                  "Season and serve with rice."],
        "tips": "Stir in a handful of spinach at the end for extra greens.",
    },
    {
        "title": "Baked Salmon with Lemon & Garlic",
        "description": "Juicy salmon fillets baked in 15 minutes.",
        "time_minutes": 20, "difficulty": "easy", "servings": 2,
        "ingredients": [I("salmon fillets", "2", "salmon", "fish"), I("lemon", "1", "lemon"), I("garlic", "2 cloves"),
                        I("butter or olive oil", "1 tbsp", "butter", "oil"),
                        I("green vegetables (broccoli, green beans, asparagus)", "to serve", "broccoli", "green bean", "asparagus")],
        "utensils": ["Oven", "Baking tray"],
        "steps": ["Heat the oven to 200 °C (400 °F).",
                  "Put the salmon on a lined baking tray with any green vegetables around it.",
                  "Top with butter, sliced garlic, lemon slices, salt and pepper.",
                  "Bake for 12–15 minutes until the salmon flakes easily."],
        "tips": "Thicker fillets need a couple more minutes.",
    },
    {
        "title": "Grilled Chicken Skewers",
        "description": "Marinated chicken and vegetables cooked on the grill.",
        "time_minutes": 30, "difficulty": "medium", "servings": 2,
        "ingredients": [I("chicken breast", "300 g", "chicken"), I("bell pepper", "1", "pepper", "capsicum"),
                        I("onion", "1"), I("yogurt", "3 tbsp", "yogurt", "yoghurt"), I("lemon", "1/2", "lemon"),
                        I("paprika", "1 tsp", "paprika", "spice")],
        "utensils": ["Grill", "Knife & cutting board", "Mixing bowl"],
        "steps": ["Cut the chicken, pepper and onion into chunks.",
                  "Mix the chicken with yogurt, lemon juice, paprika and salt; leave for 10 minutes.",
                  "Thread chicken and vegetables onto skewers.",
                  "Grill for 10–12 minutes, turning often, until cooked through."],
        "tips": "Soak wooden skewers in water first so they don't burn.",
    },
    {
        "title": "Avocado Toast with Egg",
        "description": "Crunchy toast, creamy avocado and a soft egg on top.",
        "time_minutes": 10, "difficulty": "easy", "servings": 1,
        "ingredients": [I("bread", "2 slices", "bread"), I("avocado", "1", "avocado"), I("eggs", "2", "egg"),
                        I("lemon", "a squeeze", "lemon", "lime"), I("chili flakes", "optional", "chili", "chilli")],
        "utensils": ["Toaster", "Stovetop", "Frying pan"],
        "steps": ["Toast the bread.",
                  "Mash the avocado with lemon juice, salt and pepper and spread it on the toast.",
                  "Fry the eggs in a little oil until the whites are set.",
                  "Put an egg on each toast and sprinkle with chili flakes."],
        "tips": "No toaster? Toast the bread in the dry frying pan first.",
    },
    {
        "title": "Simple Chocolate Mug Cake",
        "description": "A warm chocolate cake for one, made in the microwave.",
        "time_minutes": 5, "difficulty": "easy", "servings": 1,
        "ingredients": [I("flour", "4 tbsp", "flour"), I("sugar", "3 tbsp", "sugar"), I("cocoa powder", "2 tbsp", "cocoa", "chocolate"),
                        I("milk", "3 tbsp", "milk"), I("oil or butter", "2 tbsp", "oil", "butter"), I("egg", "1", "egg")],
        "utensils": ["Microwave", "Whisk"],
        "steps": ["Whisk all the ingredients together in a large mug until smooth.",
                  "Microwave on high for 70–90 seconds until risen and just set.",
                  "Let it cool for a minute before eating."],
        "tips": "Drop a few chocolate pieces in the middle before cooking for a gooey center.",
    },
    {
        "title": "Hummus",
        "description": "Smooth, homemade hummus to eat with bread or vegetables.",
        "time_minutes": 10, "difficulty": "easy", "servings": 4,
        "ingredients": [I("chickpeas", "1 can", "chickpea"), I("garlic", "1 clove"), I("lemon", "1", "lemon"),
                        I("olive oil", "3 tbsp", "oil"), I("tahini", "2 tbsp", "tahini", "sesame")],
        "utensils": ["Food processor"],
        "steps": ["Drain the chickpeas, keeping a few tablespoons of the liquid.",
                  "Blend everything with salt until smooth, adding the liquid to loosen it.",
                  "Serve drizzled with olive oil."],
        "tips": "A blender works too: just add a bit more liquid.",
    },
    {
        "title": "Vegetable Frittata",
        "description": "A thick oven-baked omelette, great hot or cold.",
        "time_minutes": 30, "difficulty": "easy", "servings": 4,
        "ingredients": [I("eggs", "6", "egg"), I("vegetables (peppers, spinach, zucchini, onion…)", "2 cups", "pepper", "spinach", "zucchini", "courgette", "onion", "broccoli", "mushroom"),
                        I("cheese", "50 g", "cheese", "feta", "cheddar", "parmesan"), I("milk", "3 tbsp", "milk"), I("oil", "1 tbsp")],
        "utensils": ["Oven", "Frying pan", "Stovetop", "Whisk"],
        "steps": ["Heat the oven to 190 °C (375 °F).",
                  "Soften the chopped vegetables in oil in an oven-safe frying pan for 5 minutes.",
                  "Whisk the eggs with milk, salt and pepper and pour over the vegetables. Scatter the cheese on top.",
                  "Cook on the stove for 3 minutes, then bake for 12–15 minutes until set."],
        "tips": "Let it rest 5 minutes before slicing so it holds together.",
    },
]


def _have(keywords: tuple[str, ...], user_items: list[str]) -> bool:
    return any(k in item for k in keywords for item in user_items)


def suggest_demo_recipes(ingredients: str, utensils: list[str], has_photos: bool) -> dict:
    user_items = [s.strip().lower() for s in ingredients.split(",") if s.strip()]
    available_utensils = (set(utensils) or DEFAULT_UTENSILS) | BASIC_TOOLS
    photo_note = (" Photo recognition needs AI mode, so in demo mode only typed ingredients are used."
                  if has_photos else "")

    if not user_items:
        return {"detected_ingredients": [], "recipes": [],
                "message": "Demo mode can't look at photos. Type your ingredients to get recipes." }

    candidates = []
    for recipe in RECIPES:
        if not set(recipe["utensils"]) <= available_utensils:
            continue
        ings, matched, missing, main_count = [], 0, 0, 0
        for i in recipe["ingredients"]:
            from_user = _have(i["keywords"], user_items)
            staple = any(k in STAPLES for k in i["keywords"])
            optional = any(m in i["quantity"] for m in OPTIONAL_MARKERS)
            if not staple and not optional:
                main_count += 1
                matched += from_user
                missing += not from_user
            ings.append({"name": i["name"], "quantity": i["quantity"], "have": from_user or staple})
        # Need at least 2 of the main ingredients (or all of them for tiny recipes)
        if matched < min(2, main_count) or missing > 3:
            continue
        candidates.append((missing, -matched, recipe, ings))

    candidates.sort(key=lambda c: (c[0], c[1]))
    recipes = [{**{k: v for k, v in r.items() if k != "ingredients"}, "ingredients": ings}
               for _, _, r, ings in candidates[:3]]

    if not recipes:
        message = ("Demo mode couldn't find a recipe for those ingredients and utensils. "
                   "Try adding a few more ingredients or selecting more utensils." + photo_note)
    else:
        message = (f"Demo mode: {len(recipes)} recipe(s) from SnapChef's built-in collection "
                   "that match what you have." + photo_note)
    return {"detected_ingredients": [], "recipes": recipes, "message": message}
