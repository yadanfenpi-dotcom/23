from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "inquiries"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports"
DEFAULT_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "report.html.j2"


@dataclass(frozen=True)
class ColumnAliases:
    """维护阿里国际站导出文件可能出现的字段名称。"""

    date: tuple[str, ...] = ("日期", "询盘时间", "创建时间", "Created Time", "Inquiry Date")
    country: tuple[str, ...] = ("国家", "国家/地区", "Country", "Region")
    product: tuple[str, ...] = ("产品", "产品名称", "Product", "Product Name")
    subject: tuple[str, ...] = ("主题", "询盘主题", "Subject", "Title")


COLUMN_ALIASES = ColumnAliases()
