import json
import jsonpath
import scrapy
from scrapy.http.response.html import HtmlResponse
from spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from util.XPathUtil import str_to_selector
from spider.spiders.news.NewsSpider import NewsSpider

# 动点科技 ---科技快讯页面
class TechnodeKjkxSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "technode_kjkx"
    allowed_domains = ["cn.technode.com"]
    # 科技快讯
    start_urls = ["http://news.hexun.com/financial/"

    ]

    def __init__(self, *a, **kw):
        super(TechnodeKjkxSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def start_requests(self):

        url = "https://cn.technode.com/wp-admin/admin-ajax.php"
        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.FormRequest(
            url=url,
            formdata={"action": "td_ajax_block",
                      "td_atts":
                          '{"limit":"9","ajax_pagination":"load_more","installed_post_types":"newsnow","custom_title":"科技快讯"}',
                      "td_block_id":"td_uid_1_5bf280d9209d1",
                      "td_column_number": "3",
                      "td_current_page": "1",
                      "block_type": "8"},


            callback=self.parse
        )

    def parse(self, response):
        body = response.body
        if not body:
            return
        else:
            datas = json.loads(body)
            data = datas.get("td_data")
            try:
                html_str = str_to_selector(data)
            except:
                html_str = None
            if html_str is not None:
                # 解析数据
                new_list = html_str.xpath('//div[@class="wpb_row row-fluid"]/div[@class="span4"]')
                for new in new_list:
                    #  新闻详情页URl
                    url = new.xpath('.//div[@class="td_mod5 td_mod_wrap "]/div/a/@href').get().strip()
                    # 摘要
                    # content = new.xpath('.//div[@class="td_mod5 td_mod_wrap "]').get().strip()
                    yield Request(
                        url,
                        # meta={"content": content},
                        callback=self.detail
                    )
            self.current_page += 1
            yield scrapy.FormRequest(
                url="https://cn.technode.com/wp-admin/admin-ajax.php",
                formdata={"action": "td_ajax_block",
                          "td_atts":
                              '{"limit":"9","ajax_pagination":"load_more","installed_post_types":"newsnow","custom_title":"科技快讯"}',
                          "td_block_id":"td_uid_1_5bf280d9209d1",
                          "td_column_number": "3",
                          "td_current_page": str(self.current_page),
                          "block_type": "8"},

                callback=self.parse
            )

    #
    def detail(self, response):
        # 外部编号
        url = response.url
        splits = str(url).split('/')
        out_id = splits[4] + splits[5]
        # 标题
        title = response.xpath('//h1[@class="entry-title"]/text()').get().strip()
        # 时间
        push_time = response.xpath('//time[@itemprop="dateCreated"]/text()').get().strip()
        # 新闻类型
        new_type = "科技快讯"
        # 来源
        source = "动点科技"
        #  摘要
        #digest = response.meta['content']
        # 内容
        content = response.xpath('//article/p').extract()
        content = "".join(content)
        digest = content.split('。')[0][7:]
        # 爬取来源
        spider_source = 3
        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            digest,
            content,
            response.url,
            spider_source
        )
        pass



