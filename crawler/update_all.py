from shfe import crawl_shfe


data=[]

data.extend(
    crawl_shfe()
)


import json


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
