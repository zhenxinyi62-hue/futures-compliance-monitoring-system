import requests
import re


URL = "https://www.cfachina.org/informationpublicity/discipline/"


HEADERS = {
    "User-Agent":
    "Mozilla/5.0"
}



def main():

    r = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )


    r.encoding="utf-8"

    html=r.text


    print(
        "长度:",
        len(html)
    )


    print("===================")
    print("查找 script")
    print("===================")


    scripts=re.findall(

        r"<script.*?>(.*?)</script>",

        html,

        re.S

    )


    print(
        "内嵌script数量:",
        len(scripts)
    )


    for i,s in enumerate(scripts):


        if any(

            x in s.lower()

            for x in [

                "ajax",
                "url",
                "list",
                "page",
                "json",
                "data"

            ]

        ):


            print("===================")

            print(
                "SCRIPT:",
                i
            )

            print(
                s[:2000]
            )





if __name__=="__main__":

    main()
