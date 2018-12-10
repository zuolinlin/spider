# -*- coding: utf-8 -*-
import json

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class JiQiZhiXinSpider(NewsSpider):
    """
    机器之心
    """
    custom_settings = {
        # "AUTOTHROTTLE_ENABLED": True,
        # "DOWNLOAD_DELAY": 1
    }

    name = "jiqizhixin_news"

    domain = "https://www.jiqizhixin.com"

    list_url = "https://www.jiqizhixin.com/graphql"

    data = {"operationName": "timelineInHome",
            "variables": {"cursor": "", "count": 10, "category": "all", "type": "everyone"},
            "query": "query timelineInHome($category: String!, $type: String!, $count: Int, $cursor: String) {\n  "
                     "timelines(category: $category, type: $type, first: $count, after: $cursor) {\n    ...Timeline\n "
                     "   __typename\n  }\n}\n\nfragment Timeline on TimelineConnection {\n  edges {\n    node {\n     "
                     " id\n      content_type\n      content {\n        ... on Article {\n          ...ArticleInfo\n  "
                     "        __typename\n        }\n        ... on Report {\n          ...ReportItem\n          "
                     "__typename\n        }\n        ... on Topic {\n          ...TopicItem\n          __typename\n   "
                     "     }\n        ... on Periodical {\n          title\n          cover_image_url\n          "
                     "path\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n   "
                     " __typename\n  }\n  pageInfo {\n    ...PageInfo\n    __typename\n  }\n  "
                     "__typename\n}\n\nfragment PageInfo on PageInfo {\n  endCursor\n  hasNextPage\n  "
                     "__typename\n}\n\nfragment TopicItem on Topic {\n  id\n  title\n  path\n  category\n  "
                     "likes_count\n  comments_count\n  cover_image_url\n  author {\n    id\n    name\n    path\n    "
                     "__typename\n  }\n  __typename\n}\n\nfragment ArticleInfo on Article {\n  ...ArticleSimple\n  "
                     "category_name\n  category_path\n  author {\n    name\n    id\n    avatar_url\n    path\n    "
                     "__typename\n  }\n  __typename\n}\n\nfragment ArticleSimple on Article {\n  id\n  path\n  "
                     "title\n  cover_image_url\n  published_at\n  likes_count\n  comments_count\n  description\n  "
                     "__typename\n}\n\nfragment ReportItem on Report {\n  id\n  title\n  description\n  likes_count\n "
                     " comments_count\n  path\n  created_at\n  __typename\n}\n"}

    def __init__(self, *a, **kw):
        super(JiQiZhiXinSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.domain,
            dont_filter=True
        )

    def parse(self, response):
        if self.domain.__eq__(response.url):
            items = response.xpath('//div[@class="u-block__item js-u-item is-active"]/article')
            for item in items:
                yield Request(
                    self.domain + item.xpath('main/section/a/@href').extract_first(),
                    meta={
                        "title": item.xpath('normalize-space(main/section/a/text())').extract_first(),
                        "digest": item.xpath('normalize-space(main/section/p/text())').extract_first(),
                        "source": item.xpath('normalize-space(main/footer/div[1]/a[2]/text())').extract_first(),
                        "push_date": item.xpath('main/footer/div[1]/span/time/text()').extract_first(),
                        "new_type": item.xpath('main/footer/div[2]/a/text()').extract_first(),
                    },
                    dont_filter=True,
                    priority=1,
                    callback=self.detail
                )
            data = json.loads(response.xpath('//div[@class="u-block__item js-u-item is-active"]/div[last('
                                             ')]/@data-react-props').extract_first())
            cursor = data.get("cursor")
            self.data.update({"variables": {"cursor": cursor, "count": 10, "category": "all", "type": "everyone"}})
            yield Request(
                self.list_url,
                method="POST",
                body=json.dumps(self.data),
                headers={
                    'content-type': 'application/json',
                    "X-CSRF-Token":  response.xpath("/html/head/meta[@name='csrf-token']/@content").extract_first()
                },
                dont_filter=True,
                callback=self.parse
            )
        else:
            data = json.loads(response.body)
            data = data.get("data", {}).get("timelines", {})
            edges = data.get("edges")
            for edge in edges:
                content = edge.get("node", {}).get("content", {})
                yield Request(
                    self.domain + content.get("path"),
                    meta={
                        "title": content.get("title"),
                        "digest": content.get("description"),
                        "source": content.get("author", {}).get("name"),
                        "push_date": content.get("published_at"),
                        "new_type": content.get("category_name"),
                    },
                    dont_filter=True,
                    priority=1,
                    callback=self.detail
                )
            # 分页
            page_info = data.get("pageInfo")
            if page_info.get("hasNextPage"):
                cursor = page_info.get("endCursor")
                self.data.update({"variables": {"cursor": cursor, "count": 10, "category": "all", "type": "everyone"}})
                yield Request(
                    self.list_url,
                    method="POST",
                    body=json.dumps(self.data),
                    headers={
                        'content-type': 'application/json',
                        "X-CSRF-Token":  response.request.headers.get("X-CSRF-Token")
                    },
                    dont_filter=True,
                    callback=self.parse
                )

    def detail(self, response):
        self.insert_new(
            RegExUtil.find_first("jiqizhixin.com/(.+)", response.url),
            response.meta.get("push_date"),
            response.meta.get("title"),
            response.meta.get("new_type"),
            response.meta.get("source"),
            response.meta.get("digest"),
            response.xpath('//*[@id="js-article-content"]'),
            response.url,
            48
        )
