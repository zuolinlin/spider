# -*- coding: utf-8 -*-
from scrapy import Request
from spider.spiders.BaseSpider import BaseSpider


# 投资人物
class RoboReportPdfSpider(BaseSpider):

    # 自定义配置
    custom_settings = {
    }

    name = "robo_report_pdf"

    def __init__(self, *a, **kw):
        super(RoboReportPdfSpider, self).__init__(*a, **kw)

    def start_requests(self):
        current_page = 1
        result = self.query_list_page(current_page)
        pages = result.get("pages")
        while current_page <= pages:
            result = self.query_list_page(current_page)
            for row in result.get("rows"):
                report_id = row[0]
                yield Request(
                    row[1],
                    dont_filter=True,
                    meta={"report_id": report_id}
                )
            current_page = current_page + 1

    def parse(self, response):
        report_id = response.meta["report_id"]
        size = round(len(response.body)/1024, 2)
        self.execute("""
                UPDATE 
                  `robo_report` 
                SET
                  `size` = %s
                WHERE `report_id` = %s
        """, (
            size,
            report_id
        ))

    def query_list_page(self, page_no=1):
        return self.select_rows_paper(
            sql="SELECT `report_id`,`pdf` FROM `robo_report` WHERE `pdf` IS NOT NULL AND size IS NULL",
            page_no=page_no,
            page_size=20
        )

