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
        except Exception as e:
            pass
    return res

# 1. 設定頁面
st.set_page_config(page_title="選股功能主選單", layout="centered")
st.components.v1.html(
    """
    <script>
    const viewport = window.parent.document.querySelector('meta[name="viewport"]');
    if (viewport) {
        viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, user-scalable=yes');
    }
    </script>
    """,
    height=0,
)

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
            st.session_state.current_page = 'Main'
            st.rerun()
    with col2:
        if st.button("❌ 關閉應用", type="primary"):
            st.warning("請直接關閉瀏覽器分頁。")

    st.write("---")
#   使用更精準的十六進位網頁色碼（較推薦，可自由調整深淺） #008000 綠色
    sub_df = df[df["GROUP"].astype(str).str.strip() == group_key]
    html_content = "<div style='line-height: 1.5; font-family: sans-serif; font-size: 18px;'>"
   
    is_first_line = True
    for _, row in sub_df.iterrows():
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
        # 綠色 #008000 
        if is_hyperlink:
            html_content += f"<span style='{line_style}'><a href='{desc}' target='_blank' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>{desc}</a></span>"
        else:
            html_content += f"<span style='{line_style}; color: #008000;'>{desc}</span>"
            
    html_content += "</div>"
    st.markdown(html_content, unsafe_allow_html=True)


