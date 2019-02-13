from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request

class CompanyicprecordallfinalSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "companyicprecordallfinal"
    # 爬取的范围，防治爬虫爬到别的网站
    #allowed_domains = ["https://www.baidu.com/"]
    #  开始爬取的地址

    def __init__(self, *a, **kw):
        super(CompanyicprecordallfinalSpider, self).__init__(*a, **kw)

    def start_requests(self):
        webinfos = self.fetchall("SELECT * FROM `xsbbiz`.`company_icp_record_all_final` where `status` is null  limit 0,1000000 ")
        for webinfo in webinfos:
            id = webinfo[0]
            website = webinfo[17]
            if website is not None:
               website = "www." + website
            self.exec_sql("""
                         UPDATE 
                           `xsbbiz`.`company_icp_record_all_final`
                         SET
                          
                           `status` =%s

                         WHERE `id` = %s 
                             """, (

                0,
                id
            ))
            try:
                yield Request(
                    url=website,
                    meta={
                      "id": id,
                      "website": website
                    }
                )
            except:
                self.exec_sql("""
                         UPDATE
                           `xsbbiz`.`company_icp_record_all_final`
                         SET

                           `status` =%s

                         WHERE `id` = %s
                             """, (

                    0,
                    id
                ))
            print(webinfo)
            print("=========")

    def parse(self, response):
        id =response.meta['id']
        keywords =response.xpath('/html/head/meta[@name="keywords"]/@content').extract_first()
        description = response.xpath('/html/head/meta[@name="description"]/@content').extract_first()
        self.exec_sql("""
             UPDATE 
               `xsbbiz`.`company_icp_record_all_final`
             SET
               `keywords` =%s,
               `description` =%s,
               `status` =%s
               
             WHERE `id` = %s 
                 """, (
            keywords,
            description,
            1,
            id
        ))
        print("=====success======")

