import re
import pandas as pd
import requests
import streamlit as st

# 画面設定（ブラウザのタブ名）
st.set_page_config(
    page_title="ポケモンチャンピオンズ構築記事全文検索システム",
    layout="centered",
)

# --------------------------------------------------
# 📊 GA4 Measurement Protocol (サーバーサイド直接送信)
# --------------------------------------------------
GA_MEASUREMENT_ID = "G-8RE88QPRYD"
API_SECRET = "ここに取得したAPI秘密鍵を貼り付け"


def track_page_view():
  """アプリが開かれたときにGA4へアクセスデータを直接POST送信する"""
  if API_SECRET and API_SECRET != "ここに取得したAPI秘密鍵を貼り付け":
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={API_SECRET}"
    payload = {
        "client_id": "streamlit_user",
        "events": [{
            "name": "page_view",
            "params": {
                "page_title": "ポケモンチャンピオンズ構築記事全文検索システム",
                "page_location": "https://pokemon-search.streamlit.app/",
            },
        }],
    }
    try:
      requests.post(url, json=payload, timeout=2)
    except Exception:
      pass


# ページ読み込み時にトラッキング実行
track_page_view()

# --------------------------------------------------
# 🔍 ポケモン構築記事 検索アプリ メイン処理
# --------------------------------------------------

# タイトル（サイズを小さく控えめに指定）
st.markdown(
    """
    <h3 style="font-size: 1.3rem; margin-bottom: 0.5rem; font-weight: 600;">
        <a href="/" target="_self" style="color: inherit; text-decoration: none;">
            🔍 ポケモンチャンピオンズ構築記事全文検索システム
        </a>
    </h3>
    """,
    unsafe_allow_html=True,
)

st.write("シーズン指定やキーワード入力で記事のタイトル・本文から一括検索できます。")


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

  # --------------------------------------------------
  # 📅 期間選択 (プルダウン2つを横並び)
  # --------------------------------------------------
  if "season" in df.columns:
    unique_seasons = sorted([str(s) for s in df["season"].dropna().unique()])

    if len(unique_seasons) > 0:
      st.write("**対象の期間を選択:**")
      col1, col2, col3 = st.columns([5, 1, 5])

      with col1:
        start_season = st.selectbox(
            "開始シーズン",
            options=unique_seasons,
            index=0,  # 一番最初のシーズン
            label_visibility="collapsed",
        )

      with col2:
        st.markdown(
            "<p style='text-align: center; font-size: 20px;"
            " margin-top: 5px;'>〜</p>",
            unsafe_allow_html=True,
        )

      with col3:
        end_season = st.selectbox(
            "終了シーズン",
            options=unique_seasons,
            index=len(unique_seasons) - 1,  # 一番新しいシーズン
            label_visibility="collapsed",
        )

      # 選択された範囲に含まれるシーズンを抽出
      start_idx = unique_seasons.index(start_season)
      end_idx = unique_seasons.index(end_season)

      # 逆順で選ばれても安全に対応する処理
      min_idx, max_idx = min(start_idx, end_idx), max(start_idx, end_idx)
      selected_range = unique_seasons[min_idx : max_idx + 1]

      filtered_df = filtered_df[filtered_df["season"].isin(selected_range)]

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
    season_prefix = (
        f"[{row['season']}] "
        if ("season" in row and pd.notna(row["season"]))
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
