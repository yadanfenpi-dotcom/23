from __future__ import annotations

import queue
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, X, Button, Frame, Label, Tk, filedialog, messagebox, scrolledtext

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INQUIRY_DIR = PROJECT_ROOT / "data" / "inquiries"
REPORT_DIR = PROJECT_ROOT / "reports"
SAMPLE_SCRIPT = PROJECT_ROOT / "scripts" / "generate_sample_data.py"
REPORT_SCRIPT = PROJECT_ROOT / "scripts" / "run_report.py"


class InquiryReportApp:
    """一个给日常运营使用的简易桌面窗口。"""

    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("阿里国际站询盘日报助手")
        self.root.geometry("760x520")
        self.root.minsize(680, 460)

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.running = False
        self.last_report_path: Path | None = self._find_latest_report()

        self.status_label = Label(self.root, text="准备就绪", anchor="w", padx=12, pady=8)
        self.status_label.pack(fill=X)

        self._build_buttons()
        self._build_log()
        self._append_log("欢迎使用询盘日报助手。")
        self._append_log(f"询盘目录：{INQUIRY_DIR}")
        self._append_log(f"日报目录：{REPORT_DIR}")
        self._poll_log_queue()

    def run(self) -> None:
        self.root.mainloop()

    def _build_buttons(self) -> None:
        toolbar = Frame(self.root, padx=10, pady=8)
        toolbar.pack(fill=X)

        buttons = [
            ("生成示例数据", self.generate_sample_data),
            ("生成日报", self.generate_report),
            ("打开最新日报", self.open_latest_report),
            ("打开询盘文件夹", lambda: self.open_folder(INQUIRY_DIR)),
            ("打开日报文件夹", lambda: self.open_folder(REPORT_DIR)),
            ("选择询盘文件", self.copy_selected_inquiry_hint),
        ]

        for index, (text, command) in enumerate(buttons):
            side = LEFT if index < 3 else RIGHT
            button = Button(toolbar, text=text, command=command, padx=10, pady=6)
            button.pack(side=side, padx=4)

    def _build_log(self) -> None:
        self.log_box = scrolledtext.ScrolledText(self.root, wrap="word", height=20)
        self.log_box.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.log_box.configure(state="disabled")

    def generate_sample_data(self) -> None:
        self._run_python_script("生成示例数据", SAMPLE_SCRIPT)

    def generate_report(self) -> None:
        self._run_python_script("生成日报", REPORT_SCRIPT)

    def open_latest_report(self) -> None:
        report = self._find_latest_report()
        if report is None:
            messagebox.showinfo("暂无日报", "还没有找到日报文件，请先点击“生成日报”。")
            return
        self.last_report_path = report
        webbrowser.open(report.resolve().as_uri())
        self._append_log(f"已打开日报：{report}")

    def open_folder(self, folder: Path) -> None:
        folder.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer", str(folder)])
        self._append_log(f"已打开文件夹：{folder}")

    def copy_selected_inquiry_hint(self) -> None:
        selected = filedialog.askopenfilename(
            title="选择询盘 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")],
            initialdir=INQUIRY_DIR,
        )
        if not selected:
            return
        messagebox.showinfo(
            "操作提示",
            "请把选中的 Excel 文件复制到询盘目录，并确保文件名类似：询盘_2026-05-26.xlsx。",
        )
        self._append_log(f"你选择了文件：{selected}")

    def _run_python_script(self, task_name: str, script_path: Path) -> None:
        if self.running:
            messagebox.showinfo("任务运行中", "当前已有任务在运行，请稍等。")
            return

        self.running = True
        self.status_label.configure(text=f"{task_name}中...")
        self._append_log(f"开始：{task_name}")

        thread = threading.Thread(target=self._run_script_worker, args=(task_name, script_path), daemon=True)
        thread.start()

    def _run_script_worker(self, task_name: str, script_path: Path) -> None:
        try:
            process = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=PROJECT_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if process.stdout:
                self.log_queue.put(process.stdout.strip())
            if process.returncode == 0:
                self.last_report_path = self._find_latest_report()
                self.log_queue.put(f"完成：{task_name}")
                self.log_queue.put("__STATUS__准备就绪")
            else:
                self.log_queue.put(f"失败：{task_name}，退出码 {process.returncode}")
                self.log_queue.put("__STATUS__任务失败")
        except Exception as exc:  # noqa: BLE001 - 桌面窗口需要展示任何异常
            self.log_queue.put(f"异常：{exc}")
            self.log_queue.put("__STATUS__任务异常")
        finally:
            self.log_queue.put("__RUNNING__0")

    def _poll_log_queue(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break

            if message.startswith("__STATUS__"):
                self.status_label.configure(text=message.replace("__STATUS__", "", 1))
            elif message == "__RUNNING__0":
                self.running = False
            else:
                self._append_log(message)

        self.root.after(120, self._poll_log_queue)

    def _append_log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert(END, f"{message}\n")
        self.log_box.see(END)
        self.log_box.configure(state="disabled")

    @staticmethod
    def _find_latest_report() -> Path | None:
        reports = sorted(REPORT_DIR.glob("日报_*.html"), key=lambda path: path.stat().st_mtime, reverse=True)
        return reports[0] if reports else None


def main() -> None:
    app = InquiryReportApp()
    app.run()


if __name__ == "__main__":
    main()
