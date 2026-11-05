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
        st.session_state.df = pd.read_excel("data.xlsx")
        st.session_state.df.columns = st.session_state.df.columns.str.strip()
    except Exception as e:
        st.error(f"無法讀取 data.xlsx 檔案，請確認是否與 menu.py 置於同目錄下。錯誤原因: {e}")
        st.stop()

# 3. 初始化頁面路由狀態 (Main 代表主選單，其他代表子選單的 GROUP 名稱)
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Main'

# ----------------- 畫面渲染開始 -----------------

# (A) & (B) 主選單畫面
if st.session_state.current_page == 'Main':
    welcome_title = read_reference_title()
    st.markdown(f"<h3 style='text-align: center; color: #333;'>{welcome_title}</h3>", unsafe_allow_html=True)
    st.write("---")

    # 篩選主選單項目
    df = st.session_state.df
    menu_df = df[df["GROUP"].astype(str).str.strip() == "MENU"]

    # 依序繪製主選單按鈕
    for _, row in menu_df.iterrows():
        key = str(row["KEY"]).strip()
        desc = str(row["Option Description"]).strip()
        
        # 利用 Streamlit 按鈕切換頁面狀態
        if st.button(f"按鈕 {key} : {desc}", use_container_width=True):
            st.session_state.current_page = key
            st.rerun()

# (C) 子選單畫面 (例如：點選 B 進入玩股網選股)
else:
    group_key = st.session_state.current_page
    df = st.session_state.df
    
    # 頂部導航控制列
    col1, col2 = st.columns([8, 2])
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

    for _, row in sub_df.iterrows():
        desc = str(row["Option Description"]).strip()
        is_hyperlink = str(row["hyperlink"]).strip().upper() == "Y"
        
        # 排版對齊參數 (轉換為網頁適用的縮排間距)
        pos_val = int(row["position"]) if pd.notna(row["position"]) else 50
        skip_val = int(row["SKIP LINE"]) if pd.notna(row["SKIP LINE"]) else 1
        
        # 轉換成 HTML 網頁樣式
        margin_style = f"margin-left: {pos_val}px; margin-bottom: {skip_val * 8}px;"

        if is_hyperlink:
            # 如果是超連結，渲染為網頁可點擊的藍色連結
            st.markdown(f"<div style='{margin_style}'><a href='{desc}' target='_blank' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>{desc}</a></div>", unsafe_allow_html=True)
        else:
            # 一般文字說明
            st.markdown(f"<div style='{margin_style}; color: #333;'>{desc}</div>", unsafe_allow_html=True)


