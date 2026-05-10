"""
Bootstrap a multi-site training csv from existing test.csv (text1/text2).

Why this script:
- Current project may have no DB data yet.
- We still need a minimal site-specific dataset to warm up LoRA.

Important:
- This is synthetic style adaptation (TK/Amazon/Shopee) from the same source text.
- It is suitable for cold-start/warmup, not final production quality.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

import pandas as pd


def normalize_text(text: str) -> str:
    if text is None:
        return ""
    return str(text).strip()


def split_keywords(text1: str, top_k: int = 6) -> List[str]:
    text = normalize_text(text1)
    if not text:
        return []
    text = re.sub(r"[;；|/]+", "，", text)
    parts = [p.strip() for p in re.split(r"[，,]", text) if p.strip()]
    dedup = []
    seen = set()
    for p in parts:
        if p not in seen:
            dedup.append(p)
            seen.add(p)
        if len(dedup) >= top_k:
            break
    return dedup


def first_title_word(keywords: List[str]) -> str:
    if not keywords:
        return "商品"
    return keywords[0]


def truncate_text(text: str, max_len: int = 180) -> str:
    raw = normalize_text(text)
    if len(raw) <= max_len:
        return raw
    return raw[: max_len - 1].rstrip("，,。 ") + "。"


def render_tiktokshop_desc(keywords: List[str], base_desc: str) -> str:
    kw = "、".join(keywords[:4]) if keywords else "实用、耐用"
    base = truncate_text(base_desc, max_len=150)
    return f"【一眼看懂卖点】主打{kw}。{base} 适合日常高频使用，上手快、体验直观。"


def render_amazon_desc(keywords: List[str], base_desc: str) -> str:
    kw = " / ".join(keywords[:5]) if keywords else "core features"
    base = truncate_text(base_desc, max_len=180)
    return f"【Core Features】{kw}。{base} 文案强调功能、材质与使用价值，便于快速决策。"


def render_shopee_desc(keywords: List[str], base_desc: str) -> str:
    kw = "、".join(keywords[:4]) if keywords else "好用、实用"
    base = truncate_text(base_desc, max_len=140)
    return f"【实用重点】{kw}。{base} 适合家用/宿舍等日常场景，信息简洁直接。"


def render_title(site: str, keywords: List[str]) -> str:
    core = " ".join(keywords[:2]).strip() or "商品"
    if site == "tiktokshop":
        return f"{core}｜场景实用款"
    if site == "amazon":
        return f"{core} - 功能清晰款"
    return f"{core}｜高性价比家用款"


def build_target_attributes(site: str, keywords: List[str]) -> dict:
    return {
        "site_style": site,
        "selling_points": keywords[:6],
        "copy_intent": (
            "short_scene_driven"
            if site == "tiktokshop"
            else "feature_rational"
            if site == "amazon"
            else "concise_value_driven"
        ),
    }


def convert_row(idx: int, row: pd.Series, site: str) -> dict:
    text1 = normalize_text(row.get("text1", ""))
    text2 = normalize_text(row.get("text2", ""))
    keywords = split_keywords(text1)
    source_title = first_title_word(keywords)

    if site == "tiktokshop":
        target_desc = render_tiktokshop_desc(keywords, text2)
    elif site == "amazon":
        target_desc = render_amazon_desc(keywords, text2)
    else:
        target_desc = render_shopee_desc(keywords, text2)

    return {
        "site": site,
        "des_lang_type": "中文",
        "product_src_id": idx,
        "product_url": "",
        "spu_image_url": "",
        "source_title": source_title,
        "category_name": "",
        "selling_points": text1,
        "source_attributes": json.dumps({}, ensure_ascii=False),
        "target_title": render_title(site, keywords),
        "target_desc": target_desc,
        "target_attributes_json": json.dumps(build_target_attributes(site, keywords), ensure_ascii=False),
    }


def main() -> None:
    base = Path(__file__).resolve().parent
    src = base / "product_description_generation" / "test.csv"
    out = base / "product_description_generation" / "test_multisite_bootstrap.csv"

    df = pd.read_csv(src).dropna(subset=["text1", "text2"]).copy()
    df["text1"] = df["text1"].astype(str).str.strip()
    df["text2"] = df["text2"].astype(str).str.strip()
    df = df[(df["text1"] != "") & (df["text2"] != "")].reset_index(drop=True)

    all_rows = []
    for idx, row in df.iterrows():
        sample_idx = idx + 1
        all_rows.append(convert_row(sample_idx, row, "tiktokshop"))
        all_rows.append(convert_row(sample_idx, row, "amazon"))
        all_rows.append(convert_row(sample_idx, row, "shopee"))

    out_df = pd.DataFrame(all_rows)
    out_df.to_csv(out, index=False, encoding="utf-8")

    summary = {
        "input": str(src),
        "output": str(out),
        "source_rows": int(len(df)),
        "output_rows": int(len(out_df)),
        "site_distribution": out_df["site"].value_counts().to_dict(),
        "columns": out_df.columns.tolist(),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
