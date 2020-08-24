import scrapy

from spider.spiders.active.ActiveSpider import ActiveSpider
from scrapy import Request
"""
陆想汇====金融活动
"""


class LjzforumSpider(ActiveSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "ljzforum_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["ljzforum.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://www.ljzforum.com/activity/query.do'

    base_url = "https://www.ljzforum.com/activity/{detail_no}.html"

    active_types = [
        {"name": "宏观分析", "value": "1"},
        {"name": "行业峰会", "value": "3"},
        {"name": "金融科技", "value": "2"},
        {"name": "资本市场", "value": "4"},
        {"name": "路演调研", "value": "5"},
        {"name": "金融培训", "value": "6"},
        {"name": "创业投资", "value": "7"},
        {"name": "金融生活", "value": "8"},
        {"name": "其它", "value": "9"},
        {"name": "期货外汇", "value": "10"},
        {"name": "直播活动", "value": "11"}

    ]

    def __init__(self, *a, **kw):
        super(LjzforumSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for active_type in self.active_types:
            yield scrapy.FormRequest(
                url=self.start_urls,
                formdata={
                          "limitStart": "1",
                          "limitEnd": "20",
                          "categoryId": active_type['value']},
                meta={
                    "categoryId": active_type['value'],
                    "categoryName": active_type['name'],
                    "limitStart": 0
                },

                callback=self.parse
            )

    def parse(self, response):
        data_list = response.xpath('//div[@class="activity_item"]')
        if data_list is not None:
            for data in data_list:
                title = data.xpath('./div[@class="activity_cont"]/div[@class="activity_title"]/text()').extract_first()
                detail = data.xpath('./@onclick').extract_first()
                detail_no = str(detail)[15:-1]
                detail_url = self.base_url.format(detail_no=detail_no)
                times = data.xpath('//div[@class="activity_cont"]/div[@class="activity_info"][1]/span/text()').get().strip()
                times = str(times).split(" -")[0]
                if times is not None:
                    suffer =times[0:2]
                    if str(suffer) != "20":
                        times = "2018/" +times
                        times = str(times).replace(r'/', '-').replace(r'/', '-').replace(r'/', ' ')
                    else:
                        times = str(times).replace(r'/', '-').replace(r'/', '-').replace(r'/', ' ')
                place = data.xpath('//div[@class="activity_cont"]/div[@class="activity_info"][2]/span/text()').extract_first()
                tags_data = data.xpath('./div[@class="activity_cont"]/div[@class="activity_tags"]/span/text()').extract()
                source = "陆想汇"
                classify = response.meta['categoryName']
                tags = ""
                if tags_data is not None and len(tags_data) != 0:
                    for i, tag in enumerate(tags_data):
                        tags += tag
                        if i != len(tags_data) - 1:
                            tags = tags + "、"
                self.insert_new(
                    title,
                    times,
                    place,
                    tags,
                    classify,
                    detail_url,
                    source
                )

            yield scrapy.FormRequest(
                url=self.start_urls,
                formdata={
                    "limitStart": str(int(response.meta["limitStart"])+20),
                    "limitEnd": "20",
                    "categoryId": response.meta['categoryId']},
                meta={
                    "limitStart": str(int(response.meta["limitStart"])+20),
                    "categoryName": response.meta['categoryName'],
                    "categoryId": response.meta['categoryId']
                },
                callback=self.parse
            )
