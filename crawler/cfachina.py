import requests
import json
import os
import re
from datetime import datetime


BASE_URL = "https://www.cfachina.org"

API_URL = (
    BASE_URL +
    "/qx-search/api/wcmSearch/searchDocsByProgram"
)


HEADERS = {

    "User-Agent":
    "Mozilla/5.0",

    "Referer":
    "https://www.cfachina.org/informationpublicity/discipline/"

}



def fix_url(url):

    if not url:
        return ""

    if url.startswith("http"):

        return url


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

        m = re.search(
            p,
            title
        )

        if m:

            return m.group(1)



    return "未识别机构"






def crawl_cfa():


    print("===================")
    print("开始抓取中期协纪律处分")
    print("===================")


    data=[]


    page=1



    while True:


        params={

            "pageNo":
                page,

            "pageSize":
                15,

            "keyword":
                "",

            "programName":
                "纪律处分"

        }



        r=requests.get(

            API_URL,

            headers=HEADERS,

            params=params,

            timeout=30

        )



        print(
            "请求页:",
            page,
            "状态:",
            r.status_code
        )



        obj=r.json()



        result=obj.get(
            "data",
            {}
        )



        docs=result.get(
            "dataList",
            []
        )



        if not docs:

            break



        for item in docs:


            title=item.get(
                "docTitle",
                ""
            )


            url=item.get(
                "docPubUrl",
                ""
            )


            date=item.get(
                "docRelTime",
                ""
            )



            company=extract_company(
                title
            )



            data.append({


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

                    date,


                "url":

                    fix_url(url)

            })



        total=result.get(
            "total",
            0
        )


        print(
            "累计:",
            len(data),
            "/",
            total
        )


        if len(data)>=total:

            break


        page+=1



    print("===================")

    print(
        "抓取数量:",
        len(data)
    )

    print("===================")


    return data






def save_data(data):


    os.makedirs(

        "data",

        exist_ok=True

    )


    path="data/compliance_cases.json"



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
        "保存:",
        path
    )






if __name__=="__main__":


    result=crawl_cfa()


    save_data(result)


    print(
        "中期协更新完成"
    )
