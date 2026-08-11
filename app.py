import pandas as pd
import streamlit as st

# 画面のタイトル・レイアウト設定
st.set_page_config(page_title="ポケモン構築記事検索", layout="centered")

# ① タイトルリンク（href="/" にすることでどんなURLでも確実にトップに戻ります）
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

st.write("シーズンの範囲指定やキーワード入力で検索できます。")


# ② 本文からキーワードの前後を抜き出す関数（スニペット機能）
def get_snippet(text, keyword, snippet_length=120):
  if not isinstance(text, str) or not text:
    return ""

  # キーワード未入力の場合は冒頭120文字を表示
  if not keyword:
    return text[:snippet_length] + ("..." if len(text) > snippet_length else "")

  # キーワードの位置を探す
  idx = text.lower().find(keyword.lower())

  # タイトルのみヒットした等の場合は冒頭を表示
  if idx == -1:
    return text[:snippet_length] + ("..." if len(text) > snippet_length else "")

  # キーワードの前後を計算して切り抜く（前40文字〜後80文字）
  start = max(0, idx - 40)
  end = min(len(text), idx + len(keyword) + 80)

  snippet = text[start:end]

  if start > 0:
    snippet = "..." + snippet
  if end < len(text):
    snippet = snippet + "..."

  return snippet


# CSVデータの読み込み
@st.cache_data
def load_data():
  return pd.read_csv("articles.csv")


try:
  df = load_data()

  # シーズンの一覧を取得してソート
  unique_seasons = sorted([s for s in df["season"].dropna().unique()])

  filtered_df = df.copy()

  # ③ シーズン範囲選択スライダー
  if len(unique_seasons) > 1:
    start_season, end_season = st.select_slider(
        "シーズン範囲を選択:",
        options=unique_seasons,
        value=(unique_seasons[0], unique_seasons[-1]),
    )

    start_idx = unique_seasons.index(start_season)
    end_idx = unique_seasons.index(end_season)
    selected_range = unique_seasons[start_idx : end_idx + 1]

    filtered_df = filtered_df[filtered_df["season"].isin(selected_range)]
  elif len(unique_seasons) == 1:
    st.info(f"対象シーズン: **{unique_seasons[0]}**")

  # ④ キーワード入力欄
  keyword = st.text_input(
      "検索キーワード（例: カイリュー、サイクル、最終1位）:"
  )

  if keyword:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(keyword, case=False, na=False)
        | filtered_df["text"].str.contains(keyword, case=False, na=False)
    ]

  # ⑤ 検索結果の表示
  st.markdown("---")
  st.write(f"### 検索結果: **{len(filtered_df)}** 件")

  for idx, row in filtered_df.iterrows():
    st.subheader(f"[{row['season']}] {row['title']}")
    st.markdown(f"🔗 [記事を読む]({row['url']})")

    # スニペット（抜き出し）を表示
    if pd.notna(row["text"]):
      snippet = get_snippet(str(row["text"]), keyword)
      st.caption(snippet)

    st.divider()

except Exception as e:
  st.error(
      "データの読み込みに失敗しました。`articles.csv`"
      " が正しく配置されているか確認してください。"
  )
