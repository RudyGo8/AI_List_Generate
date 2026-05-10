"""
Prepare multi-site bundle SFT dataset for listing generation.

Output format is aligned with current service prompt:
- instruction
- input  (with site/locale control tags + json payload)
- output (strict json string with product_title/product_desc/attributes)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.model_selection import train_test_split


TASK_TAG = "bundle_json"
DEFAULT_INSTRUCTION = "你是跨境电商商品文案助手。请根据输入信息输出严格JSON。"

SITE_ALIASES = ("site", "platform", "marketplace")
LOCALE_ALIASES = ("locale", "language", "lang", "des_lang_type")
GROUP_KEY_ALIASES = (
    "product_src_id",



    "spu_id",
    "product_id",
    "item_id",
    "group_id",
)
PRODUCT_URL_ALIASES = ("product_url", "item_url", "url")
SPU_IMAGE_URL_ALIASES = ("spu_image_url", "main_image_url", "image_url")
CATEGORY_ALIASES = ("category_path", "category_name", "category")
SOURCE_TITLE_ALIASES = ("source_title", "product_title", "title")
SELLING_POINTS_ALIASES = ("selling_points", "highlights", "bullet_points", "text1")
SOURCE_ATTRS_ALIASES = ("source_attributes", "attributes")
TARGET_TITLE_ALIASES = ("target_title", "product_title_out", "gen_title")
TARGET_DESC_ALIASES = ("target_desc", "product_desc", "description", "text2")
TARGET_ATTRS_ALIASES = ("target_attributes_json", "attributes_out", "gen_attributes")


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    default_input = script_dir / "product_description_generation" / "test.csv"
    default_output_dir = script_dir / "sft_json"

    parser = argparse.ArgumentParser(
        description="Prepare multi-site bundle SFT json files for LLaMA-Factory."
    )
    parser.add_argument("--input", type=Path, default=default_input, help="Input csv/jsonl/parquet")
    parser.add_argument("--output-dir", type=Path, default=default_output_dir, help="Output folder")
    parser.add_argument(
        "--dataset-prefix",
        type=str,
        default="shop_multisite_bundle_sft",
        help="Output dataset file prefix",
    )
    parser.add_argument(
        "--dataset-info-name",
        type=str,
        default="llamafactory_dataset_info_multisite.json",
        help="LLaMA-Factory dataset_info filename",
    )
    parser.add_argument(
        "--instruction",
        type=str,
        default=DEFAULT_INSTRUCTION,
        help="SFT instruction text",
    )
    parser.add_argument(
        "--target-sites",
        type=str,
        default="",
        help="Comma-separated site names to keep. Empty keeps all sites.",
    )
    parser.add_argument(
        "--default-site",
        type=str,
        default="generic_cn",
        help="Fallback site when source data has no site column.",
    )
    parser.add_argument(
        "--default-locale",
        type=str,
        default="en_US",
        help="Fallback locale when source data has no locale column.",
    )
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def pick_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    for name in aliases:
        if name in df.columns:
            return name
    return None


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".jsonl":
        return pd.read_json(path, lines=True)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported input file type: {path}")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


def parse_json_like(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if pd.isna(value):
        return default

    text = str(value).strip()
    if not text:
        return default
    try:
        return json.loads(text)
    except Exception:
        return default


def short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def validate_ratios(train_ratio: float, val_ratio: float, test_ratio: float) -> None:
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-8:
        raise ValueError(
            f"train/val/test ratio must sum to 1.0, got {train_ratio}+{val_ratio}+{test_ratio}={total}"
        )
    if any(r <= 0 for r in (train_ratio, val_ratio, test_ratio)):
        raise ValueError("train/val/test ratio must all be > 0")


def split_groups(
    groups: list[str], train_ratio: float, val_ratio: float, test_ratio: float, seed: int
) -> tuple[set[str], set[str], set[str]]:
    if not groups:
        return set(), set(), set()

    if len(groups) < 3:
        random.Random(seed).shuffle(groups)
        if len(groups) == 1:
            return set(groups), set(), set()
        return {groups[0]}, {groups[1]}, set()

    train_groups, temp_groups = train_test_split(
        groups,
        test_size=(1 - train_ratio),
        random_state=seed,
        shuffle=True,
    )
    if not temp_groups:
        return set(train_groups), set(), set()

    relative_test = test_ratio / (val_ratio + test_ratio)
    if len(temp_groups) < 2:
        return set(train_groups), set(temp_groups), set()

    val_groups, test_groups = train_test_split(
        temp_groups,
        test_size=relative_test,
        random_state=seed,
        shuffle=True,
    )
    return set(train_groups), set(val_groups), set(test_groups)


def convert_row_to_record(row: pd.Series, instruction: str) -> dict[str, Any] | None:
    site = clean_text(row["site"])
    locale = clean_text(row["locale"])
    category_path = clean_text(row["category_path"])
    source_title = clean_text(row["source_title"])
    selling_points = clean_text(row["selling_points"])
    target_title = clean_text(row["target_title"])
    target_desc = clean_text(row["target_desc"])

    if not target_desc:
        return None
    if not target_title:
        if source_title:
            target_title = source_title
        else:
            first_point = selling_points.split("，", 1)[0].strip() if selling_points else ""
            target_title = first_point or "Generated Title"

    source_attributes = parse_json_like(row["source_attributes"], default={})
    target_attributes = parse_json_like(row["target_attributes_json"], default={})

    payload = {
        "category_path": category_path,
        "source_title": source_title,
        "selling_points": selling_points,
        "source_attributes": source_attributes,
    }
    output = {
        "product_title": target_title,
        "product_desc": target_desc,
        "attributes": target_attributes,
    }
    input_text = (
        f"<SITE={site}><LOCALE={locale}><TASK={TASK_TAG}>\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
    return {
        "instruction": instruction,
        "input": input_text,
        "output": json.dumps(output, ensure_ascii=False),
    }


def prepare_dataframe(df: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, dict[str, str]]:
    mapping: dict[str, str] = {}

    site_col = pick_column(df, SITE_ALIASES)
    locale_col = pick_column(df, LOCALE_ALIASES)
    group_col = pick_column(df, GROUP_KEY_ALIASES)
    product_url_col = pick_column(df, PRODUCT_URL_ALIASES)
    spu_image_url_col = pick_column(df, SPU_IMAGE_URL_ALIASES)
    category_col = pick_column(df, CATEGORY_ALIASES)
    source_title_col = pick_column(df, SOURCE_TITLE_ALIASES)
    selling_points_col = pick_column(df, SELLING_POINTS_ALIASES)
    source_attrs_col = pick_column(df, SOURCE_ATTRS_ALIASES)
    target_title_col = pick_column(df, TARGET_TITLE_ALIASES)
    target_desc_col = pick_column(df, TARGET_DESC_ALIASES)
    target_attrs_col = pick_column(df, TARGET_ATTRS_ALIASES)

    mapping["site"] = site_col or f"(default={args.default_site})"
    mapping["locale"] = locale_col or f"(default={args.default_locale})"
    mapping["group_key"] = (
        group_col
        or product_url_col
        or spu_image_url_col
        or "(fallback=row_index)"
    )
    mapping["product_url"] = product_url_col or "(not found)"
    mapping["spu_image_url"] = spu_image_url_col or "(not found)"
    mapping["category_path"] = category_col or "(default='')"
    mapping["source_title"] = source_title_col or "(default='')"
    mapping["selling_points"] = selling_points_col or "(default='')"
    mapping["source_attributes"] = source_attrs_col or "(default={})"
    mapping["target_title"] = target_title_col or "(fallback=source_title)"
    mapping["target_desc"] = target_desc_col or "(required)"
    mapping["target_attributes_json"] = target_attrs_col or "(default={})"

    normalized = pd.DataFrame(index=df.index)
    normalized["site"] = df[site_col].apply(clean_text) if site_col else args.default_site
    normalized["locale"] = df[locale_col].apply(clean_text) if locale_col else args.default_locale
    normalized["group_key"] = df[group_col].apply(clean_text) if group_col else ""
    normalized["product_url"] = df[product_url_col].apply(clean_text) if product_url_col else ""
    normalized["spu_image_url"] = (
        df[spu_image_url_col].apply(clean_text) if spu_image_url_col else ""
    )
    normalized["category_path"] = df[category_col].apply(clean_text) if category_col else ""
    normalized["source_title"] = df[source_title_col].apply(clean_text) if source_title_col else ""
    normalized["selling_points"] = (
        df[selling_points_col].apply(clean_text) if selling_points_col else ""
    )
    normalized["source_attributes"] = (
        df[source_attrs_col] if source_attrs_col else "{}"
    )
    normalized["target_title"] = df[target_title_col].apply(clean_text) if target_title_col else ""
    normalized["target_desc"] = df[target_desc_col].apply(clean_text) if target_desc_col else ""
    normalized["target_attributes_json"] = df[target_attrs_col] if target_attrs_col else "{}"

    normalized["site"] = normalized["site"].replace("", args.default_site)
    normalized["locale"] = normalized["locale"].replace("", args.default_locale)

    # Build stable group key for split:
    # product_src_id -> product_url -> spu_image_url -> row index.
    missing = normalized["group_key"].astype(str).str.len() == 0
    if missing.any():
        normalized.loc[missing, "group_key"] = normalized.loc[missing, "product_url"].apply(
            lambda x: f"url_{short_hash(x)}" if x else ""
        )

    missing = normalized["group_key"].astype(str).str.len() == 0
    if missing.any():
        normalized.loc[missing, "group_key"] = normalized.loc[missing, "spu_image_url"].apply(
            lambda x: f"img_{short_hash(x)}" if x else ""
        )

    missing = normalized["group_key"].astype(str).str.len() == 0
    if missing.any():
        normalized.loc[missing, "group_key"] = normalized.index[missing].map(lambda i: f"row_{i}")

    # Drop invalid rows before split.
    normalized = normalized[normalized["target_desc"].astype(str).str.len() > 0].copy()
    normalized = normalized.drop_duplicates(
        subset=[
            "site",
            "locale",
            "group_key",
            "category_path",
            "source_title",
            "selling_points",
            "target_title",
            "target_desc",
        ]
    ).reset_index(drop=True)

    target_sites = [x.strip() for x in args.target_sites.split(",") if x.strip()]
    if target_sites and not site_col and args.default_site not in target_sites:
        raise ValueError(
            "Input has no site column, and default-site is not in target-sites. "
            "Please add site column or adjust --default-site/--target-sites."
        )
    if target_sites:
        normalized = normalized[normalized["site"].isin(target_sites)].reset_index(drop=True)

    return normalized, mapping


def build_splits(df: pd.DataFrame, args: argparse.Namespace) -> dict[str, pd.DataFrame]:
    train_parts: list[pd.DataFrame] = []
    val_parts: list[pd.DataFrame] = []
    test_parts: list[pd.DataFrame] = []

    for site_name, site_df in df.groupby("site", sort=True):
        group_ids = list(site_df["group_key"].astype(str).unique())
        train_groups, val_groups, test_groups = split_groups(
            group_ids,
            train_ratio=args.train_ratio,
            val_ratio=args.val_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed,
        )

        train_parts.append(site_df[site_df["group_key"].isin(train_groups)])
        val_parts.append(site_df[site_df["group_key"].isin(val_groups)])
        test_parts.append(site_df[site_df["group_key"].isin(test_groups)])

    def concat_parts(parts: list[pd.DataFrame]) -> pd.DataFrame:
        if not parts:
            return pd.DataFrame(columns=df.columns)
        return pd.concat(parts, ignore_index=True)

    return {
        "train": concat_parts(train_parts),
        "val": concat_parts(val_parts),
        "test": concat_parts(test_parts),
    }


def to_records(df: pd.DataFrame, instruction: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        record = convert_row_to_record(row, instruction=instruction)
        if record:
            out.append(record)
    return out


def write_outputs(
    splits: dict[str, list[dict[str, Any]]], output_dir: Path, dataset_prefix: str, dataset_info_name: str
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    file_map: dict[str, str] = {}
    for split_name, records in splits.items():
        file_name = f"{dataset_prefix}_{split_name}.json"
        file_map[split_name] = file_name
        out_path = output_dir / file_name
        with out_path.open("w", encoding="utf-8") as fp:
            json.dump(records, fp, ensure_ascii=False, indent=2)

    dataset_info = {}
    for split_name in ("train", "val", "test"):
        key = f"{dataset_prefix}_{split_name}"
        dataset_info[key] = {
            "file_name": file_map[split_name],
            "columns": {
                "prompt": "instruction",
                "query": "input",
                "response": "output",
            },
        }

    dataset_info_path = output_dir / dataset_info_name
    with dataset_info_path.open("w", encoding="utf-8") as fp:
        json.dump(dataset_info, fp, ensure_ascii=False, indent=2)

    return {
        "dataset_files": {k: str(output_dir / v) for k, v in file_map.items()},
        "dataset_info": str(dataset_info_path),
    }


def main() -> None:
    args = parse_args()
    validate_ratios(args.train_ratio, args.val_ratio, args.test_ratio)

    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()

    raw_df = read_table(input_path)
    prepared_df, mapping = prepare_dataframe(raw_df, args)
    if prepared_df.empty:
        raise ValueError("No rows left after cleaning/filtering. Please check input and target-sites.")

    split_df = build_splits(prepared_df, args)
    split_records = {name: to_records(df, instruction=args.instruction) for name, df in split_df.items()}
    output_info = write_outputs(
        split_records,
        output_dir=output_dir,
        dataset_prefix=args.dataset_prefix,
        dataset_info_name=args.dataset_info_name,
    )

    site_counter = Counter(prepared_df["site"].tolist())
    split_site_counter: dict[str, dict[str, int]] = defaultdict(dict)
    for split_name, df in split_df.items():
        per_site = df["site"].value_counts().to_dict()
        split_site_counter[split_name] = {k: int(v) for k, v in per_site.items()}

    summary = {
        "input_file": str(input_path),
        "output_dir": str(output_dir),
        "rows_raw": int(len(raw_df)),
        "rows_after_clean": int(len(prepared_df)),
        "rows_train": int(len(split_records["train"])),
        "rows_val": int(len(split_records["val"])),
        "rows_test": int(len(split_records["test"])),
        "site_distribution": dict(site_counter),
        "split_site_distribution": split_site_counter,
        "column_mapping": mapping,
        "files": output_info,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
