from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import COLUMN_ALIASES, ColumnAliases


class InquiryDataError(ValueError):
    """询盘数据无法解析时抛出的中文业务错误。"""


def find_latest_inquiry_file(input_dir: Path) -> Path:
    """读取指定文件夹中最新修改的 询盘_*.xlsx 文件。"""

    files = sorted(input_dir.glob("询盘_*.xlsx"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not files:
        raise InquiryDataError(f"未在目录中找到询盘 Excel 文件：{input_dir}，请放入 询盘_*.xlsx")
    return files[0]


def read_inquiries(excel_path: Path, aliases: ColumnAliases = COLUMN_ALIASES) -> pd.DataFrame:
    """读取 Excel，并统一转换为脚本内部使用的标准字段。"""

    try:
        raw = pd.read_excel(excel_path)
    except Exception as exc:  # noqa: BLE001 - 需要把底层异常包装成可读中文提示
        raise InquiryDataError(f"读取 Excel 失败：{excel_path}，原因：{exc}") from exc

    if raw.empty:
        raise InquiryDataError(f"Excel 文件没有数据：{excel_path}")

    mapping = {
        "date": _find_column(raw.columns, aliases.date, "日期/询盘时间"),
        "country": _find_column(raw.columns, aliases.country, "国家/地区"),
        "product": _find_column(raw.columns, aliases.product, "产品/产品名称"),
        "subject": _find_column(raw.columns, aliases.subject, "主题/询盘主题"),
    }

    df = raw.rename(columns={source: target for target, source in mapping.items()})[
        ["date", "country", "product", "subject"]
    ].copy()

    # 日期解析失败的行会变成 NaT，后续统一过滤并给出清晰错误。
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["country"] = df["country"].fillna("未知").astype(str).str.strip().replace("", "未知")
    df["product"] = df["product"].fillna("未填写产品").astype(str).str.strip().replace("", "未填写产品")
    df["subject"] = df["subject"].fillna("").astype(str).str.strip()

    df = df.dropna(subset=["date"])
    if df.empty:
        raise InquiryDataError("Excel 中没有可解析的询盘日期，请检查日期列格式。")

    return df


def _find_column(columns: pd.Index, aliases: tuple[str, ...], label: str) -> str:
    """按字段别名查找真实列名，大小写和首尾空格不敏感。"""

    normalized = {str(column).strip().casefold(): column for column in columns}
    for alias in aliases:
        matched = normalized.get(alias.casefold())
        if matched is not None:
            return matched
    available = "、".join(str(column) for column in columns)
    expected = "、".join(aliases)
    raise InquiryDataError(f"缺少必要字段：{label}。支持字段名：{expected}。当前文件字段：{available}")
