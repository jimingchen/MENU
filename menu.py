import os
import pandas as pd
import streamlit as st

# 調整網頁版面配置為寬版
st.set_page_config(layout="wide")

# 1. 設定檔案路徑（使用 Streamlit 相對路徑）
EXCEL_PATH = "data.xlsx"       
TXT_PATH = "reference.txt"     

# 2. 完全動態讀取 reference.txt 的標題
menu_title = ""
if os.path.exists(TXT_PATH):
    try:
        with open(TXT_PATH, "r", encoding="utf-8-sig") as f:
            for line in f:
                if "MENU_TITLE:" in line:
                    menu_title = line.split("MENU_TITLE:", 1)[1].strip()
                    break
    except Exception as e:
        menu_title = f"[讀取標題出錯: {str(e)}]"
else:
    menu_title = "[找不到 reference.txt 檔案]"

# 3. 讀取 Excel 資料
if os.path.exists(EXCEL_PATH):
    df = pd.read_excel(EXCEL_PATH)
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)
else:
    st.error(f"找不到檔案：{EXCEL_PATH}，請確認檔案已上傳至 GitHub。")
    st.stop()

# 4. 定義網頁精確排版的 HTML 產生器
def generate_html_line(text, font_size, position, skip_line, url=None):
    margin_left = position

    # 判斷有無超連結，決定是否右移
    has_url = pd.notna(url) and str(url).strip() != "" and str(url).strip().lower() != "nan"
    if not has_url:
        margin_left += 16
        content = f"<span>{text}</span>"
    else:
        clean_text = text.replace(str(url), "").strip()
        content = f'<span style="color: #000;">{clean_text}</span> &nbsp;&nbsp; <a href="{url}" 
        target="_blank" style="color: #1a0dab; text-decoration: underline; 
             font-weight: bold;">{url}</a>'

    bottom_gap = "0.10em" if skip_line >= 2 else "0.05em"
    line_hgt = "1.0" if skip_line >= 2 else "0.4"

    html = f"""
    <div style="font-size: {font_size}px; margin-left: {margin_left}px; 
         margin-bottom: {bottom_gap}; 
         line-height:{line_hgt}; font-family: sans-serif; white-space: pre-wrap;">
        {content}
    </div>
    """
    return html

# 5. 使用 Streamlit Session State 控制選單切換狀態
if "current_page" not in st.session_state:
    st.session_state.current_page = "MAIN"

# --- 畫面渲染開始 ---

# 顯示置中大標題
st.markdown(f'<div style="font-size: 28px; font-weight: bold; text-align: center; 
   margin-bottom: 30px; font-family: sans-serif;">{menu_title}</div>', unsafe_allow_html=True)

# 狀態一：顯示主選單
if st.session_state.current_page == "MAIN":
    # 篩選 GROUP == "MENU"
    menu_df = df[df['GROUP'].astype(str).str.strip() == 'MENU']

    # 建立主選單按鈕
    for _, row in menu_df.iterrows():
        key = str(row['KEY']).strip()
        desc = str(row['Option Description']).strip()
        position = int(row['position'])
        
        # 建立一個左邊縮排的區塊來放按鈕
        col_space, col_btn = st.columns([position if position > 0 else 1, 100])
        with col_btn:
            # 使用 streamlit 按鈕，點擊後更新狀態並重新整理網頁
            if st.button(f"{key} : {desc}", key=f"btn_{key}"):
                st.session_state.current_page = key
                st.rerun()

# 狀態二：顯示子選單
else:
    group_key = st.session_state.current_page
    
    # 返回主選單按鈕區塊
    col_space, col_back = st.columns([50, 100])
    with col_back:
        if st.button("⬅️ 返回主選單"):
            st.session_state.current_page = "MAIN"
            st.rerun()
            
    st.write("---") # 分隔線

    # 篩選對應的 GROUP 資料
    sub_df = df[df['GROUP'].astype(str).str.strip() == group_key]

    html_content = ""
    for _, row in sub_df.iterrows():
        desc = str(row['Option Description']).strip()
        font_size = int(row['Font size (px)'])
        position = int(row['position'])
        skip_line = int(row['SKIP LINE'])

        # 檢查有無超連結
        url = None
        if 'hyperlink' in df.columns and not pd.isna(row['hyperlink']):
            url_str = str(row['hyperlink']).strip()
            if url_str != "" and url_str.lower() != "nan":
                url = url_str

        html_content += generate_html_line(desc, font_size, position, skip_line, url)

    # 將精確排版的 HTML 渲染到網頁上
    st.markdown(html_content, unsafe_allow_html=True)

