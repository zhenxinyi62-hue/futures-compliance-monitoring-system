import requests
from bs4 import BeautifulSoup
import json


def crawl_dce():

    url = "http://www.dce.com.cn/dce/xxfw/ggtz/index.html"


    headers = {

        "User-Agent":
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),

        "Accept":
        (
            "text/html,"
            "application/xhtml+xml,"
            "application/xml;q=0.9,"
            "*/*;q=0.8"
        ),

        "Accept-Language":
        "zh-CN,zh;q=0.9",

        "Referer":
        "http://www.dce.com.cn/"

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

    print("DCE状态码:")
    print(response.status_code)

    print("--------------------")

    print("DCE网页长度:")
    print(len(response.text))

    print("====================")


    print("网页前500字符:")
    print(response.text[:500])

    print("====================")


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    announcements = []


    for a in soup.find_all("a"):


        title = a.get_text(
            strip=True
        )


        link = a.get(
            "href"
        )


        if not title:
            continue


        if (
            "公告" in title
            or "通知" in title
            or "提示" in title
        ):


            if link:


                if link.startswith("/"):

                    link = (
                        "http://www.dce.com.cn"
                        + link
                    )


                announcements.append(
                    {
                        "exchange": "DCE",
                        "title": title,
                        "type": "交易所公告",
                        "url": link
                    }
                )


    print(
        "DCE公告数量:",
        len(announcements)
    )


    return announcements



if __name__ == "__main__":


    data = crawl_dce()


    with open(
        "data/dce_announcements.json",
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
        "DCE更新完成"
    )
