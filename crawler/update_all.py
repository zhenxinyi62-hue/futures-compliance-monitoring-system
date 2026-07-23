from cfachina import crawl_cfachina
from shfe import crawl_shfe


all_data = []


# 中期协
all_data.extend(
    crawl_cfachina()
)


# 上海期货交易所
all_data.extend(
    crawl_shfe()
)


with open(
    "data/announcements.json",
    "w",
    encoding="utf-8"
) as f:

    import json

    json.dump(
        all_data,
        f,
        ensure_ascii=False,
        indent=4
    )


print(
    "全部更新完成"
)
