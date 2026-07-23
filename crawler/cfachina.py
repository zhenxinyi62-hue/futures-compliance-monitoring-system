import requests
import re
import json
import os
from bs4 import BeautifulSoup


# ==========================
# 中期协纪律处分页面
# ==========================

URL = (
    "https://www.cfachina.org/"
    "informationpublicity/discipline/"
)


HEADERS = {

    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

}



# ==========================
# 获取网页
# ==========================

def get_html():


    print("===================")
    print("访问中期协")
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


    response.encoding="utf-8"


    html = response.text


    print(
        "网页长度:",
        len(html)
    )


    return html





# ==========================
# 保存网页
# ==========================

def save_html(html):


    with open(

        "cfa_debug.html",

        "w",

        encoding="utf-8"

    ) as f:

        f.write(html)



    print(
        "已保存 cfa_debug.html"
    )





# ==========================
# 搜索接口
# ==========================

def find_api(html):


    print("===================")
    print("搜索接口关键词")
    print("===================")



    keywords = [

        "ajax",

        "api",

        "json",

        "list",

        "page",

        "discipline",

        "information",

        "search"

    ]



    for k in keywords:


        count = html.lower().count(k)


        print(

            k,

            "出现",

            count,

            "次"

        )



    print("===================")



    # 查找URL

    urls = re.findall(

        r"""

        (?:
        https?://
        |
        /
        )

        [^"'<> ]+

        """,

        html

    )



    print(
        "发现URL数量:",
        len(urls)
    )



    for u in urls[:50]:

        if any(

            key in u.lower()

            for key in [

                "api",

                "json",

                "list",

                "discipline",

                "search"

            ]

        ):

            print(
                "可能接口:",
                u
            )







# ==========================
# 查找JS文件
# ==========================

def find_js(html):


    print("===================")

    print("JS文件")

    print("===================")



    soup = BeautifulSoup(

        html,

        "html.parser"

    )


    scripts = soup.find_all(
        "script"
    )


    for s in scripts:


        src = s.get(
            "src"
        )


        if src:

            print(src)






# ==========================
# 测试公告关键词
# ==========================

def search_notice(html):


    print("===================")

    print("关键词测试")

    print("===================")


    words=[

        "中辉期货",

        "恒银期货",

        "恒力期货",

        "纪律处分",

        "中期协字"

    ]


    for w in words:


        print(

            w,

            html.find(w)

        )







# ==========================
# 主程序
# ==========================


if __name__=="__main__":


    html = get_html()


    save_html(html)


    find_api(html)


    find_js(html)


    search_notice(html)


    print("===================")

    print(
        "检测完成"
    )

    print("===================")
