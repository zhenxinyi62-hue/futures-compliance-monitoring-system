import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime


URL = "https://www.cfachina.org/informationpublicity/discipline/"


HEADERS = {
    "User-Agent": 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


BASE_URL = "https://www.cfachina.org"



def fix_url(url):

    if not url:
        return ""

    if url.startswith("http"):
        return url

    if url.startswith("./"):
        return BASE_URL + "/" + url[2:]

    if url.startswith("/"):
        return BASE_URL + url

    return BASE_URL + "/" + url



def extract_company(title):

    patterns = [

        r"关于对(.*?期货有限公司)",
        r"(.*?期货有限公司)",
        r"对(.*?期货公司)"

    ]


    for p in patterns:

        result = re.search(
            p,
            title
        )

        if result:

            return result.group(1)



    return "未识别机构"




def crawl_cfa():


    print("===================")
    print("开始访问中期协")
    print("===================")



    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )


    print(
        "状态码:",
        response.status_code
    )


    response.encoding = "utf-8"


    html = response.text
    with open(
    "cfa_full.html",
    "w",
    encoding="utf-8"
    ) as f:
    f.write(html)


    print(
        "网页长度:",
        len(html)
    )



    # 保存网页
    with open(
        "cfa_debug.html",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)



    print("===================")
    print("网页前500字符")
    print("===================")

    print(
        html[:500]
    )



    soup = BeautifulSoup(
        html,
        "html.parser"
    )



    links = soup.find_all("a")



    print("===================")
    print(
        "链接数量:",
        len(links)
    )
    print("===================")



    data = []

    seen=set()



    for a in links:


        title = a.text.strip()

        href = a.get("href")



        if not title or not href:
            continue



        url = fix_url(href)



        # 打印可能公告

        if (
            "纪律" in title
            or
            "处分" in title
            or
            "决定" in title
        ):

            print(
                "发现:",
                title
            )

            print(
                url
            )


        # 排除栏目

        if href.endswith(
            "discipline/"
        ):

            continue



        # 只保存详情页

        if (
            "discipline/" not in url
        ):

            continue



        if url in seen:
            continue


        seen.add(url)



        item = {

            "exchange":
                "中期协",

            "source":
                "中国期货业协会",

            "company":
                extract_company(title),

            "person":
                "",

            "title":
                title,

            "type":
                "纪律处分",

            "violation":
                title,

            "penalty":
                "详见中国期货业协会公告",

            "date":
                datetime.now()
                .strftime(
                    "%Y-%m-%d"
                ),

            "url":
                url

        }


        data.append(item)



    print("===================")

    print(
        "抓取公告数量:",
        len(data)
    )

    print("===================")



    return data




def save_data(data):


    os.makedirs(
        "data",
        exist_ok=True
    )


    with open(
        "data/compliance_cases.json",
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


    print(
        "JSON保存完成"
    )





if __name__ == "__main__":


    result = crawl_cfa()


    save_data(result)


    print(
        "中期协更新完成"
    )
