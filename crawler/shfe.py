import requests
from bs4 import BeautifulSoup
import json
import re


def crawl_shfe():

    url = "https://www.shfe.com.cn/publicnotice/"


    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120 Safari/537.36"
        ),
        "Referer": "https://www.shfe.com.cn/"
    }


    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )


    response.encoding = "utf-8"


    print("====================")
    print("状态码:", response.status_code)
    print("网页长度:", len(response.text))
    print("====================")


    # 打印网页标题
    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    if soup.title:
        print(
            "网页标题:",
            soup.title.text.strip()
        )


    print("====================")
    print("查找可能的数据接口")
    print("====================")


    # 查找网页中的URL
    urls = re.findall(
        r'https?://[^"\']+',
        response.text
    )


    for u in urls:

        print(u)



    print("====================")
    print("查找api关键词")
    print("====================")


    # 查找可能的接口关键词
    keywords = [
        "api",
        "json",
        "ajax",
        "notice",
        "publicnotice",
        "list",
        "page"
    ]


    for key in keywords:

        if key.lower() in response.text.lower():

            print(
                "发现关键词:",
                key
            )


    print("====================")


    return []



if __name__ == "__main__":


    data = crawl_shfe()


    with open(
        "data/announcements.json",
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
        "SHFE更新完成"
    )
