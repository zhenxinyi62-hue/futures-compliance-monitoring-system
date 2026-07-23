import requests
from bs4 import BeautifulSoup
import json


def crawl_cfachina():

    url = "https://www.cfachina.org/"


    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }


    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )


    response.encoding = "utf-8"


    print("CFA状态码:",
          response.status_code)

    print("网页长度:",
          len(response.text))


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    cases = []


    for a in soup.find_all("a"):

        title = a.get_text(
            strip=True
        )

        link = a.get(
            "href"
        )


        if not title:
            continue


        keywords = [
            "纪律处分",
            "自律",
            "处罚",
            "监管措施"
        ]


        if any(
            k in title
            for k in keywords
        ):


            if link and link.startswith("/"):

                link = (
                    "https://www.cfachina.org"
                    + link
                )


            cases.append(
                {
                    "source":
                    "中国期货业协会",

                    "type":
                    "合规处分",

                    "title":
                    title,

                    "url":
                    link
                }
            )


    print(
        "抓取数量:",
        len(cases)
    )


    return cases



if __name__ == "__main__":


    data = crawl_cfachina()


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
        "中期协更新完成"
    )
