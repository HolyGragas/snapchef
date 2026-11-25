const UTENSILS = [
  "Stovetop", "Oven", "Microwave", "Frying pan", "Pot / saucepan", "Blender",
  "Air fryer", "Grill", "Baking tray", "Mixing bowl", "Whisk", "Food processor",
  "Toaster", "Rice cooker", "Slow cooker", "Knife & cutting board",
];
const MAX_PHOTOS = 5;
const MAX_PHOTO_BYTES = 5 * 1024 * 1024;

const $ = (id) => document.getElementById(id);
const ingredients = [];
let photos = [];

// ---------- ingredient chips ----------
function renderChips() {
  $("chips").replaceChildren(...ingredients.map((name, i) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = name;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.setAttribute("aria-label", `Remove ${name}`);
    remove.textContent = "×";
    remove.onclick = () => { ingredients.splice(i, 1); renderChips(); };
    chip.append(remove);
    return chip;
  }));
}

function addIngredients(text) {
  text.split(",").map((s) => s.trim()).filter(Boolean).forEach((name) => {
    if (!ingredients.some((x) => x.toLowerCase() === name.toLowerCase())) ingredients.push(name);
  });
  renderChips();
}

$("ingredient-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === ",") {
    e.preventDefault();
    addIngredients(e.target.value);
    e.target.value = "";
  } else if (e.key === "Backspace" && !e.target.value && ingredients.length) {
    ingredients.pop();
    renderChips();
  }
});

// ---------- photos ----------
function renderPreviews() {
  $("previews").replaceChildren(...photos.map((file, i) => {
    const box = document.createElement("div");
    box.className = "preview";
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.alt = file.name;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.setAttribute("aria-label", `Remove ${file.name}`);
    remove.textContent = "×";
    remove.onclick = () => { photos.splice(i, 1); renderPreviews(); };
    box.append(img, remove);
    return box;
  }));
}

function addPhotos(files) {
  for (const file of files) {
    if (!file.type.startsWith("image/")) continue;
    if (file.size > MAX_PHOTO_BYTES) { showError(`"${file.name}" is larger than 5 MB.`); continue; }
    if (photos.length >= MAX_PHOTOS) { showError(`You can add up to ${MAX_PHOTOS} photos.`); break; }
    photos.push(file);
  }
  renderPreviews();
}

$("photo-input").addEventListener("change", (e) => { addPhotos(e.target.files); e.target.value = ""; });
const drop = $("dropzone");
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => { e.preventDefault(); drop.classList.remove("drag"); addPhotos(e.dataTransfer.files); });

// ---------- utensils ----------
$("utensils").replaceChildren(...UTENSILS.map((name) => {
  const label = document.createElement("label");
  label.className = "utensil";
  const box = document.createElement("input");
  box.type = "checkbox";
  box.value = name;
  label.append(box, name);
  return label;
}));

// ---------- submit ----------
function showError(msg) {
  $("form-error").textContent = msg;
  $("form-error").hidden = !msg;
}

$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  addIngredients($("ingredient-input").value);
  $("ingredient-input").value = "";
  showError("");

  if (!ingredients.length && !photos.length) {
    showError("Add at least one ingredient or photo.");
    return;
  }

  const data = new FormData();
  data.append("ingredients", ingredients.join(", "));
  document.querySelectorAll("#utensils input:checked").forEach((b) => data.append("utensils", b.value));
  data.append("notes", $("notes").value);
  photos.forEach((p) => data.append("photos", p));

  $("submit").disabled = true;
  $("loading").hidden = false;
  $("results").hidden = true;

  try {
    const code = $("access-code").value.trim();
    localStorage.setItem("snapchef-access-code", code);
    const res = await fetch("/api/recipes", {
      method: "POST",
      body: data,
      headers: code ? { "X-Access-Code": code } : {},
    });
    const body = await res.json().catch(() => ({ error: "The server sent an unexpected answer." }));
    if (!res.ok) throw new Error(body.error || `Request failed (${res.status})`);
    renderResults(body);
  } catch (err) {
    showError(err.message);
  } finally {
    $("submit").disabled = false;
    $("loading").hidden = true;
  }
});

// ---------- results ----------
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function renderResults({ detected_ingredients = [], recipes = [], message = "" }) {
  const detected = $("detected");
  detected.hidden = !detected_ingredients.length;
  if (detected_ingredients.length) {
    const chips = el("div", undefined, "chips");
    detected_ingredients.forEach((name) => chips.append(el("span", name, "chip")));
    detected.replaceChildren(el("h3", "📷 I spotted in your photos:"), chips);
  }

  $("message").textContent = message;

  $("recipes").replaceChildren(...recipes.map((r) => {
    const card = el("article", undefined, "card recipe");
    card.append(el("h3", r.title), el("p", r.description, "desc"));

    const meta = el("div", undefined, "meta");
    meta.append(
      el("span", `⏱ ${r.time_minutes} min`),
      el("span", `🍽 ${r.servings} serving${r.servings === 1 ? "" : "s"}`),
      el("span", `📊 ${r.difficulty}`),
    );
    if (r.utensils?.length) meta.append(el("span", `🔧 ${r.utensils.join(", ")}`));
    card.append(meta);

    card.append(el("h4", "Ingredients"));
    const ul = el("ul");
    r.ingredients.forEach((ing) => {
      const li = el("li", `${ing.quantity} ${ing.name}`.trim());
      if (!ing.have) li.append(el("span", "you need this", "missing"));
      ul.append(li);
    });
    card.append(ul);

    card.append(el("h4", "Steps"));
    const ol = el("ol");
    r.steps.forEach((s) => ol.append(el("li", s)));
    card.append(ol);

    if (r.tips) card.append(el("p", `💡 ${r.tips}`, "tips"));
    return card;
  }));

  $("results").hidden = false;
  $("results").scrollIntoView({ behavior: "smooth" });
}

// ---------- API key check ----------
fetch("/api/health")
  .then((r) => r.json())
  .then((h) => {
    $("key-warning").hidden = h.mode !== "demo";
    $("access-section").hidden = !h.access_code_required;
    $("access-code").value = localStorage.getItem("snapchef-access-code") || "";
  })
  .catch(() => {});
