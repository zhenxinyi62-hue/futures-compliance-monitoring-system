# -*- coding: utf-8 -*-
"""
中国期货业协会（CFA，cfachina.org）"纪律处分"栏目 抓取脚本
==========================================================

数据源：https://www.cfachina.org/informationpublicity/discipline/
经实测：
  - 列表页由前端 JS 异步渲染，直接用 requests 拿到的 HTML 里没有数据，
    需要用带 JS 渲染能力的浏览器（本脚本用 Playwright）打开列表页，
    等内容渲染完成后再解析。
  - 详情页（形如 .../discipline/202607/t20260710_89309.html）是服务端
    直出的静态 HTML，requests 就能直接拿到完整正文，不需要浏览器。
  - 全站没有遇到验证码/WAF 拦截（这点和上期所/大商所/郑商所官网不同，
    那几个官网有滑块验证码，本脚本没有做任何绕过验证码的处理，
    也不建议这么做）。

用法：
  pip install playwright beautifulsoup4 requests --break-system-packages
  playwright install chromium
  python cfa_discipline_scraper.py --pages 2 --out discipline.json

建议部署方式：
  用 cron 或 systemd timer 每天跑 1~2 次即可（协会发布频率通常是
  按工作日更新，不需要高频轮询），避免给对方服务器造成压力。

免责声明：
  本脚本仅抓取协会官网主动公示的公开信息，用于内部合规监控。
  请遵守 cfachina.org 的使用条款，合理控制抓取频率。
  正文解析基于本次实测页面结构编写的规则，如协会网站后续改版，
  解析规则（parse_detail 函数里的正则）可能需要相应调整。
"""

import argparse
import json
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

LIST_URL = "https://www.cfachina.org/informationpublicity/discipline/"
DETAIL_LINK_RE = re.compile(r"/informationpublicity/discipline/(\d{6})/(t\d+_\d+)\.html")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def fetch_list_links(max_pages=1, headless=True):
    """用 Playwright 打开列表页（含翻页），抓出所有详情页链接。

    列表页是异步渲染的，所以必须等页面执行完 JS 才能拿到 <a> 标签。
    如果协会官网改了翻页方式（比如从"下一页"按钮换成参数翻页），
    这里的翻页逻辑要跟着改。
    """
    from playwright.sync_api import sync_playwright

    links = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(user_agent=HEADERS["User-Agent"])
        page.goto(LIST_URL, wait_until="networkidle", timeout=30000)

        for i in range(max_pages):
            # 等列表容器渲染出真实链接（避免抓到"暂无数据"占位状态）
            page.wait_for_timeout(1500)
            anchors = page.eval_on_selector_all(
                "a[href*='/informationpublicity/discipline/']",
                "els => els.map(e => ({href: e.href, text: e.innerText}))",
            )
            for a in anchors:
                m = DETAIL_LINK_RE.search(a["href"])
                if m:
                    links.append({"url": a["href"], "list_text": a["text"].strip()})

            # 尝试翻页（选择器需要根据实际页面调整；很多此类政府/协会站点
            # 用"下一页"文字链接，如果找不到就说明到最后一页了）
            next_btn = page.query_selector("a:has-text('下一页')")
            if next_btn and i < max_pages - 1:
                next_btn.click()
                page.wait_for_load_state("networkidle")
            else:
                break

        browser.close()

    # 去重
    seen, unique = set(), []
    for item in links:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    return unique


DATE_IN_URL_RE = re.compile(r"t(\d{4})(\d{2})(\d{2})_\d+\.html")


def parse_detail(url):
    """请求详情页并解析出结构化字段。"""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")

    # 正文容器：实测该站正文在 h3(纪律处分) 之后、"附件下载"之前的一段 <p>
    full_text = soup.get_text("\n", strip=True)

    title_match = re.search(r"关于对.*?(?:纪律处分|作出纪律处分)的决定", full_text)
    title = title_match.group(0) if title_match else None

    doc_no_match = re.search(r"中期协字〔\d{4}〕\d+号", full_text)
    doc_no = doc_no_match.group(0) if doc_no_match else None

    # 当事人（第一个通常是被处分的期货公司，但也可能是个人——
    # 是否为公司交给 is_company 字段判断，不在这里过滤，方便调试时
    # 也能看到个人记录）
    company_match = re.search(r"当事人[:：]\s*([^（，,\n]+)", full_text)
    company = company_match.group(1).strip() if company_match else None
    is_company = bool(company and "期货" in company)

    # 处分决定项，形如 （一）给予XXX"YYY"的纪律处分（引号为中文全角引号）
    decisions = re.findall(r'给予([^“”]{1,30})“(.{1,20})”的纪律处分', full_text)

    # 决定书发布日期：优先用网址文件名里的日期（如 t20260710_89309.html
    # 里的 20260710），这个是协会发布该文章时打的时间戳，比在正文里搜日期
    # 靠谱得多——之前的版本用"正文里最后一个日期"，结果经常抓到页面底部
    # "相关文章"侧栏里其他文章的日期，导致日期显示错误。
    url_date_match = DATE_IN_URL_RE.search(url)
    if url_date_match:
        y, m, d = url_date_match.groups()
        decision_date = f"{y}-{m}-{d}"
    else:
        # 兜底：网址不含日期时，退回正文搜索（不太准，仅做保底）
        date_match = re.findall(r"(\d{4})年(\d{1,2})月(\d{1,2})日", full_text)
        decision_date = None
        if date_match:
            y, m, d = date_match[0]  # 取正文里第一个日期，比最后一个更接近正文开头的落款
            decision_date = f"{y}-{int(m):02d}-{int(d):02d}"

    return {
        "url": url,
        "title": title,
        "doc_no": doc_no,
        "company": company,
        "is_company": is_company,
        "decisions": [{"target": t.strip(), "penalty": p.strip()} for t, p in decisions],
        "decision_date": decision_date,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
    }


