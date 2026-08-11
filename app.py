import pandas as pd
import streamlit as st

# 画面のタイトル設定
st.set_page_config(page_title="ポケモン構築記事検索", layout="centered")

st.title("🔍 ポケモン構築記事 検索")
st.write("シーズン選択とキーワード入力で検索できます。")


# CSVデータの読み込み
@st.cache_data
def load_data():
  return pd.read_csv("articles.csv")


try:
  df = load_data()

  # ① シーズン選択ドロップダウン
  seasons = ["指定なし"] + sorted(list(df["season"].unique()))
  selected_season = st.selectbox("シーズンを選択:", seasons)

  # ② キーワード入力欄
  keyword = st.text_input("検索キーワード（例: カイリュー、サイクル、最終1位）:")

  # データの絞り込み
  filtered_df = df.copy()

  if selected_season != "指定なし":
    filtered_df = filtered_df[filtered_df["season"] == selected_season]

  if keyword:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(keyword, case=False, na=False)
        | filtered_df["text"].str.contains(keyword, case=False, na=False)
    ]

  # ③ 検索結果の表示
  st.markdown("---")
  st.write(f"### 検索結果: **{len(filtered_df)}** 件")

  for idx, row in filtered_df.iterrows():
    st.subheader(f"[{row['season']}] {row['title']}")
    st.markdown(f"🔗 [記事を読む]({row['url']})")

    # 本文の冒頭を少しだけ表示
    if pd.notna(row["text"]):
      st.caption(str(row["text"])[:150] + "...")
    st.divider()

except Exception as e:
  st.error(
      "データの読み込みに失敗しました。`articles.csv`"
      " が正しく配置されているか確認してください。"
  )
