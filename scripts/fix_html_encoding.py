from pathlib import Path

INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-HK">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>香港教育更新儀表板</title>
  <link rel="stylesheet" href="styles.css?v=5" />
</head>
<body>
  <div class="page">
    <header class="header">
      <div class="header-top">
        <div>
          <p class="eyebrow">Hong Kong Education Monitor</p>
          <h1>香港教育更新儀表板</h1>
          <p class="subtitle">八個分類獨立頁面 · 小學／中學比賽 · 獎學金 · 教師培訓 · 新聞 · QEF · 通函</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" id="refreshBtn" title="本機模式會重新擷取；GitHub Pages 會重新載入快取資料">重新整理</button>
        </div>
      </div>
      <nav class="page-nav" id="pageNav"></nav>
      <div class="meta" id="metaBar">載入中…</div>
      <section class="home-grid" id="homeGrid"></section>
    </header>

    <main>
      <div class="loading hidden" id="loading">
        <div class="spinner"></div>
        <p>正在載入資料…</p>
      </div>
      <div class="empty hidden" id="emptyState">
        <p>沒有符合條件的項目</p>
      </div>
    </main>
  </div>

  <script src="app.js?v=5"></script>
</body>
</html>
"""

SKIP = {"steam-primary.html", "steam-secondary.html", "competitions.html"}


def bump_cache(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace('href="styles.css?v=4"', 'href="styles.css?v=5"')
    if 'href="styles.css?v=' not in text:
        text = text.replace('href="styles.css"', 'href="styles.css?v=5"')
    text = text.replace('src="app.js?v=4"', 'src="app.js?v=5"')
    if 'src="app.js?v=' not in text:
        text = text.replace('src="app.js"', 'src="app.js?v=5"')
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    index_path = Path("web/index.html")
    index_path.write_text(INDEX_HTML, encoding="utf-8", newline="\n")
    assert "香港教育" in index_path.read_text(encoding="utf-8")
    print("wrote index.html")

    for path in sorted(Path("web").glob("*.html")):
        if path.name in SKIP or path.name == "index.html":
            continue
        bump_cache(path)
        print(f"updated {path.name}")


if __name__ == "__main__":
    main()
