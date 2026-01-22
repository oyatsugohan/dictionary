import streamlit as st
import json
import os
from datetime import datetime

# JSONファイルのパス
DATA_FILE = "encyclopedia_data.json"

# データの読み込み
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# データの保存
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# アプリの設定
st.set_page_config(page_title="オリジナル百科事典", page_icon="📚", layout="wide")

# データの読み込み
if "encyclopedia" not in st.session_state:
    st.session_state.encyclopedia = load_data()

# タイトル
st.title("📚 オリジナル百科事典")
st.markdown("---")

# サイドバー
with st.sidebar:
    st.header("メニュー")
    menu = st.radio("機能を選択", ["🔍 記事を検索", "➕ 新規記事作成", "📝 記事を編集", "🗑️ 記事を削除", "📊 統計情報"])
    
    st.markdown("---")
    st.subheader("📖 登録済み記事一覧")
    if st.session_state.encyclopedia:
        for title in sorted(st.session_state.encyclopedia.keys()):
            st.text(f"• {title}")
    else:
        st.info("まだ記事がありません")

# メイン画面
if menu == "🔍 記事を検索":
    st.header("記事を検索")
    
    if st.session_state.encyclopedia:
        # カテゴリー一覧を取得
        all_categories = sorted(set(v.get("category", "未分類") for v in st.session_state.encyclopedia.values()))
        
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("🔎 検索キーワードを入力", placeholder="記事のタイトルで検索")
        with col2:
            selected_category = st.selectbox("🏷️ カテゴリーで絞り込み", ["すべて"] + all_categories)
        
        # 検索結果のフィルタリング
        results = st.session_state.encyclopedia.copy()
        
        # キーワード検索
        if search_term:
            results = {k: v for k, v in results.items() 
                      if search_term.lower() in k.lower()}
        
        # カテゴリーで絞り込み
        if selected_category != "すべて":
            results = {k: v for k, v in results.items() 
                      if v.get("category", "未分類") == selected_category}
        
        if results:
            st.success(f"{len(results)}件の記事が見つかりました")
            for title, content in sorted(results.items()):
                with st.expander(f"📄 {title}"):
                    st.markdown(f"**カテゴリー:** {content.get('category', '未分類')}")
                    st.markdown(f"**作成日:** {content.get('created', '不明')}")
                    st.markdown("---")
                    st.text(content.get('content', ''))
        else:
            st.warning("該当する記事が見つかりませんでした")
    else:
        st.info("まだ記事がありません。「新規記事作成」から記事を追加してください。")

elif menu == "➕ 新規記事作成":
    st.header("新規記事作成")
    
    with st.form("new_article"):
        title = st.text_input("📝 記事タイトル", placeholder="例: あ")
        category = st.text_input("🏷️ カテゴリー", placeholder="例: 文字")
        content = st.text_area("✍️ 記事内容", height=300, placeholder="記事の内容を入力してください...")
        
        submitted = st.form_submit_button("✅ 記事を保存")
        
        if submitted:
            if not title:
                st.error("タイトルを入力してください")
            elif title in st.session_state.encyclopedia:
                st.error("同じタイトルの記事が既に存在します")
            elif not content:
                st.error("記事内容を入力してください")
            else:
                st.session_state.encyclopedia[title] = {
                    "category": category,
                    "content": content,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_data(st.session_state.encyclopedia)
                st.success(f"✅ 記事「{title}」を保存しました！")
                st.balloons()

elif menu == "📝 記事を編集":
    st.header("記事を編集")
    
    if st.session_state.encyclopedia:
        article_to_edit = st.selectbox("編集する記事を選択", sorted(st.session_state.encyclopedia.keys()))
        
        if article_to_edit:
            current_data = st.session_state.encyclopedia[article_to_edit]
            
            with st.form("edit_article"):
                new_title = st.text_input("📝 記事タイトル", value=article_to_edit)
                new_category = st.text_input("🏷️ カテゴリー", value=current_data.get("category", ""))
                new_content = st.text_area("✍️ 記事内容", value=current_data.get("content", ""), height=300)
                
                submitted = st.form_submit_button("💾 更新を保存")
                
                if submitted:
                    if not new_title:
                        st.error("タイトルを入力してください")
                    elif not new_content:
                        st.error("記事内容を入力してください")
                    else:
                        # 古いタイトルのデータを削除
                        if new_title != article_to_edit:
                            del st.session_state.encyclopedia[article_to_edit]
                        
                        # 新しいデータを保存
                        st.session_state.encyclopedia[new_title] = {
                            "category": new_category,
                            "content": new_content,
                            "created": current_data.get("created", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        save_data(st.session_state.encyclopedia)
                        st.success(f"✅ 記事「{new_title}」を更新しました！")
                        st.rerun()
    else:
        st.info("編集する記事がありません")

elif menu == "🗑️ 記事を削除":
    st.header("記事を削除")
    
    if st.session_state.encyclopedia:
        article_to_delete = st.selectbox("削除する記事を選択", sorted(st.session_state.encyclopedia.keys()))
        
        if article_to_delete:
            st.warning(f"本当に「{article_to_delete}」を削除しますか？")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🗑️ 削除", type="primary"):
                    del st.session_state.encyclopedia[article_to_delete]
                    save_data(st.session_state.encyclopedia)
                    st.success(f"記事「{article_to_delete}」を削除しました")
                    st.rerun()
            with col2:
                st.empty()
    else:
        st.info("削除する記事がありません")

elif menu == "📊 統計情報":
    st.header("統計情報")
    
    if st.session_state.encyclopedia:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 総記事数", len(st.session_state.encyclopedia))
        
        with col2:
            categories = [v.get("category", "未分類") for v in st.session_state.encyclopedia.values()]
            unique_categories = len(set(categories))
            st.metric("🏷️ カテゴリー数", unique_categories)
        
        with col3:
            total_chars = sum(len(v.get("content", "")) for v in st.session_state.encyclopedia.values())
            st.metric("✍️ 総文字数", f"{total_chars:,}")
        
        st.markdown("---")
        st.subheader("カテゴリー別記事数")
        
        category_count = {}
        for article in st.session_state.encyclopedia.values():
            cat = article.get("category", "未分類")
            category_count[cat] = category_count.get(cat, 0) + 1
        
        for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
            st.write(f"**{cat}**: {count}件")
    else:
        st.info("まだ記事がありません")

# フッター
st.markdown("---")
st.markdown("💡 **ヒント**: サイドバーから機能を選択して、あなただけの百科事典を作りましょう！")