from dyly_spider.spiders.active.ActiveSpider import ActiveSpider

"""
融资中国  =会议
"""


class ThecapitalSpider(ActiveSpider):

    name = "thecapital_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["thecapital.com.cn"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['http://www.thecapital.com.cn/Meeting/index.html']
    base_url = "http://www.thecapital.com.cn"

    def __init__(self, *a, **kw):
        super(ThecapitalSpider, self).__init__(*a, **kw)

    def parse(self, response):
        # 最新的会议
        new_data_list = response.xpath('//div[@class="zxhy clear-fix"]/dl')
        if new_data_list is not None:
            for data in new_data_list:
                title = data.xpath('./dd/div[@class="txt"]/a/text()').extract_first()
                link = data.xpath('./dd/div[@class="txt"]/a/@href').extract_first()
                source = "融资中国"
                place = data.xpath('./dd/div[@class="add"]/text()').extract_first()
                times = data.xpath('./dd/div[@class="tim"]/text()').extract_first()
                times = str(times).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
                classify = "会议"
                self.insert_new(
                    title,
                    times,
                    place,
                    None,
                    classify,
                    link,
                    source
                )

                # 往期的会议
        data_list = response.xpath('//div[@class="son"]')
        if data_list is not None:
            for da in data_list:
                link = da.xpath('./dt/a/@href').extract_first()
                link = self.base_url + link
                title = da.xpath('./dt/a/text()').extract_first()
                place = da.xpath('./dd/p/text()[1]').extract_first()
                times = da.xpath('./dd/p[2]/text()').extract_first()
                times = str(times).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
                classify = "会议"
                self.insert_new(
                    title,
                    times,
                    place,
                    None,
                    classify,
                    link,
                    source
                )



