import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime


# ===============================
# 中国期货业协会纪律处分栏目
# ===============================

URL = (
    "https://www.cfachina.org/"
    "informationpublicity/discipline/"
)


HEADERS = {

    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

}



# ===============================
# URL处理
# ===============================

def fix_url(url):

    if not url:
        return ""

    if url.startswith("./"):

        return (
            "https://www.cfachina.org/"
            + url[2:]
        )


    if url.startswith("/"):

        return (
            "https://www.cfachina.org"
            + url
        )


    if url.startswith("http"):

        return url


    return (
        "https://www.cfachina.org/"
        + url
    )





# ===============================
# 提取机构名称
# ===============================

def extract_company(title):


    patterns = [

        # 关于对XX期货有限公司...
        r"关于对(.*?期货(?:有限公司|股份有限公司|公司))",

        # XX期货有限公司关于
        r"^(.*?期货(?:有限公司|股份有限公司|公司))",

        # 对XX期货有限公司
        r"对(.*?期货(?:有限公司|股份有限公司|公司))",

    ]


    for p in patterns:


        result = re.search(
            p,
            title
        )


        if result:

            return (
                result.group(1)
                .strip()
            )



    # 找不到公司时识别人名

    name_pattern = (
        r"关于对(.*?)作出"
    )


    result = re.search(
        name_pattern,
        title
    )


    if result:

        return (
            result.group(1)
            .strip()
            +
            "（个人）"
        )



    return "未识别机构"







# ===============================
# 抓取公告
# ===============================

def crawl_cfa():


    print("===================")

    print(
        "开始抓取中国期货业协会"
    )

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



    soup = BeautifulSoup(

        response.text,

        "html.parser"

    )

    
    print(response.text[:1000]
    print("==================="))
    print("===================")

    data = []



    seen = set()



    # 只处理列表区域链接

    for a in soup.find_all("a"):


        title = (
            a.text
            .strip()
        )


        href = a.get(
            "href"
        )



        if not title or not href:

            continue



        # 排除菜单

        if title in [

            "纪律处分",

            "首页",

            "更多",

            "返回"

        ]:

            continue



        # 只保留真正公告

        if (
            "关于对" not in title
            and
            "纪律处分" not in title
            and
            "处分" not in title
        ):

            continue



        # 排除栏目自身

        if (
            href.endswith(
                "discipline/"
            )
        ):

            continue



        url = fix_url(
            href
        )



        # 去重

        if url in seen:

            continue


        seen.add(url)



        company = extract_company(
            title
        )



        item = {


            "exchange":

                "中期协",


            "source":

                "中国期货业协会",


            "company":

                company,


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


        data.append(
            item
        )



    print(
        "抓取数量:",
        len(data)
    )



    return data







# ===============================
# 保存数据
# ===============================

def save_data(data):


    os.makedirs(

        "data",

        exist_ok=True

    )



    path = (

        "data/compliance_cases.json"

    )



    with open(

        path,

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
        "保存完成:",
        path
    )







# ===============================
# 主程序
# ===============================

if __name__ == "__main__":


    result = crawl_cfa()


    save_data(result)


    print(
        "中期协更新完成"
    )
