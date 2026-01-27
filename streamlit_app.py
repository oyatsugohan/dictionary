import streamlit as st
import json
import os
import hashlib
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image

# ファイルパス
USERS_FILE = "users_data.json"

# パスワードのハッシュ化
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 画像をBase64エンコード
def encode_image(image_file):
    """アップロードされた画像をBase64文字列に変換"""
    if image_file is not None:
        return base64.b64encode(image_file.read()).decode()
    return None

# Base64文字列を画像に変換
def decode_image(base64_string):
    """Base64文字列を画像に変換"""
    if base64_string:
        return Image.open(BytesIO(base64.b64decode(base64_string)))
    return None

# 画像を指定した高さにリサイズ
def resize_image_by_height(image, target_height):
    """画像をアスペクト比を保ったまま指定した高さにリサイズ"""
    if image:
        # アスペクト比を計算
        aspect_ratio = image.width / image.height
        new_width = int(target_height * aspect_ratio)
        # リサイズ
        resized = image.resize((new_width, target_height), Image.Resampling.LANCZOS)
        return resized
    return None

# ユーザーデータの読み込み
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ユーザーデータの保存
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ユーザーの百科事典データを取得
def get_user_encyclopedia(username):
    users = load_users()
    if username in users:
        return users[username].get("encyclopedia", {})
    return {}

# ユーザーの百科事典データを保存
def save_user_encyclopedia(username, encyclopedia):
    users = load_users()
    if username in users:
        users[username]["encyclopedia"] = encyclopedia
        save_users(users)

# アプリの設定
st.set_page_config(page_title="オリジナル百科事典", page_icon="📚", layout="wide")

# セッション状態の初期化
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "encyclopedia" not in st.session_state:
    st.session_state.encyclopedia = {}

# ログイン/サインアップ画面
if not st.session_state.logged_in:
    st.title("📚 オリジナル百科事典")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 ログイン", "✍️ 新規登録"])
    
    with tab1:
        st.header("ログイン")
        with st.form("login_form"):
            username = st.text_input("ユーザー名")
            password = st.text_input("パスワード", type="password")
            login_button = st.form_submit_button("ログイン")
            
            if login_button:
                users = load_users()
                if username in users:
                    if users[username]["password"] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.encyclopedia = get_user_encyclopedia(username)
                        st.success(f"ようこそ、{username}さん！")
                        st.rerun()
                    else:
                        st.error("パスワードが間違っています")
                else:
                    st.error("ユーザー名が見つかりません")
    
    with tab2:
        st.header("新規登録")
        with st.form("signup_form"):
            new_username = st.text_input("ユーザー名（半角英数字推奨）")
            new_password = st.text_input("パスワード", type="password")
            confirm_password = st.text_input("パスワード（確認）", type="password")
            signup_button = st.form_submit_button("登録")
            
            if signup_button:
                if not new_username or not new_password:
                    st.error("ユーザー名とパスワードを入力してください")
                elif new_password != confirm_password:
                    st.error("パスワードが一致しません")
                elif len(new_password) < 4:
                    st.error("パスワードは4文字以上で設定してください")
                else:
                    users = load_users()
                    if new_username in users:
                        st.error("このユーザー名は既に使用されています")
                    else:
                        users[new_username] = {
                            "password": hash_password(new_password),
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "encyclopedia": {}
                        }
                        save_users(users)
                        st.success("登録が完了しました！ログインしてください。")

