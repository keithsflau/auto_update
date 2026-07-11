const CATEGORY_ORDER = [
  "steam_primary",
  "steam_secondary",
  "tcs_teacher",
  "news_primary",
  "news_secondary",
  "qef",
  "edb_circular",
];

const CATEGORY_COLORS = {
  steam_primary: { bg: "#eefaf3", color: "#0f7a4c" },
  steam_secondary: { bg: "#eef6ff", color: "#1f5eff" },
  tcs_teacher: { bg: "#f6f0ff", color: "#6d28d9" },
  news_primary: { bg: "#fff1f2", color: "#be123c" },
  news_secondary: { bg: "#eff6ff", color: "#1d4ed8" },
  qef: { bg: "#fff7ed", color: "#c2410c" },
  edb_circular: { bg: "#f8fafc", color: "#334155" },
};

const isLocalServer = ["localhost", "127.0.0.1"].includes(window.location.hostname);

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
    let data;
    if (isLocalServer) {
      const url = refresh ? "/api/refresh" : "/api/data";
      const options = refresh ? { method: "POST" } : {};
      const response = await fetch(url, options);
      data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "載入失敗");
      }
    } else {
      const response = await fetch(`data/dashboard.json?t=${Date.now()}`);
      if (!response.ok) {
        throw new Error("載入失敗");
      }
      data = await response.json();
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
  return (snapshot.items || [])
    .filter((item) => {
      if (activeCategory !== "all" && item.category !== activeCategory) return false;
      if (newOnly && !item.is_new) return false;
      if (!searchQuery) return true;
      const blob = `${item.title} ${item.summary} ${item.category_label} ${item.subcategory_label || ""}`.toLowerCase();
      return blob.includes(searchQuery);
    })
    .sort((a, b) => {
      const dateA = a.date_sort || "0000-01-01";
      const dateB = b.date_sort || "0000-01-01";
      if (dateA !== dateB) return dateB.localeCompare(dateA);
      return (a.title || "").localeCompare(b.title || "", "zh-HK");
    });
}

function renderCards(items) {
  els.cardsGrid.innerHTML = "";
  els.emptyState.classList.toggle("hidden", items.length > 0);

  items.forEach((item) => {
    const node = els.cardTemplate.content.cloneNode(true);
    const card = node.querySelector(".card");
    const categoryBadge = node.querySelector(".category-badge");
    const subcategoryBadge = node.querySelector(".subcategory-badge");
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

    if (item.subcategory_label) {
      subcategoryBadge.textContent = item.subcategory_label;
      subcategoryBadge.classList.remove("hidden");
    } else {
      subcategoryBadge.classList.add("hidden");
    }

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

  const lookback = snapshot.lookback_days || 365;
  const autoUpdate = isLocalServer ? "" : " · 每 6 小時自動更新 · TCS 每日電郵";
  els.metaBar.textContent = `最後更新：${formatTime(snapshot.updated_at)} · 近 ${lookback} 日內 ${snapshot.total} 項 · ${snapshot.new_total} 項新資料 · 按日期由近到遠排列${autoUpdate}`;
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
