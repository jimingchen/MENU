import os
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML

# 1. 設定檔案路徑（修正：改為 Colab 絕對路徑，確保讀取成功）
EXCEL_PATH = "data.xlsx"       # 如果您的 Excel 檔名不同請自行修改
TXT_PATH = "reference.txt"     # 強制指定 Colab 根目錄路徑

# 2. 完全動態讀取 reference.txt，絕不硬編碼標題內容
menu_title = ""
if os.path.exists(TXT_PATH):
    try:
        with open(TXT_PATH, "r", encoding="utf-8-sig") as f:
            for line in f:
                if "MENU_TITLE:" in line:
                    # 使用 split 分割並極限去除兩端空白，完整抓取後方任何中英文文字
                    menu_title = line.split("MENU_TITLE:", 1)[1].strip()
                    break
    except Exception as e:
        menu_title = f"[讀取標題出錯: {str(e)}]"
else:
    menu_title = "[找不到 reference.txt 檔案，請確認路徑]"

# 3. 讀取 Excel 資料
df = pd.read_excel(EXCEL_PATH)
df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

# 4. 定義精確排版的 HTML 產生器
def generate_html_line(text, font_size, position, skip_line, url=None):
    # 基本的左邊距
    margin_left = position

    # 判斷有無超連結，決定是否右移 (右移 16px，約 2 個英文字元寬)
    has_url = pd.notna(url) and str(url).strip() != "" and str(url).strip().lower() != "nan"
    if not has_url:
        margin_left += 16
        content = f"<span>{text}</span>"
    else:
        # 有超連結，呈現文字與超連結
        clean_text = text.replace(str(url), "").strip()
        content = f'<span style="color: #000;">{clean_text}</span> &nbsp;&nbsp; <a href="{url}" target="_blank" style="color: #1a0dab; text-decoration: underline; font-weight: bold;">{url}</a>'

    # skip_line == 1 時極度緊鄰 (0.05em)；skip_line == 2 時微幅跳行 (0.35em)
    bottom_gap = "0.10em" if skip_line >= 2 else "0.05em"
    line_hgt = "1" if skip_line >= 2 else "0.5"

    html = f"""
    <div style="font-size: {font_size}px; margin-left: {margin_left}px; margin-bottom: {bottom_gap}; line-height:{line_hgt}; font-family: sans-serif; white-space: pre-wrap;">
        {content}
    </div>
    """
    return html

# 5. 建立互動元件與主程式
output_area = widgets.Output()

def show_main_menu():
    with output_area:
        output_area.clear_output()

        # 顯示從 txt 檔案讀取到的標題
        display(HTML(f'<div style="font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 20px; font-family: sans-serif;">{menu_title}</div>'))

        # 篩選 GROUP == "MENU"
        menu_df = df[df['GROUP'].astype(str).str.strip() == 'MENU']

        # 建立主選單按鈕
        for _, row in menu_df.iterrows():
            key = str(row['KEY']).strip()
            desc = str(row['Option Description']).strip()
            font_size = int(row['Font size (px)'])
            position = int(row['position'])

            btn = widgets.Button(
                description=f"{key} : {desc}",
                layout=widgets.Layout(width='auto', max_width='90%', margin=f'6px 0px 6px {position}px')
            )
            btn.style.font_size = f"{font_size}px"

            def make_click_callback(target_group):
                return lambda b: show_sub_menu(target_group)

            btn.on_click(make_click_callback(key))
            display(btn)

def show_sub_menu(group_key):
    with output_area:
        output_area.clear_output()

        # 返回主選單按鈕
        back_btn = widgets.Button(description="⬅️ 返回主選單", layout=widgets.Layout(width='150px', margin='10px 0px 15px 50px'))
        back_btn.on_click(lambda b: show_main_menu())
        display(back_btn)

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

        display(HTML(html_content))

# 啟動程式顯示畫面
display(output_area)
show_main_menu()
