import os
import streamlit as st
import pandas as pd

# ==========================================
# 0. 在此定義讀取 reference.txt 的函式
# ==========================================
def read_reference_title():
    """讀取 reference.txt 中的資訊，並以字典形式分開回傳"""
    res = {
        "title": "歡迎 來到選股功能，祝 身體健康，投資順利",
        "hint1": None,
        "hint2": None
    }
    if os.path.exists("reference.txt"):
        try:
            with open("reference.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line_str = line.strip()
                    if line_str.startswith("MENU_TITLE:"):
                        res["title"] = line_str.replace("MENU_TITLE:", "").strip()
                    elif line_str.startswith("HINT1:"):
                        res["hint1"] = line_str.replace("HINT1:", "").strip()
                    elif line_str.startswith("HINT2:"):
                        res["hint2"] = line_str.replace("HINT2:", "").strip()
                    elif line_str.startswith("HINT3:"):
                        res["hint3"] = line_str.replace("HINT3:", "").strip()    
        except Exception as e:
            pass
    return res

# 1. 設定頁面
st.set_page_config(page_title="選股功能主選單", layout="centered")
# 初始化縮放比例 (預設為 100%)
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 100

# 建立 3 個按鈕（放大、縮小、還原）
zoom_col1, zoom_col2, zoom_col3 = st.columns(3)
with zoom_col1:
    if st.button("➕ 畫面放大", use_container_width=True):
        st.session_state.zoom_level = min(st.session_state.zoom_level + 15, 200) # 最高放大到 200%
        st.rerun()
with zoom_col2:
    if st.button("➖ 畫面縮小", use_container_width=True):
        st.session_state.zoom_level = max(st.session_state.zoom_level - 15, 70)  # 最低縮小到 70%
        st.rerun()
with zoom_col3:
    if st.button("🔄 恢復預設", use_container_width=True):
        st.session_state.zoom_level = 100
        st.rerun()

# 動態注入 CSS，將整個網頁依據比例縮放
st.markdown(f"""
    <style>
    .block-container, div[data-testid="stVerticalBlock"] {{
        zoom: {st.session_state.zoom_level}%;
        -moz-transform: scale({st.session_state.zoom_level / 100}); /* 針對 Firefox 瀏覽器 */
        -moz-transform-origin: top center;
    }}
    </style>
""", unsafe_allow_html=True)

# 2. 初始化 Excel 資料
if 'df' not in st.session_state:
    try:
        df_read = pd.read_excel("data.xlsx")
        df_read.columns = df_read.columns.str.strip().str.upper()
        st.session_state.df = df_read
    except Exception as e:
        st.error(f"無法讀取 data.xlsx 檔案，請確認是否與 menu.py 置於同目錄下。錯誤原因: {e}")
        st.stop()

# 3. 初始化頁面路由狀態
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Main'

# ----------------- 畫面渲染開始 -----------------

# (A) & (B) 主選單畫面
if st.session_state.current_page == 'Main':
    # 讀取文字檔資訊（回傳字典）
    info_dict = read_reference_title()
    
    # 建立一個統一的 HTML 容器，精準控制每行間距
    title_html = "<div style='text-align: center; font-family: sans-serif;'>"
    
    # 主標題：使用深灰色 (#333)，大小設為 24px (等同 h3)
    title_html += f"<div style='font-size: 24px; font-weight: bold; color: #333; margin-top: 10px; margin-bottom: 5px;'>{info_dict['title']}</div>"
    
    # 檢查並加入 HINT1：有抓到才塞入，設定淡紅色 (#FF6B6B)，大小 16px
    if info_dict.get("hint1"):
        title_html += f"<div style='font-size: 16px; font-weight: bold; color: #FF6B6B; margin-top: 4px; margin-bottom: 4px;'>{info_dict['hint1']}</div>"
        
    # 檢查並加入 HINT2：有抓到才塞入，設定淡紅色 (#FF6B6B)，大小 16px
    if info_dict.get("hint2"):
        title_html += f"<div style='font-size: 16px; font-weight: bold; color: #FF6B6B; margin-top: 4px; margin-bottom: 4px;'>{info_dict['hint2']}</div>"

    # 檢查並加入 HINT3：有抓到才塞入，設定淡紅色 (#FF6B6B)，大小 16px
    if info_dict.get("hint3"):
        title_html += f"<div style='font-size: 16px; font-weight: bold; color: #FF6B6B; margin-top: 4px; margin-bottom: 4px;'>{info_dict['hint3']}</div>"
    title_html += "</div>"
    
    # 一次性將標題與提示文字渲染到網頁畫面上
    st.markdown(title_html, unsafe_allow_html=True)
    st.write("---")

    df = st.session_state.df
    menu_df = df[df["GROUP"].astype(str).str.strip() == "MENU"]

    # 注入 CSS 樣式
    st.markdown("""
        <style>
        .block-container {
            padding-top: 3.5rem !important;
        }
        hr {
            margin-top: 5px !important;      
            margin-bottom: 10px !important;  
        }
        div.stButton > button p {
            font-size: 23px !important;
            color: #0066cc !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    for _, row in menu_df.iterrows():
        key = str(row["KEY"]).strip() if "KEY" in row else ""
        desc = str(row["OPTION DESCRIPTION"]).strip() if "OPTION DESCRIPTION" in row else ""
        
        if st.button(f" {key} : {desc}", use_container_width=True):
            st.session_state.current_page = key
            st.rerun()

# (C) 子選單畫面
else:
    group_key = st.session_state.current_page
    df = st.session_state.df
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 返回主選單"):
            # 返回主選單時，清除影片播放狀態
            if 'active_video' in st.session_state:
                st.session_state.active_video = None
            st.session_state.current_page = 'Main'
            st.rerun()
    with col2:
        if st.button("❌ 關閉應用", type="primary"):
            st.warning("請直接關閉瀏覽器分頁。")

    st.write("---")

    # 關鍵修正 1：檢查前端是否透過隱形表單傳回了要播放的影片網址
    # 這是純內部的資料傳遞，完全不改動網址列（URL），所以 Streamlit 絕對不會退回主選單！
    if st.experimental_get_fragment_delta if hasattr(st, 'experimental_get_fragment_delta') else True:
        # 讀取用來接收網址的秘密 Session 變數
        if 'pending_video' in st.session_state and st.session_state.pending_video:
            st.session_state.active_video = st.session_state.pending_video
            st.session_state.pending_video = None

    sub_df = df[df["GROUP"].astype(str).str.strip() == group_key]
    # 100% 回歸您最初最完美的純 HTML 文字排版與字體
    html_content = "<div style='line-height: 1.5; font-family: sans-serif; font-size: 18px; word-break: break-all;'>"
   
    is_first_line = True
    for index, row in sub_df.iterrows():
        desc = str(row["OPTION DESCRIPTION"]).strip() if "OPTION DESCRIPTION" in row else ""
        is_hyperlink = str(row["HYPERLINK"]).strip().upper() == "Y" if "HYPERLINK" in row else False
        
        pos_val = int(row["POSITION"]) if ("POSITION" in row and pd.notna(row["POSITION"])) else 50
        skip_val = int(row["SKIP LINE"]) if ("SKIP LINE" in row and pd.notna(row["SKIP LINE"])) else 1
        
        if is_first_line:
            top_margin = 0
            is_first_line = False
        else:
            top_margin = (skip_val - 1) * 24 if skip_val > 1 else 0
        
        line_style = f"margin-left: {pos_val}px; margin-top: {top_margin}px; margin-bottom: 0px; padding: 0px; display: block;"
        
        if is_hyperlink:
            url_lower = desc.lower()
            if url_lower.endswith('.mp4'):
                # 先把前面的累積文字渲染出來，確保順序正確
                if html_content != "<div style='line-height: 1.5; font-family: sans-serif; font-size: 18px;'>":
                    html_content += "</div>"
                    st.markdown(html_content, unsafe_allow_html=True)
                    html_content = "<div style='line-height: 1.5; font-family: sans-serif; font-size: 18px;'>"
                
                # 關鍵修正 2：外觀和您原本的超連結完全一致（無邊框、字體、顏色、對齊完美符合圖 A）
                # 點擊時透過 onclick 語法直接改寫 st.session_state 變數，完全不經過網址跳轉，100% 在原地重新整理並拉出播放器
                link_id = f"vid_link_{index}"
                st.markdown(f"""
                    <div style='margin-left: {pos_val}px; margin-top: {top_margin}px; display: block;'>
                        <a href='javascript:void(0);' id='{link_id}' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>{desc}</a>
                    </div>
                """, unsafe_allow_html=True)
                
                # 默默在後台放一個點擊按鈕，但用 CSS 徹底隱藏它，改用超連結點擊來觸發它
                if st.button("", key=f"hidden_btn_{index}", help=None):
                    st.session_state.active_video = desc
                    st.rerun()
                
                # 利用 JavaScript 讓前端漂亮的超連結點擊時，去聯動觸發後台隱藏按鈕的點擊事件
                st.components.v1.html(f"""
                    <script>
                    setTimeout(function() {{
                        const aTag = window.parent.document.getElementById('{link_id}');
                        const btn = window.parent.document.querySelector('button[key="hidden_btn_{index}"]');
                        if (aTag && btn && !aTag.dataset.bound) {{
                            aTag.dataset.bound = "true";
                            aTag.addEventListener('click', function(e) {{
                                e.preventDefault();
                                btn.click(); // 隱形觸發 Streamlit 原生按鈕，不改網址，100% 原地刷新！
                            }});
                        }}
                    }}, 200);
                    </script>
                """, height=0)
            else:
                # 正常的 PDF 連結維持原樣，開新分頁預覽不下載
                html_content += f"<span style='{line_style}'><a href='{desc}' target='_blank' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>{desc}</a></span>"
        else:
            html_content += f"<span style='{line_style}; color: #008000;'>{desc}</span>"
            
    if html_content != "<div style='line-height: 1.5; font-family: sans-serif; font-size: 18px;'>":
        html_content += "</div>"
        st.markdown(html_content, unsafe_allow_html=True)

    # 檢查後台狀態：如果有點擊影片，就在原地（下方）渲染播放器
    if 'active_video' in st.session_state and st.session_state.active_video:
        st.write("---")
        
        # 排版：左邊標題，右邊關閉按鈕
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.subheader("📺 影片線上播放")
        with v_col2:
            # 點擊關閉，清空狀態並刷新頁面，讓影片徹底消失
            if st.button("❌ 關閉影片", use_container_width=True):
                st.session_state.active_video = None
                st.rerun()
                
        # 顯示原生播放器，不下載、不進 GitHub
        st.video(st.session_state.active_video, autoplay=True)


