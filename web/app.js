const PAGES = [
  { key: "competition", file: "competitions.html", label: "學界比賽" },
  { key: "scholarship", file: "scholarships.html", label: "獎學金申請" },
  { key: "tcs_teacher", file: "tcs.html", label: "教師培訓 (TCS)" },
  { key: "news_primary", file: "news-primary.html", label: "小學新聞" },
  { key: "news_secondary", file: "news-secondary.html", label: "中學新聞" },
  { key: "qef", file: "qef.html", label: "優質教育基金 (QEF)" },
  { key: "edb_circular", file: "edb.html", label: "教育局通函" },
];

const CATEGORY_COLORS = {
  competition: { bg: "#eefaf3", color: "#0f7a4c" },
  scholarship: { bg: "#fff7ed", color: "#c2410c" },
  tcs_teacher: { bg: "#f6f0ff", color: "#6d28d9" },
  news_primary: { bg: "#fff1f2", color: "#be123c" },
  news_secondary: { bg: "#eff6ff", color: "#1d4ed8" },
  qef: { bg: "#fff7ed", color: "#c2410c" },
  edb_circular: { bg: "#f8fafc", color: "#334155" },
};

const TAB_CONFIGS = {
  tcs: {
    category: "tcs_teacher",
    accent: "#6d28d9",
    fallback: "other",
    tabs: [
      { key: "", label: "全部" },
      { key: "steam", label: "STEAM" },
      { key: "ai", label: "AI" },
      { key: "admin", label: "行政" },
      { key: "self_review", label: "自評" },
      { key: "exchange", label: "交流團" },
      { key: "guidance", label: "訓輔導" },
      { key: "promotion", label: "晉升" },
      { key: "other", label: "其他" },
    ],
  },
  competition: {
    category: "competition",
    accent: "#0f7a4c",
    fallback: "general",
    tabs: [
      { key: "", label: "全部" },
      { key: "steam", label: "STEAM / 創科" },
      { key: "science", label: "科學 / 數學" },
      { key: "arts", label: "藝術 / 文化" },
      { key: "sports", label: "體育" },
      { key: "language", label: "語文 / 辯論" },
      { key: "social", label: "公民 / 服務" },
      { key: "general", label: "其他比賽" },
    ],
  },
  scholarship: {
    category: "scholarship",
    accent: "#c2410c",
    fallback: "general",
    tabs: [
      { key: "", label: "全部" },
      { key: "secondary", label: "中學" },
      { key: "primary", label: "小學" },
      { key: "university", label: "升學 / 大專" },
      { key: "general", label: "其他獎學金" },
    ],
  },
};

const isLocalServer = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const pageCategory = document.body.dataset.category || "";
const pageTitle = document.body.dataset.title || "香港教育更新儀表板";
const tabMode = document.body.dataset.tabs || "";
const tabConfig = TAB_CONFIGS[tabMode] || null;

let snapshot = null;
let newOnly = false;
let searchQuery = "";
let activeSubcategoryTab = "";

const els = {
  metaBar: document.getElementById("metaBar"),
  pageNav: document.getElementById("pageNav"),
  homeGrid: document.getElementById("homeGrid"),
  pageStats: document.getElementById("pageStats"),
  cardsGrid: document.getElementById("cardsGrid"),
  loading: document.getElementById("loading"),
  emptyState: document.getElementById("emptyState"),
  refreshBtn: document.getElementById("refreshBtn"),
  searchInput: document.getElementById("searchInput"),
  newOnly: document.getElementById("newOnly"),
  cardTemplate: document.getElementById("cardTemplate"),
  subcategoryTabs: document.getElementById("subcategoryTabs"),
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
  if (els.refreshBtn) els.refreshBtn.disabled = isLoading;
}

