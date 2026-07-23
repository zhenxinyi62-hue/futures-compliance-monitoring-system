import requests
import re


BASE = "https://www.cfachina.org"


URL = (
    BASE +
    "/informationpublicity/discipline/"
)


HEADERS = {
    "User-Agent":
    "Mozilla/5.0"
}



def get(url):

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    r.encoding="utf-8"

    return r.text




def scan(text,name):

    print("===================")
    print(name)
    print("===================")


    keywords=[

        "ajax",

        "$.get",

        "$.post",

        "url",

        "list",

        "json",

        "page",

        "data",

        "discipline",

        "information"

    ]


    for k in keywords:

        if k.lower() in text.lower():

            print(
                "发现:",
                k
            )




def main():


    html=get(URL)


    print(
        "HTML:",
        len(html)
    )


    # 找JS

    js=re.findall(

        r'<script.*?src="(.*?)"',

        html

    )


    print(
        "JS数量:",
        len(js)
    )



    for item in js:


        if not item.startswith("http"):

            item=BASE+item



        print(
            "检查:",
            item
        )



        try:

            js_text=get(item)


            scan(
                js_text,
                item
            )


            # 保存

            filename=item.split("/")[-1]

            with open(

                "js_"+filename,

                "w",

                encoding="utf-8"

            ) as f:

                f.write(js_text)


        except Exception as e:

            print(e)





if __name__=="__main__":

    main()
