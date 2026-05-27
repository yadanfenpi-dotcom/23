from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd


@dataclass(frozen=True)
class ReportData:
    """日报模板需要的全部结构化数据。"""

    report_date: date
    used_fallback_date: bool
    inquiry_count: int
    country_counts: dict[str, int]
    top_products: list[dict[str, int | str]]
    high_priority: list[dict[str, str]]


def analyze_inquiries(df: pd.DataFrame, today: date | None = None) -> ReportData:
    """按昨天优先、最新日期兜底的规则分析询盘数据。"""

    current_date = today or date.today()
    yesterday = current_date - timedelta(days=1)
    df = df.copy()
    df["day"] = df["date"].dt.date

    available_days = sorted(df["day"].dropna().unique())
    if yesterday in available_days:
        report_date = yesterday
        used_fallback_date = False
    else:
        report_date = available_days[-1]
        used_fallback_date = True

    daily_df = df[df["day"] == report_date].copy()

    country_counts = daily_df["country"].value_counts().to_dict()
    top_products = [
        {"name": str(product), "count": int(count)}
        for product, count in daily_df["product"].value_counts().head(3).items()
    ]

    priority_mask = daily_df["subject"].str.contains(r"sample|urgent", case=False, na=False, regex=True)
    high_priority = [
        {
            "date": row["date"].strftime("%Y-%m-%d %H:%M"),
            "country": row["country"],
            "product": row["product"],
            "subject": row["subject"],
        }
        for _, row in daily_df[priority_mask].sort_values("date").iterrows()
    ]

    return ReportData(
        report_date=report_date,
        used_fallback_date=used_fallback_date,
        inquiry_count=int(len(daily_df)),
        country_counts={str(country): int(count) for country, count in country_counts.items()},
        top_products=top_products,
        high_priority=high_priority,
    )
