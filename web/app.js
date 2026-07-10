const CATEGORY_ORDER = [
  "steam_primary",
  "steam_secondary",
  "tcs_teacher",
  "qef",
  "edb_circular",
];

const CATEGORY_COLORS = {
  steam_primary: { bg: "#eefaf3", color: "#0f7a4c" },
  steam_secondary: { bg: "#eef6ff", color: "#1f5eff" },
  tcs_teacher: { bg: "#f6f0ff", color: "#6d28d9" },
  qef: { bg: "#fff7ed", color: "#c2410c" },
  edb_circular: { bg: "#f8fafc", color: "#334155" },
};

let snapshot = null;
let activeCategory = "all";
let newOnly = false;
let searchQuery = "";

const els = {
  metaBar: document.getElementById("metaBar"),
  statsGrid: document.getElementById("statsGrid"),
  categoryTabs: document.getElementById("categoryTabs"),
  cardsGrid: document.getElementById("cardsGrid"),
  loading: document.getElementById("loading"),
  emptyState: document.getElementById("emptyState"),
  refreshBtn: document.getElementById("refreshBtn"),
  searchInput: document.getElementById("searchInput"),
  newOnly: document.getElementById("newOnly"),
  cardTemplate: document.getElementById("cardTemplate"),
};

function formatTime(iso) {
  if (!iso) return "未知";
  const date = new Date(iso);
  return date.toLocaleString("zh-HK", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function setLoading(isLoading) {
  els.loading.classList.toggle("hidden", !isLoading);
  els.refreshBtn.disabled = isLoading;
}

async function fetchData(refresh = false) {
  setLoading(true);
  try {
    const url = refresh ? "/api/refresh" : "/api/data";
    const options = refresh ? { method: "POST" } : {};
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "載入失敗");
    }
    snapshot = data;
    render();
  } catch (error) {
    els.metaBar.textContent = `錯誤：${error.message}`;
    els.cardsGrid.innerHTML = "";
    els.emptyState.classList.remove("hidden");
  } finally {
    setLoading(false);
  }
}

function renderStats() {
  els.statsGrid.innerHTML = "";
  const labels = snapshot.category_labels || {};

  const allCard = document.createElement("button");
  allCard.className = `stat-card${activeCategory === "all" ? " active" : ""}`;
  allCard.innerHTML = `
    <div class="stat-label">全部</div>
    <div class="stat-value">${snapshot.total || 0}</div>
    <div class="stat-new">${snapshot.new_total || 0} 項新資料</div>
  `;
  allCard.addEventListener("click", () => {
    activeCategory = "all";
    render();
  });
  els.statsGrid.appendChild(allCard);

  CATEGORY_ORDER.forEach((key) => {
    const card = document.createElement("button");
    card.className = `stat-card${activeCategory === key ? " active" : ""}`;
    const total = snapshot.counts?.[key] || 0;
    const fresh = snapshot.new_counts?.[key] || 0;
    card.innerHTML = `
      <div class="stat-label">${labels[key] || key}</div>
      <div class="stat-value">${total}</div>
      <div class="stat-new">${fresh} 項新資料</div>
    `;
    card.addEventListener("click", () => {
      activeCategory = key;
      render();
    });
    els.statsGrid.appendChild(card);
  });
}

function renderTabs() {
  const labels = snapshot.category_labels || {};
  const tabs = [{ key: "all", label: "全部" }];
  CATEGORY_ORDER.forEach((key) => tabs.push({ key, label: labels[key] || key }));

  els.categoryTabs.innerHTML = "";
  tabs.forEach((tab) => {
    const button = document.createElement("button");
    button.className = `tab${activeCategory === tab.key ? " active" : ""}`;
    button.textContent = tab.label;
    button.addEventListener("click", () => {
      activeCategory = tab.key;
      render();
    });
    els.categoryTabs.appendChild(button);
  });
}

function filteredItems() {
  return (snapshot.items || []).filter((item) => {
    if (activeCategory !== "all" && item.category !== activeCategory) return false;
    if (newOnly && !item.is_new) return false;
    if (!searchQuery) return true;
    const blob = `${item.title} ${item.summary} ${item.category_label}`.toLowerCase();
    return blob.includes(searchQuery);
  });
}

function renderCards(items) {
  els.cardsGrid.innerHTML = "";
  els.emptyState.classList.toggle("hidden", items.length > 0);

  items.forEach((item) => {
    const node = els.cardTemplate.content.cloneNode(true);
    const card = node.querySelector(".card");
    const categoryBadge = node.querySelector(".category-badge");
    const newBadge = node.querySelector(".new-badge");
    const titleLink = node.querySelector(".card-title a");
    const dateEl = node.querySelector(".card-date");
    const summaryEl = node.querySelector(".card-summary");

    if (item.is_new) {
      card.classList.add("is-new");
      newBadge.classList.remove("hidden");
    }

    const colors = CATEGORY_COLORS[item.category] || CATEGORY_COLORS.edb_circular;
    categoryBadge.textContent = item.category_label;
    categoryBadge.style.background = colors.bg;
    categoryBadge.style.color = colors.color;

    titleLink.textContent = item.title;
    titleLink.href = item.url || "#";

    dateEl.textContent = item.date ? `日期：${item.date}` : "";
    dateEl.classList.toggle("hidden", !item.date);

    summaryEl.textContent = item.summary || "";
    summaryEl.classList.toggle("hidden", !item.summary);

    els.cardsGrid.appendChild(node);
  });
}

function render() {
  if (!snapshot) return;

  els.metaBar.textContent = `最後更新：${formatTime(snapshot.updated_at)} · 共 ${snapshot.total} 項 · ${snapshot.new_total} 項新資料`;
  renderStats();
  renderTabs();
  renderCards(filteredItems());
}

els.refreshBtn.addEventListener("click", () => fetchData(true));
els.searchInput.addEventListener("input", (event) => {
  searchQuery = event.target.value.trim().toLowerCase();
  renderCards(filteredItems());
  els.emptyState.classList.toggle("hidden", filteredItems().length > 0);
});
els.newOnly.addEventListener("change", (event) => {
  newOnly = event.target.checked;
  renderCards(filteredItems());
  els.emptyState.classList.toggle("hidden", filteredItems().length > 0);
});

fetchData(false);
