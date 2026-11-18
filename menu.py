import os
import base64
import subprocess
import urllib.parse
from datetime import datetime, timezone, timedelta
import streamlit as st
import pandas as pd

# ==========================================
# 0. 定義讀取 reference.txt 與 Git 時間的函式
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
        except Exception:
            pass
    return res

@st.cache_data(ttl=600)
def get_github_commit_time(filepath):
    """取得檔案最後一次推送至 GitHub (Git Commit) 的台灣時間"""
    if not os.path.exists(filepath):
        return ""
    try:
        cmd = ["git", "log", "-1", "--format=%ct", "--", filepath]
        timestamp_str = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if timestamp_str:
            tw_tz = timezone(timedelta(hours=8))
            dt = datetime.fromtimestamp(int(timestamp_str), tz=tw_tz)
            return dt.strftime("%Y/%m/%d %H:%M")
    except Exception:
        pass
    
    try:
        mtime = os.path.getmtime(filepath)
        tw_tz = timezone(timedelta(hours=8))
        dt = datetime.fromtimestamp(mtime, tz=tw_tz)
        return dt.strftime("%Y/%m/%d %H:%M")
    except Exception:
        return ""

# 1. 設定頁面
st.set_page_config(page_title="選股功能主選單", layout="centered")
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 100

zoom_col1, zoom_col2, zoom_col3 = st.columns(3)
with zoom_col1:
    if st.button("➕ 畫面放大", use_container_width=True):
        st.session_state.zoom_level = min(st.session_state.zoom_level + 15, 200)
        st.rerun()
with zoom_col2:
    if st.button("➖ 畫面縮小", use_container_width=True):
        st.session_state.zoom_level = max(st.session_state.zoom_level - 15, 70)
        st.rerun()
with zoom_col3:
    if st.button("🔄 恢復預設", use_container_width=True):
        st.session_state.zoom_level = 100
        st.rerun()

