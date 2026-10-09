const state = { episodes: [], filtered: [] };
const $ = (selector) => document.querySelector(selector);
const collator = new Intl.Collator("de", { numeric: true, sensitivity: "base" });
const number = new Intl.NumberFormat("de-DE");

function text(value = "") {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  })[character]);
}

function searchable(episode) {
  return [
    episode.number, episode.title, episode.description,
    ...episode.cast.flatMap((item) => {
      const [family, given] = item.person.split(",").map((part) => part.trim());
      return [item.role, item.person, given ? `${given} ${family}` : item.person];
    }),
    ...episode.production.flatMap((item) => [item.credit, item.value]),
  ].join(" ").toLocaleLowerCase("de");
}

function setUrl() {
  const params = new URLSearchParams();
  if ($("#query").value) params.set("q", $("#query").value);
  if ($("#decade").value) params.set("jahr", $("#decade").value);
  if ($("#coverage").value) params.set("daten", $("#coverage").value);
  history.replaceState(null, "", `${location.pathname}${params.size ? `?${params}` : ""}${location.hash}`);
}

function applyFilters() {
  const query = $("#query").value.trim().toLocaleLowerCase("de");
  const decade = Number($("#decade").value);
  const coverage = $("#coverage").value;
  state.filtered = state.episodes.filter((episode) => {
    if (query && !episode._search.includes(query)) return false;
    if (decade && (episode.release_year < decade || episode.release_year >= decade + 10)) return false;
    if (coverage === "production" && !episode.production.length) return false;
    if (coverage === "cast" && !episode.cast.length) return false;
    if (coverage === "description" && !episode.description) return false;
    if (coverage === "incomplete" && episode.production.length && episode.cast.length && episode.description) return false;
    return true;
  }).sort((a, b) => collator.compare(a.number, b.number));
  render();
  setUrl();
}

function render() {
  const container = $("#results");
  const template = $("#episode-card-template");
  const fragment = document.createDocumentFragment();
  for (const episode of state.filtered) {
    const card = template.content.firstElementChild.cloneNode(true);
    card.querySelector(".episode-number").textContent = String(episode.number).padStart(3, "0");
    card.querySelector("strong").textContent = episode.title;
    const duration = episode.duration_seconds ? `${Math.round(episode.duration_seconds / 60)} Min.` : "Laufzeit offen";
    card.querySelector("small").textContent = `${episode.release_year} · ${episode.cast.length} Rollen · ${duration}`;
    card.addEventListener("click", () => showEpisode(episode));
    fragment.append(card);
  }
  container.replaceChildren(fragment);
  container.setAttribute("aria-busy", "false");
  $("#result-count").textContent = `${number.format(state.filtered.length)} von ${number.format(state.episodes.length)} Folgen`;
  $("#empty").hidden = state.filtered.length > 0;
}

function list(items, first, second) {
  if (!items.length) return '<p class="muted">Noch keine Daten vorhanden.</p>';
  return `<dl class="detail-list">${items.map((item) => `<div><dt>${text(item[first])}</dt><dd>${text(item[second])}</dd></div>`).join("")}</dl>`;
}

function showEpisode(episode) {
  const duration = episode.duration_seconds
    ? `${Math.floor(episode.duration_seconds / 60)}:${String(episode.duration_seconds % 60).padStart(2, "0")} Min.`
    : "Laufzeit offen";
  const sources = episode.sources.map((source, index) => `<a href="${text(source.url)}" target="_blank" rel="noreferrer">Quelle ${index + 1}</a>`).join("");
  $("#episode-detail").innerHTML = `
    <p class="detail-number">Folge ${String(episode.number).padStart(3, "0")}</p>
    <h2>${text(episode.title)}</h2>
    <div class="detail-meta"><span class="pill">${episode.release_year}</span><span class="pill">${duration}</span><span class="pill">${episode.cast.length} Rollen</span></div>
    <p class="detail-description">${text(episode.description || "Noch keine Beschreibung vorhanden.")}</p>
    <section class="detail-section"><h3>Sprecher & Rollen</h3>${list(episode.cast, "role", "person")}</section>
    <section class="detail-section"><h3>Produktion</h3>${list(episode.production, "credit", "value")}</section>
    <section class="detail-section"><h3>Trackpunkte</h3>${list(episode.tracks, "position", "title")}</section>
    <div class="detail-links"><a href="./api/v1/episodes/${String(episode.number).padStart(3, "0")}.json">JSON öffnen</a>${sources}</div>`;
  $("#episode-dialog").showModal();
}

async function init() {
  const response = await fetch("./api/v1/episodes.json");
  if (!response.ok) throw new Error(`API antwortet mit ${response.status}`);
  const payload = await response.json();
  state.episodes = payload.episodes.map((episode) => ({ ...episode, _search: searchable(episode) }));

  const years = state.episodes.map((episode) => episode.release_year).filter(Boolean);
  const decades = [...new Set(years.map((year) => Math.floor(year / 10) * 10))].sort();
  $("#decade").insertAdjacentHTML("beforeend", decades.map((year) => `<option value="${year}">${year}er</option>`).join(""));
  $("#episode-count").textContent = number.format(state.episodes.length);
  $("#cast-count").textContent = number.format(state.episodes.reduce((sum, episode) => sum + episode.cast.length, 0));
  $("#production-count").textContent = number.format(state.episodes.filter((episode) => episode.production.length).length);

  const params = new URLSearchParams(location.search);
  $("#query").value = params.get("q") || "";
  $("#decade").value = params.get("jahr") || "";
  $("#coverage").value = params.get("daten") || "";
  applyFilters();
}

$("#search-form").addEventListener("input", applyFilters);
$("#search-form").addEventListener("reset", () => setTimeout(applyFilters));
$("#episode-dialog .dialog-close").addEventListener("click", () => $("#episode-dialog").close());
$("#episode-dialog").addEventListener("click", (event) => {
  if (event.target === $("#episode-dialog")) $("#episode-dialog").close();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "/" && document.activeElement?.tagName !== "INPUT") {
    event.preventDefault(); $("#query").focus();
  }
});
$("#copy-api").addEventListener("click", async () => {
  const url = new URL("./api/v1/episodes/001.json", location.href).href;
  await navigator.clipboard.writeText(url);
  $("#copy-api").textContent = "Kopiert ✓";
  setTimeout(() => { $("#copy-api").textContent = "URL kopieren"; }, 1600);
});

init().catch((error) => {
  $("#result-count").textContent = "Daten konnten nicht geladen werden";
  $("#results").innerHTML = `<p>${text(error.message)}</p>`;
});

if ("serviceWorker" in navigator) navigator.serviceWorker.register("./service-worker.js");
