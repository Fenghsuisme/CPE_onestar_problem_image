#!/usr/bin/env python3
"""
UVA PDF downloader + uDebug test case scraper

Usage:
  python3 uva_scraper.py 100
  python3 uva_scraper.py 100 101 102
"""

import sys, os, time, zipfile
import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDFS_NEW = os.path.join(BASE_DIR, "pdfs", "new")
ZIP_DIR  = os.path.join(BASE_DIR, "autofill", "zip_files")
DONE_DIR = os.path.join(BASE_DIR, "autofill", "done")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
AJAX_HEADERS = {**HEADERS, "X-Requested-With": "XMLHttpRequest"}
DELAY = 1.5  # 每次請求間隔（秒），避免被封鎖


# ── PDF ──────────────────────────────────────────────────────────────────────

def download_pdf(num: str) -> bool:
    volume = int(num) // 100
    url  = f"https://onlinejudge.org/external/{volume}/{num}.pdf"
    dest = os.path.join(PDFS_NEW, f"{num}.pdf")

    if os.path.exists(dest):
        print(f"  ⏭  PDF 已存在，跳過")
        return True

    os.makedirs(PDFS_NEW, exist_ok=True)
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code != 200 or b"%PDF" not in r.content[:8]:
        print(f"  ❌ PDF 下載失敗 ({r.status_code}): {url}")
        return False

    with open(dest, "wb") as f:
        f.write(r.content)
    print(f"  ✅ PDF: {dest}")
    return True


# ── uDebug helpers ───────────────────────────────────────────────────────────

def get_problem_page(session: requests.Session, num: str):
    """回傳 (soup, form_build_id, problem_nid)，失敗回傳 (None, None, None)"""
    r = session.get(f"https://www.udebug.com/UVa/{num}",
                    headers=HEADERS, timeout=30)
    if r.status_code != 200:
        return None, None, None

    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form", id="udebug-custom-problem-view-input-output-form")
    if not form:
        return None, None, None

    form_build_id = form.find("input", {"name": "form_build_id"})["value"]
    problem_nid   = form.find("input", {"name": "problem_nid"})["value"]
    return soup, form_build_id, problem_nid


def get_input_ids(soup) -> list[str]:
    """從 select_input_table 取出所有不重複的 data-id"""
    table = soup.find("div", class_="select_input_table")
    if not table:
        return []
    seen, ids = set(), []
    for a in table.find_all("a", attrs={"data-id": True}):
        nid = a["data-id"]
        if nid not in seen:
            seen.add(nid)
            ids.append(nid)
    return ids


def fetch_input(session: requests.Session, input_nid: str) -> str | None:
    r = session.post(
        "https://www.udebug.com/udebug-custom-get-selected-input-ajax",
        data={"input_nid": input_nid},
        headers=AJAX_HEADERS,
        timeout=30,
    )
    if r.status_code != 200:
        return None
    raw = r.json().get("input_value", "")
    return raw.replace("\r\n", "\n").replace("\r", "\n").strip() or None


def fetch_output(
    session: requests.Session,
    num: str,
    problem_nid: str,
    form_build_id: str,
    input_text: str,
    input_nid: str,
) -> tuple[str | None, str | None]:
    """回傳 (output_text, new_form_build_id)"""
    r = session.post(
        f"https://www.udebug.com/UVa/{num}",
        data={
            "problem_nid":   problem_nid,
            "input_data":    input_text,
            "node_nid":      input_nid,
            "op":            "Get Accepted Output",
            "form_build_id": form_build_id,
            "form_id":       "udebug_custom_problem_view_input_output_form",
        },
        headers={**HEADERS, "Referer": f"https://www.udebug.com/UVa/{num}"},
        timeout=60,
    )
    if r.status_code != 200:
        return None, None

    soup = BeautifulSoup(r.text, "html.parser")

    ta = soup.find("textarea", {"name": "output_data"})
    output = ta.get_text().replace("\r\n", "\n").replace("\r", "\n").strip() if ta else None

    # 從回傳頁面更新 form_build_id
    form = soup.find("form", id="udebug-custom-problem-view-input-output-form")
    new_token = None
    if form:
        fbi = form.find("input", {"name": "form_build_id"})
        if fbi:
            new_token = fbi["value"]

    return output, new_token


# ── autofill ─────────────────────────────────────────────────────────────────

def save_autofill(folder_name: str, cases: list[tuple[str, str]]):
    zip_path  = os.path.join(ZIP_DIR,  f"{folder_name}.zip")
    done_path = os.path.join(DONE_DIR, folder_name)
    os.makedirs(done_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w") as zf:
        for i, (inp, out) in enumerate(cases, 1):
            zf.writestr(f"{i}.in",  inp + "\n")
            zf.writestr(f"{i}.out", out + "\n")

    # 保留原始 .in/.out 檔案
    with zipfile.ZipFile(zip_path) as zf:
        for fn in zf.namelist():
            with open(os.path.join(done_path, fn), "wb") as f:
                f.write(zf.read(fn))

    print(f"  ✅ autofill 完成：{zip_path}（{len(cases)} 筆）")


# ── main logic ───────────────────────────────────────────────────────────────

def scrape_problem(num: str):
    print(f"\n{'='*52}")
    print(f"  UVA {num}")
    print(f"{'='*52}")

    # 1. PDF
    if not download_pdf(num):
        return

    session = requests.Session()

    # 2. 取 uDebug 頁面
    time.sleep(DELAY)
    soup, form_build_id, problem_nid = get_problem_page(session, num)
    if soup is None:
        print(f"  ⚠️  uDebug 無此題 (UVa/{num})，跳過測資")
        return

    input_ids = get_input_ids(soup)
    if not input_ids:
        print(f"  ⚠️  無公開測資")
        return

    print(f"  找到 {len(input_ids)} 筆測資")

    cases = []
    for i, input_nid in enumerate(input_ids, 1):
        print(f"  [{i:2d}/{len(input_ids)}] nid={input_nid}", end="", flush=True)

        # 取 input
        try:
            time.sleep(DELAY)
            inp = fetch_input(session, input_nid)
        except Exception as e:
            print(f"  ❌ input 例外：{e}，跳過")
            continue
        if inp is None:
            print("  ❌ input 失敗，跳過")
            continue

        # 取 output（用當前 form_build_id）
        try:
            time.sleep(DELAY)
            out, new_token = fetch_output(
                session, num, problem_nid, form_build_id, inp, input_nid
            )
        except Exception as e:
            print(f"  ❌ output 例外：{e}，跳過")
            continue
        if new_token:
            form_build_id = new_token  # 更新 token

        if out is None:
            print("  ❌ output 失敗，跳過")
            continue

        print(f"  ✅  in={len(inp)}c  out={len(out)}c")
        cases.append((inp, out))

    if cases:
        save_autofill(f"uva{num}", cases)
    else:
        print("  ⚠️  沒有可用測資")


def main():
    if len(sys.argv) < 2:
        print("用法：python3 uva_scraper.py <題號> [題號 ...]")
        print("  例：python3 uva_scraper.py 100")
        print("      python3 uva_scraper.py 100 101 102")
        sys.exit(1)

    os.makedirs(PDFS_NEW, exist_ok=True)
    os.makedirs(ZIP_DIR,  exist_ok=True)
    os.makedirs(DONE_DIR, exist_ok=True)

    for num in sys.argv[1:]:
        scrape_problem(num.strip())

    print("\n✅ 全部完成")


if __name__ == "__main__":
    main()