st.markdown(f"""
    <style>
    .block-container, div[data-testid="stVerticalBlock"] {{
        zoom: {st.session_state.zoom_level}%;
        -moz-transform: scale({st.session_state.zoom_level / 100});
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

# 3. 統一攔截網址列的影片或 PDF 參數（支援中文檔名解碼與自動定位所屬群組）
query_params = st.query_params
if "play_video" in query_params:
    video_name = urllib.parse.unquote(str(query_params["play_video"]))
    st.session_state.active_video = video_name
    st.session_state.active_pdf = None
    if 'current_page' not in st.session_state or st.session_state.current_page == 'Main':
        if 'last_valid_group' in st.session_state and st.session_state.last_valid_group:
            st.session_state.current_page = st.session_state.last_valid_group
        else:
            st.session_state.current_page = 'OP'
            st.session_state.last_valid_group = 'OP'

elif "view_pdf" in query_params:
    pdf_name = urllib.parse.unquote(str(query_params["view_pdf"]))
    st.session_state.active_pdf = pdf_name
    st.session_state.active_video = None
    if 'current_page' not in st.session_state or st.session_state.current_page == 'Main':
        df_tmp = st.session_state.df
        matched = df_tmp[df_tmp["OPTION DESCRIPTION"].astype(str).str.strip() == pdf_name]
        if not matched.empty:
            found_grp = str(matched.iloc["GROUP"]).strip()
            st.session_state.current_page = found_grp
            st.session_state.last_valid_group = found_grp
        elif 'last_valid_group' in st.session_state and st.session_state.last_valid_group:
            st.session_state.current_page = st.session_state.last_valid_group
        else:
            st.session_state.current_page = 'X'
            st.session_state.last_valid_group = 'X'
else:
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Main'

# ----------------- 畫面渲染開始 -----------------

# (A) & (B) 主選單畫面
if st.session_state.current_page == 'Main':
    info_dict = read_reference_title()
    
    title_html = "<div style='text-align: center; font-family: sans-serif;'>"
    title_html += f"<div style='font-size: 24px; font-weight: bold; color: #333; margin-top: 10px; margin-bottom: 5px;'>{info_dict['title']}</div>"
    
    if info_dict.get("hint1"):
        title_html += f"<div style='font-size: 16px; font-weight: bold; color: #FF6B6B; margin-top: 4px; margin-bottom: 4px;'>{info_dict['hint1']}</div>"
    if info_dict.get("hint2"):
        title_html += f"<div style='font-size: 16px; font-weight: bold; color: #FF6B6B; margin-top: 4px; margin-bottom: 4px;'>{info_dict['hint2']}</div>"
    if info_dict.get("hint3"):
        title_html += f"<div style='font-size: 16px; font-weight: bold; color: #FF6B6B; margin-top: 4px; margin-bottom: 4px;'>{info_dict['hint3']}</div>"
    title_html += "</div>"
    
    st.markdown(title_html, unsafe_allow_html=True)
    st.write("---")

    df = st.session_state.df
    menu_df = df[df["GROUP"].astype(str).str.strip() == "MENU"]

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
    st.session_state.last_valid_group = group_key
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 返回主選單"):
            st.session_state.active_video = None
            st.session_state.active_pdf = None
            st.query_params.clear()
            st.session_state.current_page = 'Main'
            st.rerun()
    with col2:
        if st.button("❌ 關閉應用", type="primary"):
            st.warning("請直接關閉瀏覽器分頁。")

    st.write("---")

    sub_df = df[df["GROUP"].astype(str).str.strip() == group_key]
    
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
            encoded_desc = urllib.parse.quote(desc)
            if url_lower.endswith('.mp4'):
                html_content += f"<span style='{line_style}'><a href='?play_video={encoded_desc}' target='_self' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>{desc}</a></span>"
            elif url_lower.endswith('.pdf') and not url_lower.startswith('http'):
                commit_time = get_github_commit_time(desc)
                time_badge = f"<span style='color: #d93025; font-size: 15px; margin-left: 14px; font-weight: bold;'>({commit_time})</span>" if commit_time else ""
                html_content += f"<span style='{line_style}'><a href='?view_pdf={encoded_desc}' target='_self' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>📄 {desc}</a>{time_badge}</span>"
            else:
                html_content += f"<span style='{line_style}'><a href='{desc}' target='_blank' style='color: #1a73e8; text-decoration: underline; font-weight: bold;'>{desc}</a></span>"
        else:
            html_content += f"<span style='{line_style}; color: #008000;'>{desc}</span>"
            
    html_content += "</div>"
    st.markdown(html_content, unsafe_allow_html=True)

    # 影片播放器區塊
    # 影片播放器區塊
    if 'active_video' in st.session_state and st.session_state.active_video:
        st.write("---")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.subheader("影片線上播放")
        with v_col2:
            if st.button("關閉影片", use_container_width=True):
                st.session_state.active_video = None
                st.query_params.clear()
                st.rerun()
        st.video(st.session_state.active_video, autoplay=True)

    # 本地 PDF 檢視器區塊
    if 'active_pdf' in st.session_state and st.session_state.active_pdf:
        pdf_filename = st.session_state.active_pdf
        st.write("---")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            st.subheader(f"檢視：{pdf_filename}")
        with p_col2:
            if st.button("關閉 PDF", use_container_width=True):
                st.session_state.active_pdf = None
                st.query_params.clear()
                st.rerun()
                
        if os.path.exists(pdf_filename):
            with open(pdf_filename, "rb") as f:
                pdf_bytes = f.read()
            
            st.download_button(
                label="下載此 PDF 檔案",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf"
            )
            
            try:
                import fitz
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                st.caption(f"共 {len(doc)} 頁（可直接往下滑動瀏覽）")
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                    st.image(pix.tobytes("png"), use_container_width=True)
            except Exception as e:
                st.warning(f"無法直接預覽畫面，請點擊上方下載按鈕檢視。（原因：{e}）")
        else:
            st.error(f"找不到檔案：{pdf_filename}")


