import os
import sys
import webbrowser
import tkinter as tk
from tkinter import font
import pandas as pd

def read_reference_title():
    """讀取 reference.txt 中的 MENU_TITLE"""
    title = "歡迎光臨股票選單系統"  # 預設標題
    if os.path.exists("reference.txt"):
        try:
            with open("reference.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MENU_TITLE:"):
                        title = line.replace("MENU_TITLE:", "").strip()
                        break
        except Exception as e:
            print(f"讀取 reference.txt 失敗: {e}")
    return title

def open_url(url):
    """用瀏覽器打開超連結"""
    if url and (url.startswith("http://") or url.startswith("https://")):
        webbrowser.open(url)

class MenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("選股功能主選單")
        self.root.geometry("1000x700")
        
        # 讀取 Excel 資料
        try:
            self.df = pd.read_excel("data.xlsx")
            # 去除欄位名稱前後的空白
            self.df.columns = self.df.columns.str.strip()
        except Exception as e:
            lbl = tk.Label(root, text=f"無法讀取 data.xlsx: {e}", fg="red", font=("Microsoft JhengHei", 16))
            lbl.pack(pady=20)
            return

        # 顯示主畫面
        self.show_main_menu()

    def clear_window(self):
        """清除視窗內所有元件"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        """(A) & (B) 呈現主選單畫面"""
        self.clear_window()
        
        # 讀取並顯示 reference.txt 的歡迎詞
        welcome_title = read_reference_title()
        title_label = tk.Label(
            self.root, 
            text=welcome_title, 
            font=("Microsoft JhengHei", 18, "bold"), 
            wraplength=900, 
            justify="center"
        )
        title_label.pack(pady=25)

        # 篩選 GROUP == "MENU" 的資料
        menu_df = self.df[self.df["GROUP"].astype(str).str.strip() == "MENU"]

        # 建立選單按鈕容器
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(fill="both", expand=True, px=50)

        for _, row in menu_df.iterrows():
            key = str(row["KEY"]).strip()
            desc = str(row["Option Description"]).strip()
            
            # 讀取排版參數（若為空則給予預設值）
            f_size = int(row["Font size (px)"]) if pd.notna(row["Font size (px)"]) else 24
            pos = int(row["position"]) if pd.notna(row["position"]) else 150
            skip_line = int(row["SKIP LINE"]) if pd.notna(row["SKIP LINE"]) else 2

            # 設定按鈕顯示文字，例如 "A : 提問 GOOGLE 或 其他"
            button_text = f"{key} :  {desc}"
            
            # 建立按鈕，點擊時進入子選單，並傳入對應的 KEY (如 'A', 'B')
            btn = tk.Button(
                menu_frame, 
                text=button_text, 
                font=("Microsoft JhengHei", int(f_size * 0.75)),  # 轉換為 tkinter font size
                anchor="w",  # 文字靠左
                justify="left",
                command=lambda k=key: self.show_sub_menu(k)
            )
            # 使用 position 作為左邊的留白 (padx)，並依據 SKIP LINE 調整上下間距 (pady)
            btn.pack(fill="x", padx=pos, pady=skip_line * 6, anchor="w")

    def show_sub_menu(self, group_key):
        """(C) 呈現子選單畫面 (依據所選的 GROUP)"""
        self.clear_window()

        # 建立頂部導航與關閉按鈕區域
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=20, pady=10)

        # 回主選單按鈕
        btn_back = tk.Button(
            top_frame, 
            text="返回主選單", 
            font=("Microsoft JhengHei", 12), 
            command=self.show_main_menu
        )
        btn_back.pack(side="left")

        # 關閉視窗按鈕
        btn_close = tk.Button(
            top_frame, 
            text="關閉視窗", 
            font=("Microsoft JhengHei", 12), 
            bg="#ff4d4d", 
            fg="white", 
            command=self.root.quit
        )
        btn_close.pack(side="right")

        # 建立滾動區域以防內容過長
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # 篩選對應 GROUP 的資料 (例如 GROUP == "B")
        sub_df = self.df[self.df["GROUP"].astype(str).str.strip() == group_key]

        for _, row in sub_df.iterrows():
            desc = str(row["Option Description"]).strip()
            f_size = int(row["Font size (px)"]) if pd.notna(row["Font size (px)"]) else 16
            pos = int(row["position"]) if pd.notna(row["position"]) else 50
            skip_line = int(row["SKIP LINE"]) if pd.notna(row["SKIP LINE"]) else 1
            is_hyperlink = str(row["hyperlink"]).strip().upper() == "Y"

            # 建立文字標籤或超連結
            if is_hyperlink:
                # 如果是超連結，文字改為藍色、加底線，並綁定點擊事件
                lbl = tk.Label(
                    scroll_frame, 
                    text=desc, 
                    font=("Microsoft JhengHei", int(f_size * 0.75), "underline"), 
                    fg="blue", 
                    cursor="hand2",
                    anchor="w",
                    justify="left"
                )
                lbl.bind("<Button-1>", lambda event, url=desc: open_url(url))
            else:
                lbl = tk.Label(
                    scroll_frame, 
                    text=desc, 
                    font=("Microsoft JhengHei", int(f_size * 0.75)), 
                    anchor="w",
                    justify="left"
                )

            # 依據 position 欄位決定左邊縮排，依據 SKIP LINE 決定下方間距
            lbl.pack(fill="x", padx=pos, pady=(0, skip_line * 8), anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuApp(root)
    root.mainloop()


