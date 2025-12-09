
import threading
import time
import tkinter as tk
from tkinter import messagebox
from agent import SystemMonitor  

BG_MAIN = "#e5fff3"
BG_SIDEBAR = "#b9f4d9"
BG_CARD = "#ffffff"
ACCENT = "#1f6c4f"
BUTTON_BG = "#8ef1c0"
BUTTON_BG_DISABLED = "#cdeedc"
BUTTON_TEXT = "#0f4f5b"
STATUS_OK = "#1e9f47"
STATUS_ERROR = "#d11f3f"
STATUS_NEUTRAL = "#777777"
STATUS_RUNNING = "#1f6c4f"


class AgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SysMonitor Agent")
        self.root.configure(bg=BG_MAIN)
        self.root.geometry("520x260")
        self.root.resizable(False, False)

        self.monitor = SystemMonitor()
        self.running = False
        self.thread = None

        sidebar = tk.Frame(
            root,
            bg=BG_SIDEBAR,
            width=110
        )
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        title_label = tk.Label(
            sidebar,
            text="SysMonitor\nAgent",
            bg=BG_SIDEBAR,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold"),
            justify=tk.CENTER
        )
        title_label.place(relx=0.5, rely=0.2, anchor="center")

        hint_label = tk.Label(
            sidebar,
            text="Установите\nна рабочую\nстанцию\nи запустите\nмониторинг.",
            bg=BG_SIDEBAR,
            fg="#2f5d46",
            font=("Segoe UI", 9),
            justify=tk.CENTER
        )
        hint_label.place(relx=0.5, rely=0.65, anchor="center")

        card = tk.Frame(
            root,
            bg=BG_CARD,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d0e6d9"
        )
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=16)

        header = tk.Label(
            card,
            text="Клиент мониторинга",
            bg=BG_CARD,
            fg=ACCENT,
            font=("Segoe UI", 12, "bold")
        )
        header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(4, 8))

        lbl_server = tk.Label(
            card,
            text="Адрес сервера:",
            bg=BG_CARD,
            fg="#333333",
            font=("Segoe UI", 10)
        )
        lbl_server.grid(row=1, column=0, sticky="w", padx=(4, 4), pady=(2, 2))

        self.server_entry = tk.Entry(
            card,
            width=34,
            font=("Segoe UI", 10)
        )
        self.server_entry.grid(row=1, column=1, columnspan=2, sticky="we", padx=(4, 8), pady=(2, 2))
        
        # подставить IP сервера в сети
        self.server_entry.insert(0, "http://127.0.0.1:5000")

        lbl_interval = tk.Label(
            card,
            text="Интервал (сек):",
            bg=BG_CARD,
            fg="#333333",
            font=("Segoe UI", 10)
        )
        lbl_interval.grid(row=2, column=0, sticky="w", padx=(4, 4), pady=(6, 2))

        self.interval_entry = tk.Entry(
            card,
            width=10,
            font=("Segoe UI", 10)
        )
        self.interval_entry.grid(row=2, column=1, sticky="w", padx=(4, 4), pady=(6, 2))
        self.interval_entry.insert(0, "5")

        self.status_dot = tk.Label(
            card,
            text="●",
            bg=BG_CARD,
            fg=STATUS_NEUTRAL,
            font=("Segoe UI", 12)
        )
        self.status_dot.grid(row=3, column=0, sticky="w", padx=(4, 0), pady=(10, 2))

        self.status_label = tk.Label(
            card,
            text="Статус: остановлен",
            bg=BG_CARD,
            fg=STATUS_NEUTRAL,
            font=("Segoe UI", 10)
        )
        self.status_label.grid(row=3, column=1, columnspan=2, sticky="w", padx=(2, 4), pady=(10, 2))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(14, 4), sticky="e")

        self.start_btn = tk.Button(
            btn_frame,
            text="Запустить мониторинг",
            command=self.start,
            bg=BUTTON_BG,
            fg=BUTTON_TEXT,
            activebackground="#77c8a5",
            activeforeground=BUTTON_TEXT,
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=4,
            cursor="hand2"
        )
        self.start_btn.grid(row=0, column=0, padx=4)

        self.stop_btn = tk.Button(
            btn_frame,
            text="Остановить",
            command=self.stop,
            bg=BUTTON_BG_DISABLED,
            fg="#666666",
            activebackground=BUTTON_BG_DISABLED,
            activeforeground="#666666",
            relief=tk.FLAT,
            font=("Segoe UI", 10),
            padx=12,
            pady=4,
            state=tk.DISABLED,
            cursor="arrow"
        )
        self.stop_btn.grid(row=0, column=1, padx=4)

        card.columnconfigure(1, weight=1)

    def loop(self, server_url, interval):
        while self.running:
            ok = self.monitor.send_metrics(server_url)
            if ok:
                self.set_status("Статус: данные отправлены", STATUS_OK)
            else:
                self.set_status("Статус: ошибка отправки", STATUS_ERROR)
            time.sleep(interval)

    def set_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.status_dot.config(fg=color)

    def start(self):
        if self.running:
            return

        server_url = self.server_entry.get().strip()
        if not server_url:
            messagebox.showerror("Ошибка", "Введите адрес сервера")
            return

        try:
            interval = int(self.interval_entry.get().strip())
            if interval <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Ошибка", "Интервал должен быть положительным числом")
            return

        self.running = True
        self.start_btn.config(
            state=tk.DISABLED,
            bg=BUTTON_BG_DISABLED,
            fg="#666666",
            cursor="arrow"
        )
        self.stop_btn.config(
            state=tk.NORMAL,
            bg=BUTTON_BG,
            fg=BUTTON_TEXT,
            cursor="hand2"
        )
        self.set_status("Статус: запущен", STATUS_RUNNING)

        self.thread = threading.Thread(
            target=self.loop,
            args=(server_url, interval),
            daemon=True
        )
        self.thread.start()

    def stop(self):
        if not self.running:
            return

        self.running = False
        self.start_btn.config(
            state=tk.NORMAL,
            bg=BUTTON_BG,
            fg=BUTTON_TEXT,
            cursor="hand2"
        )
        self.stop_btn.config(
            state=tk.DISABLED,
            bg=BUTTON_BG_DISABLED,
            fg="#666666",
            cursor="arrow"
        )
        self.set_status("Статус: остановлен", STATUS_NEUTRAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = AgentApp(root)
    root.mainloop()
