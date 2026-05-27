from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402


def create_country_pie_chart(country_counts: dict[str, int], output_path: Path) -> Path | None:
    """生成国家/地区分布饼图；没有数据时返回 None。"""

    if not country_counts:
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _configure_chinese_font()

    labels = list(country_counts.keys())
    sizes = list(country_counts.values())
    colors = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2", "#4b5563"]

    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=150)
    ax.pie(
        sizes,
        labels=labels,
        autopct=lambda percent: f"{percent:.0f}%" if percent >= 5 else "",
        startangle=90,
        colors=colors[: len(labels)],
        textprops={"fontsize": 9, "color": "#111827"},
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.axis("equal")
    ax.set_title("国家/地区分布", fontsize=13, pad=12, color="#111827")
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


def _configure_chinese_font() -> None:
    """尽量选择系统中的中文字体，避免图表中文乱码。"""

    preferred_fonts = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "Arial Unicode MS",
    ]
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for font in preferred_fonts:
        if font in installed:
            plt.rcParams["font.sans-serif"] = [font]
            break
    plt.rcParams["axes.unicode_minus"] = False