else:
    # ログイン後のメイン画面
    
    # タイトルとログアウトボタン
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"📚 {st.session_state.username}の百科事典")
    with col2:
        if st.button("🚪 ログアウト"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.encyclopedia = {}
            st.rerun()
    
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("メニュー")
        menu = st.radio("機能を選択", ["🔍 記事を検索", "➕ 新規記事作成", "📝 記事を編集", "🗑️ 記事を削除", "📊 統計情報"])
        
        st.markdown("---")
        
        # 記事一覧の表示/非表示
        show_list = st.checkbox("📖 登録済み記事一覧を表示", value=True)
        
        if show_list:
            if st.session_state.encyclopedia:
                for title in sorted(st.session_state.encyclopedia.keys()):
                    st.text(f"• {title}")
            else:
                st.info("まだ記事がありません")
    
    # メイン画面
    if menu == "🔍 記事を検索":
        st.header("記事を検索")
        
        if st.session_state.encyclopedia:
            # カテゴリー一覧を取得（リスト形式にも対応）
            all_categories = set()
            for article in st.session_state.encyclopedia.values():
                cats = article.get("category", ["未分類"])
                if isinstance(cats, list):
                    all_categories.update(cats)
                else:
                    all_categories.add(cats)
            all_categories = sorted(all_categories)
            
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
                          if selected_category in (v.get("category", ["未分類"]) if isinstance(v.get("category", []), list) else [v.get("category", "未分類")])}
            
            if results:
                st.success(f"{len(results)}件の記事が見つかりました")
                for title, content in sorted(results.items()):
                    with st.expander(f"📄 {title}"):
                        # カテゴリー表示（リスト形式にも対応）
                        cats = content.get('category', ['未分類'])
                        if isinstance(cats, list):
                            category_display = ", ".join(cats)
                        else:
                            category_display = cats
                        st.markdown(f"**カテゴリー:** {category_display}")
                        st.markdown(f"**作成日:** {content.get('created', '不明')}")
                        st.markdown("---")
                        
                        # 画像を表示（高さ50pxに制限）
                        if content.get('image'):
                            img = decode_image(content['image'])
                            if img:
                                resized_img = resize_image_by_height(img, 50)
                                st.image(resized_img, caption=f"{title}の画像")
                                st.markdown("---")
                        
                        st.text(content.get('content', ''))
            else:
                st.warning("該当する記事が見つかりませんでした")
        else:
            st.info("まだ記事がありません。「新規記事作成」から記事を追加してください。")
    
    elif menu == "➕ 新規記事作成":
        st.header("新規記事作成")
        
        with st.form("new_article"):
            title = st.text_input("📝 記事タイトル", placeholder="例: Python")
            category = st.text_input("🏷️ カテゴリー", placeholder="例: プログラミング言語, 技術 (カンマ区切りで複数指定可能)")
            
            # 画像アップロード
            uploaded_image = st.file_uploader("🖼️ 画像を追加（任意）", type=['png', 'jpg', 'jpeg', 'gif', 'webp'])
            if uploaded_image:
                preview_img = Image.open(uploaded_image)
                resized_preview = resize_image_by_height(preview_img, 50)
                st.image(resized_preview, caption="プレビュー")
            
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
                    # カテゴリーをリスト形式に変換（カンマ区切り）
                    categories = [cat.strip() for cat in category.split(",") if cat.strip()]
                    if not categories:
                        categories = ["未分類"]
                    
                    # 画像をエンコード
                    image_data = None
                    if uploaded_image:
                        uploaded_image.seek(0)  # ファイルポインタを先頭に戻す
                        image_data = encode_image(uploaded_image)
                    
                    st.session_state.encyclopedia[title] = {
                        "category": categories,
                        "content": content,
                        "image": image_data,
                        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_user_encyclopedia(st.session_state.username, st.session_state.encyclopedia)
                    st.success(f"✅ 記事「{title}」を保存しました！")
                    st.balloons()
    
    elif menu == "📝 記事を編集":
        st.header("記事を編集")
        
        if st.session_state.encyclopedia:
            article_to_edit = st.selectbox("編集する記事を選択", sorted(st.session_state.encyclopedia.keys()))
            
            if article_to_edit:
                current_data = st.session_state.encyclopedia[article_to_edit]
                
                # カテゴリーをリストから文字列に変換
                current_categories = current_data.get("category", [])
                if isinstance(current_categories, list):
                    category_str = ", ".join(current_categories)
                else:
                    category_str = current_categories
                
                with st.form("edit_article"):
                    new_title = st.text_input("📝 記事タイトル", value=article_to_edit)
                    new_category = st.text_input("🏷️ カテゴリー", value=category_str, placeholder="カンマ区切りで複数指定可能")
                    
                    # 既存の画像を表示（高さ50pxに制限）
                    if current_data.get('image'):
                        st.write("**現在の画像:**")
                        current_img = decode_image(current_data['image'])
                        if current_img:
                            resized_current = resize_image_by_height(current_img, 50)
                            st.image(resized_current, caption="現在の画像")
                    
                    # 画像の更新
                    uploaded_image = st.file_uploader("🖼️ 新しい画像をアップロード（任意・空欄の場合は既存の画像を保持）", 
                                                     type=['png', 'jpg', 'jpeg', 'gif', 'webp'])
                    if uploaded_image:
                        new_preview_img = Image.open(uploaded_image)
                        resized_new_preview = resize_image_by_height(new_preview_img, 50)
                        st.image(resized_new_preview, caption="新しい画像のプレビュー")
                    
                    # 画像削除オプション
                    delete_image = st.checkbox("🗑️ 画像を削除する")
                    
                    new_content = st.text_area("✍️ 記事内容", value=current_data.get("content", ""), height=300)
                    
                    submitted = st.form_submit_button("💾 更新を保存")
                    
                    if submitted:
                        if not new_title:
                            st.error("タイトルを入力してください")
                        elif not new_content:
                            st.error("記事内容を入力してください")
                        else:
                            # カテゴリーをリスト形式に変換
                            categories = [cat.strip() for cat in new_category.split(",") if cat.strip()]
                            if not categories:
                                categories = ["未分類"]
                            
                            # 画像の処理
                            image_data = current_data.get('image')  # 既存の画像を保持
                            
                            if delete_image:
                                image_data = None  # 画像を削除
                            elif uploaded_image:
                                uploaded_image.seek(0)
                                image_data = encode_image(uploaded_image)  # 新しい画像に更新
                            
                            # 古いタイトルのデータを削除
                            if new_title != article_to_edit:
                                del st.session_state.encyclopedia[article_to_edit]
                            
                            # 新しいデータを保存
                            st.session_state.encyclopedia[new_title] = {
                                "category": categories,
                                "content": new_content,
                                "image": image_data,
                                "created": current_data.get("created", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_user_encyclopedia(st.session_state.username, st.session_state.encyclopedia)
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
                
                # プレビュー表示（高さ50pxに制限）
                preview_data = st.session_state.encyclopedia[article_to_delete]
                if preview_data.get('image'):
                    img = decode_image(preview_data['image'])
                    if img:
                        resized_delete_preview = resize_image_by_height(img, 50)
                        st.image(resized_delete_preview, caption="この画像も削除されます")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ 削除", type="primary"):
                        del st.session_state.encyclopedia[article_to_delete]
                        save_user_encyclopedia(st.session_state.username, st.session_state.encyclopedia)
                        st.success(f"記事「{article_to_delete}」を削除しました")
                        st.rerun()
                with col2:
                    st.empty()
        else:
            st.info("削除する記事がありません")
    
    elif menu == "📊 統計情報":
        st.header("統計情報")
        
        if st.session_state.encyclopedia:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📚 総記事数", len(st.session_state.encyclopedia))
            
            with col2:
                all_categories = set()
                for article in st.session_state.encyclopedia.values():
                    cats = article.get("category", ["未分類"])
                    if isinstance(cats, list):
                        all_categories.update(cats)
                    else:
                        all_categories.add(cats)
                st.metric("🏷️ カテゴリー数", len(all_categories))
            
            with col3:
                total_chars = sum(len(v.get("content", "")) for v in st.session_state.encyclopedia.values())
                st.metric("✍️ 総文字数", f"{total_chars:,}")
            
            with col4:
                image_count = sum(1 for v in st.session_state.encyclopedia.values() if v.get("image"))
                st.metric("🖼️ 画像付き記事", image_count)
            
            st.markdown("---")
            st.subheader("カテゴリー別記事数")
            
            category_count = {}
            for article in st.session_state.encyclopedia.values():
                cats = article.get("category", ["未分類"])
                if isinstance(cats, list):
                    for cat in cats:
                        category_count[cat] = category_count.get(cat, 0) + 1
                else:
                    category_count[cats] = category_count.get(cats, 0) + 1
            
            for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
                st.write(f"**{cat}**: {count}件")
        else:
            st.info("まだ記事がありません")
    
    # フッター
    st.markdown("---")
    st.markdown("💡 **ヒント**: サイドバーから機能を選択して、あなただけの百科事典を作りましょう！")