function renderPageNav() {
  if (!els.pageNav) return;

  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  els.pageNav.innerHTML = "";

  const homeLink = document.createElement("a");
  homeLink.href = "index.html";
  homeLink.className = `page-nav-link${currentPath === "index.html" ? " active" : ""}`;
  homeLink.textContent = "首頁";
  els.pageNav.appendChild(homeLink);

  PAGES.forEach((page) => {
    const link = document.createElement("a");
    link.href = page.file;
    link.className = `page-nav-link${currentPath === page.file ? " active" : ""}`;
    link.textContent = page.label;
    els.pageNav.appendChild(link);
  });
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
    if (els.cardsGrid) els.cardsGrid.innerHTML = "";
    if (els.homeGrid) els.homeGrid.innerHTML = "";
    els.emptyState.classList.remove("hidden");
  } finally {
    setLoading(false);
  }
}

function getCategoryLabel(key) {
  return (snapshot?.category_labels || {})[key] || key;
}

function renderHome() {
  const labels = snapshot.category_labels || {};
  els.homeGrid.innerHTML = "";

  PAGES.forEach((page) => {
    const total = snapshot.counts?.[page.key] || 0;
    const fresh = snapshot.new_counts?.[page.key] || 0;
    const colors = CATEGORY_COLORS[page.key] || CATEGORY_COLORS.edb_circular;

    const card = document.createElement("a");
    card.href = page.file;
    card.className = "home-card";
    card.style.borderColor = colors.color;
    card.innerHTML = `
      <div class="home-card-label" style="color:${colors.color}">${labels[page.key] || page.label}</div>
      <div class="home-card-value">${total}</div>
      <div class="home-card-new">${fresh} 項新資料</div>
      <div class="home-card-cta">進入 →</div>
    `;
    els.homeGrid.appendChild(card);
  });

  const lookback = snapshot.lookback_days || 365;
  const autoUpdate = isLocalServer ? "" : " · 每 6 小時自動更新";
  els.metaBar.textContent = `最後更新：${formatTime(snapshot.updated_at)} · 近 ${lookback} 日內共 ${snapshot.total} 項${autoUpdate}`;
}

function getTabLabel(key) {
  if (!tabConfig) return key;
  const tab = tabConfig.tabs.find((entry) => entry.key === key);
  return tab ? tab.label : key;
}

function initSubcategoryTabFromHash() {
  if (!tabConfig) return;
  const hash = window.location.hash.replace("#", "");
  if (tabConfig.tabs.some((tab) => tab.key === hash)) {
    activeSubcategoryTab = hash;
  }
}

function countBySubcategory(items, fallback) {
  const counts = {};
  items.forEach((item) => {
    const key = item.subcategory || fallback;
    counts[key] = (counts[key] || 0) + 1;
  });
  return counts;
}

function categoryItems() {
  if (!tabConfig) return [];
  return (snapshot.items || []).filter((item) => item.category === tabConfig.category);
}

function renderSubcategoryTabs() {
  if (!els.subcategoryTabs || !tabConfig) return;

  const items = categoryItems();
  const counts = countBySubcategory(items, tabConfig.fallback);
  els.subcategoryTabs.innerHTML = "";
  els.subcategoryTabs.classList.remove("hidden");
  els.subcategoryTabs.style.setProperty("--tab-accent", tabConfig.accent);

  tabConfig.tabs.forEach((tab) => {
    const count = tab.key ? counts[tab.key] || 0 : items.length;
    const button = document.createElement("button");
    button.type = "button";
    button.className = `subcategory-tab${activeSubcategoryTab === tab.key ? " active" : ""}`;
    button.innerHTML = `<span class="subcategory-tab-label">${tab.label}</span><span class="subcategory-tab-count">${count}</span>`;
    button.addEventListener("click", () => {
      activeSubcategoryTab = tab.key;
      window.location.hash = tab.key;
      renderCategoryPage();
    });
    els.subcategoryTabs.appendChild(button);
  });
}

