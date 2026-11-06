import os
import streamlit as st
import pandas as pd

# 1. 讀取標題與設定頁面
st.set_page_config(page_title="選股功能主選單", layout="centered")

def read_reference_title():
    """讀取 reference.txt 中的 MENU_TITLE"""
    title = "歡迎 來到選股功能 , 祝 身體健康 , 投資順利"  # 預設標題
    if os.path.exists("reference.txt"):
        try:
            with open("reference.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MENU_TITLE:"):
                        title = line.replace("MENU_TITLE:", "").strip()
                        break
        except Exception as e:
            pass
    return title

# 2. 初始化 Excel 資料
if 'df' not in st.session_state:
    try:
        df_read = pd.read_excel("data.xlsx")
        # 強制將所有欄位名稱去除前後空白，並統一轉換為大寫
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
    welcome_title = read_reference_title()
    st.markdown(f"<h3 style='text-align: center; color: #333;'>{welcome_title}</h3>", unsafe_allow_html=True)
    st.write("---")

    df = st.session_state.df
    menu_df = df[df["GROUP"].astype(str).str.strip() == "MENU"]

    # 注入 CSS 樣式：強制將頁面上所有 st.button 的字體放大至 28px、顏色設為藍色
    st.markdown("""
        <style>
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

# (C) 子選單畫面 (處理精準換行與縮排)
else:
    group_key = st.session_state.current_page
    df = st.session_state.df
    
    # 頂部導航控制列
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 返回主選單"):
            st.session_state.current_page = 'Main'
            st.rerun()
    with col2:
        if st.button("❌ 關閉應用", type="primary"):
            st.warning("請直接關閉瀏覽器分頁。")

    st.write("---")

    # 篩選對應 GROUP 的資料
    sub_df = df[df["GROUP"].astype(str).str.strip() == group_key]

    # 將所有行打包進同一個 HTML 容器中，精準控制每一行的 margin
    html_content = "<div style='line-height: 1.5; font-family: sans-serif; font-size: 16px;'>"
    
    is_first_line = True
    for _, row in sub_df.iterrows():
        desc = str(row["OPTION DESCRIPTION"]).strip() if "OPTION DESCRIPTION" in row else ""
        is_hyperlink = str(row["HYPERLINK"]).strip().upper() == "Y" if "HYPERLINK" in row else False
        
        # 讀取 position 與 SKIP LINE
        pos_val = int(row["POSITION"]) if ("POSITION" in row and pd.notna(row["POSITION"])) else 50
        skip_val = int(row["SKIP LINE"]) if ("SKIP LINE" in row and pd.notna(row["SKIP LINE"])) else 1
        
        # 【核心公式修正】：改為控制上方間距（margin-top）
        # skip_val = 1 代表跳到下 1 行（不空行），上方距離設為 0px
        # skip_val = 2 代表跳到下 2 行（空 1 行），上方距離設為 24px（一行字高度）
        # 如果是子選單的第一行，則不強制空行，維持原本網頁頂部自然間距
        if is_first_line:
            top_margin = 0
            is_first_line = False
        else:
            top_margin = (skip_val - 1) * 24 if skip_val > 1 else 0
        
        # 行內樣式：徹底消除瀏覽器預設邊距，改用精準計算的上方間距與縮排
        line_style = f"margin-left: {pos_val}px; margin-top: {top_margin}px; margin-bottom: 0px; padding: 0px; display: block;"

        if is_hyperlink:
            # 超連結行
            html_content += f"<span style='{line_style}'><a href='{desc}' target='_blank' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>{desc}</a></span>"
        else:
            # 一般文字行
            html_content += f"<span style='{line_style}; color: #333;'>{desc}</span>"
            
    html_content += "</div>"

    # 一次性渲染整頁
    st.markdown(html_content, unsafe_allow_html=True)


