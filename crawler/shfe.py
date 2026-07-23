import requests
from bs4 import BeautifulSoup
import json


def crawl_shfe():

    url = "https://www.shfe.com.cn/publicnotice/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
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


    print("状态码:", response.status_code)

    print("网页长度:", len(response.text))


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    announcements = []


    # 查找公告链接
    for a in soup.find_all("a"):

        title = a.get_text(
            strip=True
        )

        link = a.get(
            "href"
        )


        if not title:
            continue


        # 只保留公告
        if (
            "公告" in title
            or "通知" in title
        ):

            if link:

                if link.startswith("/"):

                    link = (
                        "https://www.shfe.com.cn"
                        + link
                    )


                # 去重
                exists = any(
                    x["url"] == link
                    for x in announcements
                )


                if not exists:

                    announcements.append(
                        {
                            "exchange": "SHFE",
                            "title": title,
                            "type": "交易所公告",
                            "url": link
                        }
                    )


    print(
        "抓取公告数量:",
        len(announcements)
    )


    return announcements



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
