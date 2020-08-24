import datetime
from scrapy import Request
from spider.spiders.news.NewsSpider import NewsSpider


class IfenxiSpider(NewsSpider):
    """
    爱分析访谈栏目
    """
    name = "ifenxi_news"
    allowed_domains = ['ifenxi.com']

    # 爱分析访谈栏目5、6页新闻
    #start_urls = ['http://ifenxi.com/archives/category/interview/page/{n}'.format(n=n) for n in range(5,7)]

    # 爱分析首页，可爬取爱分析所有栏目新闻,当前爬取的是第一页的新闻
    start_urls = ['http://ifenxi.com/page/{n}'.format(n=n) for n in range(1,2)]

    def start_requests(self):
        print('开始')
        for start_url in self.start_urls:
            print('---->',start_url)
            yield Request(
                start_url,
                callback=self.parse
            )

    def __init__(self, *a, **kw):
        super(IfenxiSpider, self).__init__(*a, **kw)

    def parse(self, response):
        """
        爱分析访谈列表
        :param response:
        :return:
        """
        data_list = response.xpath("//div[@class='ajax-load-box posts-con']//div[@class='content-box']/div[@class='posts-default-box']")
        for data in data_list:
            detailurl = str(data.xpath("./div[@class='posts-default-title']/h2/a/@href").extract_first())
            title = data.xpath("./div[@class='posts-default-title']/h2/a/@title").extract_first()
            digest = data.xpath("./div[@class='posts-default-content']/div[@class='posts-text']/text()").extract_first()

            strs = str(detailurl).split('/')
            out_id = strs[-1]

            new_type = data.xpath("./div[@class='posts-default-content']/div[@class='posts-default-info']/ul/li[@class='ico-cat']/a/text()").extract_first()
            push_date = data.xpath("./div[@class='posts-default-content']/div[@class='posts-default-info']/ul/li[@class='ico-time']/text()").extract_first()

            ti = push_date[-2:]
            if ti == "时前":
                houses = push_date[0:-3]
                push_date = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime(
                    "%Y-%m-%d %H:%M")
            elif ti == "天前":
                days = push_date[0:-2]
                push_date = (datetime.datetime.now() - datetime.timedelta(days=int(days))).strftime("%Y-%m-%d %H:%M")
            elif ti == "钟前":
                minute = push_date[0:-3]
                push_date = (datetime.datetime.now() - datetime.timedelta(minutes=int(minute))).strftime(
                    "%Y-%m-%d %H:%M")
            elif ti == "周前":
                print(".....")
            else:
                push_date = push_date

            yield Request(
                url=detailurl,
                meta={"out_id": out_id,
                      "push_date": push_date,
                      "title": title,
                      "new_type": new_type,
                      "digest": digest
                      },
                callback=self.detail
            )

    def detail(self,response):
        out_id = response.meta['out_id']

        push_date = response.meta['push_date']

        title = response.meta['title']
        new_type = response.meta['new_type']
        source = '爱分析'
        digest = response.meta['digest']
        content = response.xpath("/html/body").extract_first()
        source_url = response.url
        spider_source = 47

        #print(out_id, push_date, title, new_type, source, digest, source_url, spider_source)
        #print(push_date)
        #print(type(push_date))

        self.insert_new(
            out_id,
            push_date,
            title,
            new_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )
