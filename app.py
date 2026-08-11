import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 画面設定
st.set_page_config(page_title="ポケモン構築記事検索", layout="centered")

# --------------------------------------------------
# 📊 Google アナリティクス (GA4) 埋め込み
# --------------------------------------------------
GA_MEASUREMENT_ID = "G-8RE88QPRYD"

ga_html = f"""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_MEASUREMENT_ID}');
</script>
"""
components.html(ga_html, height=0, width=0)

# --------------------------------------------------
# 🔍 ポケモン構築記事 検索アプリ メイン処理
# --------------------------------------------------

# タイトル
st.markdown(
    """
    <h1>
        <a href="/" target="_self" style="color: inherit; text-decoration: none;">
            🔍 ポケモン構築記事 検索
        </a>
    </h1>
    """,
    unsafe_allow_html=True,
)

st.write("キーワード入力で記事のタイトル・本文から一括検索できます。")


# キーワードハイライト関数
def highlight_text(text, keyword):
  if not keyword or not isinstance(text, str):
    return text
  pattern = re.escape(keyword)
  return re.sub(f"({pattern})", r"**\1**", text, flags=re.IGNORECASE)


# 本文スニペット抽出関数
def get_snippet(text, keyword, snippet_length=120):
  if not isinstance(text, str) or not text:
    return ""
  if not keyword:
    return text[:snippet_length] + ("..." if len(text) > snippet_length else "")

  idx = text.lower().find(keyword.lower())
  if idx == -1:
    return text[:snippet_length] + ("..." if len(text) > snippet_length else "")

  start = max(0, idx - 40)
  end = min(len(text), idx + len(keyword) + 80)
  snippet = text[start:end]

  if start > 0:
    snippet = "..." + snippet
  if end < len(text):
    snippet = snippet + "..."
  return snippet


# CSVデータ読み込み
@st.cache_data
def load_data():
  return pd.read_csv("articles.csv")


try:
  df = load_data()
  filtered_df = df.copy()

  # キーワード入力欄
  keyword = st.text_input(
      "検索キーワード（例: カイリュー、サイクル、最終1位）:"
  )

  if keyword:
    condition = filtered_df["title"].str.contains(keyword, case=False, na=False)
    if "text" in filtered_df.columns:
      condition = condition | filtered_df["text"].str.contains(
          keyword, case=False, na=False
      )
    filtered_df = filtered_df[condition]

  # 検索結果件数
  st.markdown("---")
  st.write(f"### 検索結果: **{len(filtered_df)}** 件")

  # 記事リストのループ表示
  for idx, row in filtered_df.iterrows():
    # シーズン表示（変な文字が入っている場合は無視して[M-4]固定にする安全ガード）
    season_str = str(row.get("season", ""))
    season_prefix = (
        "[M-4] "
        if "M-4" in season_str
        else f"[{season_str}] "
        if (season_str and len(season_str) < 10)
        else ""
    )

    display_title = highlight_text(str(row["title"]), keyword)

    st.subheader(f"{season_prefix}{display_title}")
    st.markdown(f"🔗 [記事を読む]({row['url']})")

    if "text" in row and pd.notna(row["text"]):
      snippet = get_snippet(str(row["text"]), keyword)
      highlighted_snippet = highlight_text(snippet, keyword)
      st.caption(highlighted_snippet)

    st.divider()

  # サイトフッター注記
  st.markdown("---")
  st.caption(
      "※本サイトは各ブログ・記事の検索サービスであり、著作権は各著作者に帰属します。"
  )

except Exception as e:
  st.error(
      "データの読み込みに失敗しました。`articles.csv`"
      " が正しく配置されているか確認してください。"
  )
