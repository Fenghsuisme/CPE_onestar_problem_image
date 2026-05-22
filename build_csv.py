#!/usr/bin/env python3
"""
PDF → PNG → DMOJ CSV

用法：
  單題：python3 build_csv.py 100
  多題：python3 build_csv.py 100 524 439
  全部：python3 build_csv.py
"""

import sys
import os
import csv
import re

try:
    import fitz  # pymupdf
except ImportError:
    print("❌ 請先安裝 pymupdf：pip install pymupdf")
    sys.exit(1)

# ── 設定區 ──────────────────────────────────────────────
PDFS_DIR   = "pdfs/new"
OUTPUT_CSV = "output.csv"

DEFAULT_TIME_LIMIT   = 3
DEFAULT_MEMORY_LIMIT = 262144

ALLOWED_LANGUAGES = "C,C11,Clang,Clang++,CPP03,CPP11,CPP14,CPP17,CPP20"
PROBLEM_GROUP     = "NUK"
PROBLEM_TYPES     = "CPP"
AUTHORS           = "Feng,A1115514"
POINTS            = 1
IS_PUBLIC         = "FALSE"
IS_FULL_MARKUP    = "FALSE"
PARTIAL           = "FALSE"
SHORT_CIRCUIT     = "FALSE"
IS_MANUALLY_MANAGED = "FALSE"

GITHUB_IMG_BASE = (
    "https://raw.githubusercontent.com"
    "/Fenghsuisme/CPE_onestar_problem_image/main/images"
)

IMG_REPO_DIR = "images"
PNG_DPI      = 150  # 解析度，150 dpi 品質夠用且檔案不會太大

CSV_FIELDS = [
    "code", "name", "description", "group", "time_limit", "memory_limit",
    "points", "types", "authors", "curators", "testers", "allowed_languages",
    "is_public", "partial", "short_circuit", "is_manually_managed",
    "license", "og_image", "summary", "banned_users", "organizations",
    "is_organization_private", "enable_waveform", "enable_ppa",
    "ppa_maximum_fmax", "f4pga_board", "f4pga_target_fmax", "openlane_pdk",
    "openlane_ppa_score", "openlane_critical_path_ns", "openlane_core_area_um2",
    "openlane_power_total", "solution_content", "solution_is_public",
    "solution_authors", "translation_en_name", "translation_en_description",
    "translation_zh_hant_name", "translation_zh_hant_description",
    "clarifications", "language_limits", "is_full_markup"
]
# ────────────────────────────────────────────────────────


def pdf_to_png(problem_number: str) -> list[str]:
    """
    把 PDF 每頁轉成 PNG，存到 image repo。
    回傳該題所有 PNG 的 GitHub raw URL 列表。
    """
    pdf_path = os.path.join(PDFS_DIR, f"{problem_number}.pdf")
    if not os.path.exists(pdf_path):
        print(f"  [錯誤] 找不到 {pdf_path}")
        return []

    dest_dir = os.path.join(IMG_REPO_DIR, problem_number)
    os.makedirs(dest_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    urls = []
    mat = fitz.Matrix(PNG_DPI / 72, PNG_DPI / 72)  # 72 dpi 是 PDF 基準

    for i, page in enumerate(doc, start=1):
        filename = f"{problem_number}_p{i}.png"
        out_path = os.path.join(dest_dir, filename)

        # 若已存在就跳過（避免重複轉換）
        if os.path.exists(out_path):
            print(f"  ⏭  已存在 {out_path}，跳過")
        else:
            pix = page.get_pixmap(matrix=mat)
            pix.save(out_path)
            print(f"  ✅ 產生 {out_path}")

        urls.append(f"{GITHUB_IMG_BASE}/{problem_number}/{filename}")

    doc.close()
    return urls


def build_description(img_urls: list[str]) -> str:
    """
    組合 description：圖片 + 空白的 Sample Input/Output。
    """
    lines = []

    for url in img_urls:
        lines.append(f"![]({url})\n")

    lines.append("")
    lines.append("### Sample Input")
    lines.append("```text")
    lines.append("")
    lines.append("```")
    lines.append("")
    lines.append("### Sample Output")
    lines.append("```text")
    lines.append("")
    lines.append("```")

    return "\n".join(lines)


def build_row(problem_number: str) -> dict | None:
    print(f"\n處理 {problem_number}:")

    img_urls = pdf_to_png(problem_number)
    if not img_urls:
        return None

    print(f"  共 {len(img_urls)} 頁")

    # PDF 處理完後移到 old/
    old_dir = os.path.join(os.path.dirname(PDFS_DIR), "old")
    os.makedirs(old_dir, exist_ok=True)
    pdf_src = os.path.join(PDFS_DIR, f"{problem_number}.pdf")
    pdf_dst = os.path.join(old_dir, f"{problem_number}.pdf")
    os.rename(pdf_src, pdf_dst)
    print(f"  📦 已移至 pdfs/old/{problem_number}.pdf")

    code        = f"uva{problem_number}"
    name        = f"[UVa {problem_number}]"
    description = build_description(img_urls)

    row = {field: "" for field in CSV_FIELDS}
    row.update({
        "code":                code,
        "name":                name,
        "description":         description,
        "group":               PROBLEM_GROUP,
        "time_limit":          DEFAULT_TIME_LIMIT,
        "memory_limit":        DEFAULT_MEMORY_LIMIT,
        "points":              POINTS,
        "types":               PROBLEM_TYPES,
        "authors":             AUTHORS,
        "allowed_languages":   ALLOWED_LANGUAGES,
        "is_public":           IS_PUBLIC,
        "partial":             PARTIAL,
        "short_circuit":       SHORT_CIRCUIT,
        "is_manually_managed": IS_MANUALLY_MANAGED,
        "is_full_markup":      IS_FULL_MARKUP,
    })
    return row


def write_csv(rows: list[dict], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n✅ 已寫入 {path}（共 {len(rows)} 題）")


def get_all_problem_numbers() -> list[str]:
    if not os.path.isdir(PDFS_DIR):
        print(f"[錯誤] 找不到資料夾 {PDFS_DIR}/")
        sys.exit(1)
    nums = sorted(
        os.path.splitext(f)[0]
        for f in os.listdir(PDFS_DIR)
        if f.endswith(".pdf")
    )
    if not nums:
        print(f"[錯誤] {PDFS_DIR}/ 內沒有 PDF 檔案")
        sys.exit(1)
    return nums


def main():
    if len(sys.argv) >= 2:
        nums = sys.argv[1:]
        print(f"── 指定題目模式：{', '.join(nums)} ──")
    else:
        nums = get_all_problem_numbers()
        print(f"── 批量模式：共 {len(nums)} 題 ──")

    rows = []
    for num in nums:
        row = build_row(num)
        if row:
            rows.append(row)

    if rows:
        write_csv(rows, OUTPUT_CSV)
        print("\n📌 記得把圖片推上 GitHub：")
        print(f"   cd image/CPE_onestar_problem_image")
        print(f"   git add .")
        print(f"   git commit -m 'add problem images'")
        print(f"   git push")
        print(f"   （push 完再匯入 DMOJ）")


if __name__ == "__main__":
    main()