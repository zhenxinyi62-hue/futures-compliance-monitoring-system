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
        timeout=20,
        allow_redirects=True
    )


    response.encoding = "utf-8"


    print("====================")
    print("请求地址:")
    print(url)

    print("--------------------")

    print("最终地址:")
    print(response.url)

    print("--------------------")

    print("状态码:")
    print(response.status_code)

    print("--------------------")

    print("网页长度:")
    print(len(response.text))

    print("====================")


    print("网页内容前500字符:")
    print(response.text[:500])


    print("====================")


    # 搜索可能接口

    print("搜索接口关键词")
    print("====================")


    keywords = [
        "api",
        "json",
        "ajax",
        "notice",
        "publicnotice",
        "list",
        "page",
        "data"
    ]


    for key in keywords:

        if key.lower() in response.text.lower():

            print(
                "发现:",
                key
            )


    print("====================")


    # 提取网页中的URL

    print("发现URL:")
    print("====================")


    urls = re.findall(
        r'https?://[^"\']+',
        response.text
    )


    for u in urls:

        print(u)


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


    print("SHFE更新完成")