def transform_to_app_format(records):
    """把 parse_detail 的原始结果，按公司分组整理成小程序前端可以直接
    fetch() 读取的结构：[{company, docNo, url, nodes:[...]}]
    """
    by_company = {}
    for r in records:
        if not r.get("company") or not r.get("is_company"):
            continue  # 跳过个人从业人员记录，只保留期货公司本身
        key = r["company"]
        node = {
            "date": r.get("decision_date") or "",
            "cat": "violation",
            "label": "协会纪律处分",
            "text": (
                f"{r['title']}（{r['doc_no'] or '文号待核实'}）。"
                if r.get("title") else "协会纪律处分决定（详情见原文链接）。"
            ),
        }
        if key not in by_company:
            by_company[key] = {
                "company": key,
                "docNo": r.get("doc_no") or "",
                "url": r["url"],
                "nodes": [],
            }
        by_company[key]["nodes"].append(node)

    # 每家公司按日期新到旧排序
    app_data = list(by_company.values())
    for c in app_data:
        c["nodes"].sort(key=lambda n: n["date"], reverse=True)
    app_data.sort(key=lambda c: c["nodes"][0]["date"] if c["nodes"] else "", reverse=True)
    return app_data


def transform_to_violations_schema(records):
    """转换成用户现有 index.html 期望的结构：
    { generated_at: "...", items: [{id, exchange, company, type, content, penalty, date}] }

    注意：这批数据来自中国期货业协会（行业自律组织），不是某个交易所，
    所以 exchange 字段统一标注为「中期协」，不要伪造成具体某个交易所，
    避免误导。
    """
    items = []
    for i, r in enumerate(records, 1):
        if not r.get("company") or not r.get("is_company"):
            continue  # 跳过个人从业人员记录，只保留期货公司本身
        decisions = r.get("decisions") or []
        penalty_text = "；".join(f"{t}：{p}" for t, p in
                                  [(d["target"], d["penalty"]) for d in decisions]) or ""
        # 简单规则判断类型标签，可按需调整
        joined_penalty = " ".join(d["penalty"] for d in decisions)
        if any(k in joined_penalty for k in ["暂停会员资格", "撤销", "禁止"]):
            item_type = "处罚"
        elif decisions:
            item_type = "违规"
        else:
            item_type = "通知"

        items.append({
            "id": i,
            "exchange": "中期协",
            "company": r["company"],
            "type": item_type,
            "content": r.get("title") or "协会纪律处分决定",
            "penalty": penalty_text,
            "date": r.get("decision_date") or "",
            "source_url": r["url"],
            "doc_no": r.get("doc_no") or "",
        })

    items.sort(key=lambda x: x["date"], reverse=True)
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "items": items,
    }


def main():
    parser = argparse.ArgumentParser(description="抓取中期协纪律处分公示")
    parser.add_argument("--pages", type=int, default=1, help="抓取的列表页数")
    parser.add_argument("--out", type=str, default="discipline.json", help="原始结构化数据输出路径")
    parser.add_argument("--app-json", type=str, default=None,
                         help="额外输出一份「按公司分组」的 JSON（旧版原型用，如 data/dynamics.json）")
    parser.add_argument("--violations-json", type=str, default=None,
                         help="额外输出一份「扁平列表」的 JSON（适配 data/violations.json 结构）")
    parser.add_argument("--delay", type=float, default=1.5, help="每次请求详情页之间的等待秒数")
    args = parser.parse_args()

    print(f"[1/2] 打开列表页，翻 {args.pages} 页...")
    links = fetch_list_links(max_pages=args.pages)
    print(f"    找到 {len(links)} 条详情链接")

    results = []
    for i, item in enumerate(links, 1):
        try:
            print(f"[2/2] ({i}/{len(links)}) 抓取详情：{item['url']}")
            detail = parse_detail(item["url"])
            detail["list_text"] = item["list_text"]
            results.append(detail)
        except Exception as e:
            print(f"    跳过（解析失败）：{e}")
        time.sleep(args.delay)  # 控制请求频率，做个文明的爬虫

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"完成，共 {len(results)} 条记录已写入 {args.out}")

    if args.app_json:
        app_data = transform_to_app_format(results)
        with open(args.app_json, "w", encoding="utf-8") as f:
            json.dump(app_data, f, ensure_ascii=False, indent=2)
        print(f"已额外生成前端可读取的 {args.app_json}（{len(app_data)} 家公司）")

    if args.violations_json:
        violations_payload = transform_to_violations_schema(results)
        with open(args.violations_json, "w", encoding="utf-8") as f:
            json.dump(violations_payload, f, ensure_ascii=False, indent=2)
        print(f"已额外生成 {args.violations_json}（{len(violations_payload['items'])} 条记录）")


if __name__ == "__main__":
    main()
