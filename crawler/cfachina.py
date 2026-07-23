import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
 
# 中期协网站
URL = "https://www.cfachina.org/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
 
# 只关心真正是"纪律处分/自律处分"类公告的标题关键词
# （原来的关键词列表里有单独的"违规""处罚"，太宽泛，容易夹带无关新闻，
#  这里收窄一些，减少误抓）
TITLE_KEYWORDS = ["纪律处分", "自律处分", "监管措施"]
 
# 详情页里"当事人：XXX"字段的正则，比在标题里瞎猜公司名可靠得多
COMPANY_IN_DETAIL_RE = re.compile(r"当事人[:：]\s*([^（，,\n]+)")
DOC_NO_RE = re.compile(r"中期协字〔\d{4}〕\d+号")
# 网址里的日期，形如 .../202607/t20260710_89309.html，20260710 就是真实发布日期
DATE_IN_URL_RE = re.compile(r"t(\d{4})(\d{2})(\d{2})_\d+\.html")
 
 
def fix_url(url):
    """补全链接。原来的版本只处理了以 / 开头的相对路径，
    不带斜杠的相对路径（比如 informationpublicity/xxx.html）会被原样
    返回，生成打不开的坏链接——这里统一用 urljoin 处理，什么形式的
    相对路径都能补全。
    """
    if not url:
        return ""
    from urllib.parse import urljoin
    return urljoin(URL, url)
 
 
def extract_date_from_url(url):
    """优先从网址文件名里取真实发布日期，而不是用脚本运行时间。
    这是修复"日期永远是今天"这个问题的关键。
    """
    m = DATE_IN_URL_RE.search(url)
    if m:
        y, mo, d = m.groups()
        return f"{y}-{mo}-{d}"
    return None
 
 
def extract_company_from_title(title):
    """标题里猜公司名，作为兜底方案（详情页抓取失败时才用这个）。"""
    patterns = [
        r"关于对(.*?期货(?:有限公司|股份有限公司|公司))",
        r"对(.*?期货(?:有限公司|股份有限公司|公司))",
        r"^(.*?期货(?:有限公司|股份有限公司|公司))",
    ]
    for pattern in patterns:
        result = re.search(pattern, title)
        if result:
            return result.group(1).strip()
 
    if "期货有限公司" in title:
        start = title.find("期货有限公司")
        before = title[:start]
        for i in range(len(before) - 1, -1, -1):
            if before[i] in "，。关于对":
                before = before[i + 1:]
                break
        return before + "期货有限公司"
 
    return None
 
 
def fetch_detail(url):
    """抓详情页，拿到更可靠的公司名、文号、真实日期（作为网址日期的兜底）。
    请求失败时返回 None，调用方会退回用标题里猜的公司名。
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")
        full_text = soup.get_text("\n", strip=True)
 
        company_match = COMPANY_IN_DETAIL_RE.search(full_text)
        doc_no_match = DOC_NO_RE.search(full_text)
 
        return {
            "company": company_match.group(1).strip() if company_match else None,
            "doc_no": doc_no_match.group(0) if doc_no_match else None,
        }
    except Exception as e:
        print(f"    详情页抓取失败（{url}）：{e}")
        return None
 
 
def crawl_cfa():
    print("===================")
    print("开始抓取中国期货业协会")
    print("===================")
 
    response = requests.get(URL, headers=HEADERS, timeout=20)
    print("状态码:", response.status_code)
    response.encoding = "utf-8"
 
    soup = BeautifulSoup(response.text, "html.parser")
 
    data = []
    seen_urls = set()
 
    for a in soup.find_all("a"):
        title = a.text.strip()
        link = a.get("href")
 
        if not title or not link:
            continue
 
        if not any(k in title for k in TITLE_KEYWORDS):
            continue
 
        link = fix_url(link)
        if link in seen_urls:
            continue
        seen_urls.add(link)
 
        # 只有公司级别的通报才要，个人从业人员的记录跳过
        if "期货" not in title:
            continue
 
        print(f"处理: {title[:40]}...")
 
        # 优先抓详情页拿准确公司名和文号；失败了再退回标题里猜
        detail = fetch_detail(link)
        company = (detail and detail.get("company")) or extract_company_from_title(title) or "未识别机构"
        doc_no = detail and detail.get("doc_no")
 
        # 日期：优先用网址里的真实发布日期
        date = extract_date_from_url(link)
        if not date:
            print(f"    警告：无法从网址提取日期，跳过此条（{link}）")
            continue
 
        item = {
            "company": company,
            "source": "中国期货业协会",
            "type": "纪律处分",
            "violation": title,
            "penalty": "详见中国期货业协会公告",
            "doc_no": doc_no or "",
            "date": date,
            "url": link,
        }
        data.append(item)
 
    print("本次抓取数量:", len(data))
    return data
 
 
def save_data(new_data):
    """合并保存：不再用 'w' 直接覆盖整个文件，而是把新抓到的数据和
    已有文件里的旧数据按 url 去重合并，这样老记录不会因为被首页顶下去
    而丢失，数据是越攒越多而不是每次清零重来。
    """
    os.makedirs("data", exist_ok=True)
    path = "data/compliance_cases.json"
 
    existing = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception as e:
            print(f"读取已有数据失败（将视为空）：{e}")
 
    by_url = {item["url"]: item for item in existing}
    for item in new_data:
        by_url[item["url"]] = item  # 新数据覆盖同 url 的旧数据（比如公司名后来抓准了）
 
    merged = sorted(by_url.values(), key=lambda x: x["date"], reverse=True)
 
    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
 
    print(f"保存完成: {path}（累计 {len(merged)} 条，本次新增/更新 {len(new_data)} 条）")
 
 
if __name__ == "__main__":
    result = crawl_cfa()
    save_data(result)
    print("中期协更新完成")
