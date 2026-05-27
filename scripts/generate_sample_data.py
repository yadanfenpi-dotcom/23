from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from inquiry_daily_report.config import DEFAULT_INPUT_DIR  # noqa: E402


def main() -> None:
    """生成固定日期的模拟询盘 Excel，方便本地和 GitHub Actions 测试。"""

    DEFAULT_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DEFAULT_INPUT_DIR / "询盘_2026-05-26.xlsx"

    rows = [
        ["2026-05-26 08:12", "United States", "Solar Garden Light", "Need sample for retail test"],
        ["2026-05-26 09:40", "Germany", "LED Street Light", "Price list request"],
        ["2026-05-26 10:05", "Brazil", "Solar Garden Light", "Urgent order for distributor"],
        ["2026-05-26 11:32", "India", "Portable Power Station", "Need catalog and MOQ"],
        ["2026-05-26 13:18", "United States", "Solar Garden Light", "Sample shipping cost"],
        ["2026-05-26 15:45", "France", "LED Street Light", "Project quotation"],
        ["2026-05-26 16:20", "Brazil", "Camping Lantern", "urgent delivery date"],
        ["2026-05-25 10:00", "Canada", "Camping Lantern", "Older inquiry for comparison"],
    ]

    df = pd.DataFrame(rows, columns=["Inquiry Date", "Country", "Product Name", "Subject"])
    df.to_excel(output_path, index=False)
    print(f"已生成模拟询盘数据：{output_path}")


if __name__ == "__main__":
    main()
