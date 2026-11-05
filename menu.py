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

    for _, row in menu_df.iterrows():
        key = str(row["KEY"]).strip() if "KEY" in row else ""
        desc = str(row["OPTION DESCRIPTION"]).strip() if "OPTION DESCRIPTION" in row else ""
        
        if st.button(f"按鈕 {key} : {desc}", use_container_width=True):
            st.session_state.current_page = key
            st.rerun()

# (C) 子選單畫面 (處理精準換行與縮排)
else:
    group_key = st.session_state.current_page
    df = st.session_state.df
    
    # 頂部導航控制列
    col1, col2 = st.columns()
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

    # 【核心修正】：將所有行打包進同一個 HTML 容器中，精準控制每一行的 margin
    html_content = "<div style='line-height: 1.5; font-family: sans-serif;'>"
    
    for _, row in sub_df.iterrows():
        desc = str(row["OPTION DESCRIPTION"]).strip() if "OPTION DESCRIPTION" in row else ""
        is_hyperlink = str(row["HYPERLINK"]).strip().upper() == "Y" if "HYPERLINK" in row else False
        
        # 讀取 position 與 SKIP LINE
        pos_val = int(row["POSITION"]) if ("POSITION" in row and pd.notna(row["POSITION"])) else 50
        skip_val = int(row["SKIP LINE"]) if ("SKIP LINE" in row and pd.notna(row["SKIP LINE"])) else 1
        
        # 根據 Excel 規則計算下方空行距離：
        # skip_val = 1 代表不空行，下方距離設為 2px (緊密貼合)
        # skip_val = 2 代表空 1 行，下方距離設為 22px (拉開一行文字的距離)
        bottom_margin = 2 if skip_val <= 1 else (skip_val - 1) * 22
        
        # 行內樣式：強制消除網頁預設邊距，改用精準計算的 padding/margin
        line_style = f"margin-left: {pos_val}px; margin-top: 0px; margin-bottom: {bottom_margin}px; padding: 0px; display: block;"

        if is_hyperlink:
            # 超連結行
            html_content += f"<span style='{line_style}'><a href='{desc}' target='_blank' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>{desc}</a></span>"
        else:
            # 一般文字行
            html_content += f"<span style='{line_style}; color: #333;'>{desc}</span>"
            
    html_content += "</div>"

    # 一次性渲染整頁，確保瀏覽器不產生多餘段落間距
    st.markdown(html_content, unsafe_allow_html=True)


