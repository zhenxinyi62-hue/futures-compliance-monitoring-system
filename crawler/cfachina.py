import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime


# 中期协网站
URL = "https://www.cfachina.org/"

HEADERS = {

    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

}



def extract_company(title):

    """
    从标题中提取期货公司名称

    示例：
    关于对XX期货有限公司采取纪律处分的决定

    返回：
    XX期货有限公司
    """


    patterns = [

        r"关于对(.*?)采取",

        r"关于对(.*?)给予",

        r"关于对(.*?)作出",

        r"关于对(.*?)纪律处分"

    ]


    for pattern in patterns:


        result = re.search(
            pattern,
            title
        )


        if result:


            company = result.group(1)


            if "期货" in company:


                return company


            else:


                return company + "期货有限公司"



    return "未识别机构"





def fix_url(url):

    """
    补全链接
    """


    if not url:

        return ""


    if url.startswith("/"):

        return (
            "https://www.cfachina.org"
            +
            url
        )


    return url





def crawl_cfa():



    print("===================")

    print("开始抓取中国期货业协会")

    print("===================")



    response = requests.get(

        URL,

        headers=HEADERS,

        timeout=20

    )


    print(
        "状态码:",
        response.status_code
    )



    response.encoding="utf-8"



    soup = BeautifulSoup(

        response.text,

        "html.parser"

    )



    data=[]



    # 查找所有链接

    for a in soup.find_all("a"):



        title = a.text.strip()


        link = a.get("href")



        if not title:

            continue



        # 只抓处分、处罚、纪律相关

        keywords=[

            "纪律处分",

            "自律处分",

            "监管措施",

            "违规",

            "处罚"

        ]



        if any(
            k in title
            for k in keywords
        ):



            link = fix_url(link)



            company = extract_company(
                title
            )



            item={


                "company":

                    company,


                "source":

                    "中国期货业协会",


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

                    link

            }



            data.append(item)




    print(

        "抓取数量:",

        len(data)

    )



    return data





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







if __name__=="__main__":



    result = crawl_cfa()



    save_data(result)


    print(

        "中期协更新完成"

    )
