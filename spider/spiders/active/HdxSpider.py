import time
from scrapy import Request
import urllib.parse
import uuid
from spider.spiders.active.ActiveSpider import ActiveSpider
from spider.spiders.BaseSpider import BaseSpider

"""
活动行 === 金融 创业 it互联网 医疗 科技

"""


class HdxSpider(ActiveSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "hdx_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["huodongxing.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['http://www.huodongxing.com']
    base_url = "http://www.huodongxing.com"
    start_urls = "http://www.huodongxing.com/events?orderby=o&channel=行业&tag={classify}&city=全部&isChannel=true&page={pageNo}"
    news_type_url_list =[
        {"name": "IT互联网"},
        {"name" : "创业"},
        {"name": "科技"},
        {"name": "金融"},
        {"name": "医疗"}
    ]
    # news_type_url_list = [
    #     {"code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=IT互联网&city=全部&isChannel=true&page=1",
    #      "name": "IT互联网"},
    #     {"code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=创业&city=全部&isChannel=true&page=1",
    #      "name": "创业"},
    #     {
    #         "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=科技&city=全部&isChannel=true&page=1",
    #         "name": "科技"},
    #     {
    #         "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=金融&city=全部8&isChannel=true&page=1",
    #         "name": "金融"},
    #     {
    #         "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=医疗&city=全部&isChannel=true&page=2",
    #         "name": "医疗"},
        # {
        #     "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=游戏&city=全部&isChannel=true&page=1",
        #     "name": "游戏"},
        # {
        #     "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=游戏&city=全部&isChannel=true&page=1",
        #     "name": "游戏"},
        # {
        #     "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=电商&city=全部&isChannel=true&page=1",
        #     "name": "电商"},
        # {
        #     "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=教育&city=全部&isChannel=true&page=1",
        #     "name": "教育"},
        # {
        #     "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=营销&city=全部&isChannel=true&page=1",
        #     "name": "营销"},
        # {
        #     "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=设计&city=全部&isChannel=true&page=1",
        #     "name": "设计"},
        #
        # {
        #     "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=地产&city=全部&isChannel=true&page=1",
        #     "name": "地产"},

        # {
        #     "code": "http://www.huodongxing.com/events?orderby=o&channel=行业&tag=服务业&city=全部&isChannel=true&page=1",
        #     "name": "服务业"},
   # ]
    photo_tag_url ="http://cdn.huodongxing.com/Content/v3.0/img/hdx/hdx-main-feature/admin-head/dujia.png"

    def __init__(self, *a, **kw):
        super(HdxSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for active_classify in self.news_type_url_list:
            yield Request(
                self.start_urls.format(classify=active_classify.get("name") ,pageNo=1),
                meta={
                    "classify": active_classify.get("name"),
                    "pageNo": "1"
                },
                dont_filter=True
            )

    def parse(self, response):
        data_list = response.xpath('//div[@class="search-tab-content-list-check flex"]/div[@class="search-tab-content-item-mesh"]')
        if data_list is not None:
            for data in data_list:
               xy = data.xpath('./a/div[@class="item-mesh-conter"]/div/img/@src').extract_first()
               if xy is None or xy == self.photo_tag_url:
                  title = data.xpath('./a/img/@alt').extract_first()
                  times = data.xpath('./a/div[@class="item-mesh-conter"]/p[@class="date-pp"]//text()').extract()
                  new_time = times[0] + times[1]
                  # if times is not None and len(times) !=0:
                  #     new_tinme = times[0]+times[1]
                  #
                  #     month = str(new_tinme)[0:2]
                  #     if int(month) >5 and int(month)<=12:
                  #         times = "2018年"+new_tinme
                  #     else:
                  #         times = "2019年" + new_tinme
                  #     times = str(times).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
                  place = data.xpath('.//div[@class="item-dress flex"]/p[@class="item-dress-pp"]/text()').extract_first()
                  tags_data = data.xpath('./a/div[@class="item-mesh-bottom flex"]/div[@class="item-bottom-left flex"]/div[@class="tag-list flex"]//p//span/text()').extract()
                  tags=""
                  if tags_data is not None and len(tags_data) != 0:
                      for i, tag in enumerate(tags_data):
                          tags += tag
                          if i != len(tags_data) - 1:
                              tags = tags + "、"
                  url = response.url
                  url= urllib.parse.unquote(url)
                  classify = str(url)[55:].split("&city")[0][4:]
                  link = data.xpath('./a/@href').extract_first()
                  link = self.base_url +link
                  link = urllib.parse.unquote(link)
                  source = "活动行"
                  yield Request(
                      link,
                      meta={
                          "title": title,
                          "place": place,
                          "tags":  tags,
                          "classify": classify,
                          "link": link,
                          "new_time": new_time
                      },
                      callback=self.detail
                  )

        num = response.meta['pageNo']
        classify = response.meta['classify']
        next_num = int(num) + 1
        if next_num <= 200:
            next_url = self.start_urls.format(classify=classify,pageNo=str(next_num))
            next_url = urllib.parse.unquote(next_url)
            yield Request(next_url,
                          dont_filter=True,
                          meta={
                              "classify": response.meta['classify'],
                              "pageNo": str(next_num)
                          },
                          callback=self.parse)
        else:
            return

    def detail(self, response):
          new_time = response.meta['new_time']
          try:
              sponsor = response.xpath('//div[@title="活动发起人"]/a/text()').get().strip()
              times = response.xpath('//div[@class="address-info-wrap"]/div/text()').get().strip()
              times = str(times).split("～")[0]
              times = times.split(",")[2].split(" ")[1]
              new_time = response.meta['new_time']
              times = times+"年"+new_time
              times = str(times).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
          except:
              response.xpath('//div[@class="event-details-lite-meta"]/text()[1]')
              times ="2018年" + new_time
              times = str(times).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
          title= response.meta['title']
          place = response.meta['place']
          tags = response.meta['tags']
          classify = response.meta['classify']
          link = response.meta['link']
          source = "活动行"

          # 插入sql
          pojo = self.fetchone(
              "SELECT 1 FROM `financial_activities` WHERE `link`='%s' AND `source`='%s' " % (link, source))
          if pojo is None:
              self.insert_new(
                  title,
                  times,
                  place,
                  tags,
                  classify,
                  link,
                  source,
                  sponsor
              )


