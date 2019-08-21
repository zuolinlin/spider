from dyly_spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
import json

class KRSpider(NewsSpider):
    start_urls = ["https://36kr.com/information/web_news"]
    name = "36kr_news"
    allowed_domains = ["36kr.com"]

    def start_requests(self):
        url = "https://36kr.com/pp/api/aggregation-entity?type=web_latest_article&per_page=30"
        yield Request(
            url=url,
            callback=self.parse
        )

    def __init__(self, *a, **kw):
        super(KRSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def parse(self, response):
        self.current_page += 1;
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            data = jsondata["data"]
            items = data['items']
            next_last_id = items[len(items) - 1]['id']
            print(next_last_id)
            for item in items:
                id =item['id']
                entity_id= item['entity_id']
                published_at = item['post']['published_at']
                summary = item['post']['summary']
                herf = "https://36kr.com/p/" + str(entity_id)
                print(item)
                yield Request(
                    url=herf,
                    meta={"id": id,
                          "entity_id": entity_id,
                          "published_at": published_at,
                          "summary": summary},
                    callback=self.detail
                )
            next_url = "https://36kr.com/pp/api/aggregation-entity?type=web_latest_article&b_id="+str(next_last_id)+"&per_page=30"
            if self.current_page <5:
                yield Request(
                    next_url,
                    callback=self.parse
                )

    def detail(self, response):
        #out_id =response.meta.get('id')
        summary = response.meta.get('summary')
        entity_id = response.meta.get('entity_id')
        published_at = response.meta.get('published_at')
        title =response.xpath('//h1[@class="article-title margin-bottom-20 common-width"]/text()').extract_first(),
        content = response.xpath("//div[@class='common-width content articleDetailContent kr-rich-text-wrapper']").extract_first(),

        new_type = "最新",
        # self.insert_new(
        #     response.meta.get('id'),
        #     published_at,
        #     title,
        #     new_type,
        #     "36氪",
        #     summary,
        #     content,
        #     response.url,
        #     "2"
        # )

        self.insert_new(
            response.meta.get('id'),
            published_at,
            title,
            new_type,
            "36氪",
            summary,
            content,
            response.url,
            "2"
        )
        print(content)
        print(entity_id)
        pass