function renderPageStats() {
  if (!els.pageStats) return;

  if (tabConfig) {
    const items = categoryItems();
    const tabLabel = activeSubcategoryTab ? getTabLabel(activeSubcategoryTab) : "全部";
    const tabItems = activeSubcategoryTab
      ? items.filter((item) => (item.subcategory || tabConfig.fallback) === activeSubcategoryTab)
      : items;
    const fresh = tabItems.filter((item) => item.is_new).length;
    const colors = CATEGORY_COLORS[tabConfig.category] || CATEGORY_COLORS.edb_circular;

    els.pageStats.innerHTML = `
      <div class="page-stat-card" style="border-color:${colors.color}">
        <div class="page-stat-label" style="color:${colors.color}">${tabLabel}</div>
        <div class="page-stat-value">${tabItems.length}</div>
        <div class="page-stat-new">${fresh} 項新資料</div>
      </div>
    `;
    renderSubcategoryTabs();
    return;
  }

  const total = snapshot.counts?.[pageCategory] || 0;
  const fresh = snapshot.new_counts?.[pageCategory] || 0;
  const colors = CATEGORY_COLORS[pageCategory] || CATEGORY_COLORS.edb_circular;

  els.pageStats.innerHTML = `
    <div class="page-stat-card" style="border-color:${colors.color}">
      <div class="page-stat-label" style="color:${colors.color}">${getCategoryLabel(pageCategory)}</div>
      <div class="page-stat-value">${total}</div>
      <div class="page-stat-new">${fresh} 項新資料</div>
    </div>
  `;
}

function filteredItems() {
  return (snapshot.items || [])
    .filter((item) => {
      if (item.category !== pageCategory) return false;
      if (tabConfig && activeSubcategoryTab) {
        const key = item.subcategory || tabConfig.fallback;
        if (key !== activeSubcategoryTab) return false;
      }
      if (newOnly && !item.is_new) return false;
      if (!searchQuery) return true;
      const blob = `${item.title} ${item.summary} ${item.category_label} ${item.subcategory_label || ""} ${item.level_label || ""}`.toLowerCase();
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
  if (!els.cardsGrid) return;

  els.cardsGrid.innerHTML = "";
  els.emptyState.classList.toggle("hidden", items.length > 0);

  items.forEach((item) => {
    const node = els.cardTemplate.content.cloneNode(true);
    const card = node.querySelector(".card");
    const categoryBadge = node.querySelector(".category-badge");
    const subcategoryBadge = node.querySelector(".subcategory-badge");
    const levelBadge = node.querySelector(".level-badge");
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

    if (levelBadge) {
      if (item.level_label) {
        levelBadge.textContent = item.level_label;
        levelBadge.classList.remove("hidden");
      } else {
        levelBadge.classList.add("hidden");
      }
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

function renderCategoryPage() {
  const items = filteredItems();
  const lookback = snapshot.lookback_days || 365;
  const autoUpdate = isLocalServer ? "" : " · 每 6 小時自動更新";
  const tabSuffix = tabConfig && activeSubcategoryTab ? ` · ${getTabLabel(activeSubcategoryTab)}` : "";
  els.metaBar.textContent = `最後更新：${formatTime(snapshot.updated_at)} · 近 ${lookback} 日內 ${items.length} 項${tabSuffix} · 按日期由近到遠排列${autoUpdate}`;
  renderPageStats();
  renderCards(items);
}

function render() {
  if (!snapshot) return;

  renderPageNav();

  if (!pageCategory) {
    renderHome();
    return;
  }

  renderCategoryPage();
}

if (els.refreshBtn) {
  els.refreshBtn.addEventListener("click", () => fetchData(true));
}
if (els.searchInput) {
  els.searchInput.addEventListener("input", (event) => {
    searchQuery = event.target.value.trim().toLowerCase();
    renderCards(filteredItems());
    els.emptyState.classList.toggle("hidden", filteredItems().length > 0);
  });
}
if (els.newOnly) {
  els.newOnly.addEventListener("change", (event) => {
    newOnly = event.target.checked;
    renderCards(filteredItems());
    els.emptyState.classList.toggle("hidden", filteredItems().length > 0);
  });
}
if (tabConfig) {
  window.addEventListener("hashchange", () => {
    initSubcategoryTabFromHash();
    renderCategoryPage();
  });
  initSubcategoryTabFromHash();
}

document.title = pageCategory ? `${pageTitle} · 香港教育更新` : "香港教育更新儀表板";
const heading = document.getElementById("pageHeading");
if (heading && pageCategory) {
  heading.textContent = pageTitle;
}

renderPageNav();
fetchData(false);
