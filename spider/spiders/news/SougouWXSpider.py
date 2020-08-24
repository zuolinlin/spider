# # -*- coding: utf-8 -*-
# import logging
# import time
# from urllib.parse import urljoin
#
# import js2xml
# from lxml import etree
# from pydispatch import dispatcher
# from scrapy import Request, signals
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
#
# from spider.spiders.news.NewsSpider import NewsSpider
#
#
# # 搜狗-微信文章
# class SougouWXSpider(NewsSpider):
#     name = "sougou_weixin"
#     allowed_domains = ["sogou.com", "qq.com"]
#     start_url = "https://weixin.sogou.com/weixin?query={}&type=1"
#
#     custom_settings = {
#         "LOG_LEVEL": logging.INFO,
#         "DOWNLOAD_DELAY": 3,
#     }
#
#     wechat_list = []
#
#     def __init__(self, *a, **kw):
#         super(SougouWXSpider, self).__init__(*a, **kw)
#         self.chrome_options = Options()
#         #  设置浏览器是否隐藏
#         # self.chrome_options.add_argument('--headless')
#         # self.chrome_options.add_argument('--disable-gpu')
#         self.browser = webdriver.Chrome(executable_path=r'spider/file/chromedriver',
#                                         chrome_options=self.chrome_options)
#         # chrome_options = webdriver.ChromeOptions()
#         # # 不打开浏览器窗口
#         # chrome_options.add_argument('headless')
#         # chrome_options.add_argument('no-sandbox')
#         # self.browser = webdriver.Chrome(executable_path=r'spider/file/chromedriver',
#         #                                 chrome_options=chrome_options)
#         # 传递信息,也就是当爬虫关闭时scrapy会发出一个spider_closed的信息,当这个信号发出时就调用closeSpider函数关闭这个浏览器.
#         dispatcher.connect(self.spider_closed, signals.spider_closed)
#         with open(r'spider/file/wechat.txt', mode='r', encoding='utf-8') as f:
#             for line in f:
#                 if len(line) > 0:
#                     self.wechat_list.append(line)
#
#     def start_requests(self):
#         # 查找公众号
#         for wechat in self.wechat_list:
#             name = wechat.split()
#             if len(name) > 1:
#                 yield Request(
#                     self.start_url.format(name[1]),
#                     meta={"selenium": True},
#                     dont_filter=True,
#                 )
#             else:
#                 yield Request(
#                     self.start_url.format(name[0]),
#                     meta={"selenium": True},
#                     dont_filter=True,
#                 )
#
#     def parse(self, response):
#         # 默认取第一个
#         gzh = response.xpath("//ul[@class='news-list2']/li[1]")
#         news_url = gzh.xpath("./div/div[@class='txt-box']/p[@class='tit']/a/@href").extract_first()
#         gzh_img = gzh.xpath("./div/div[@class='img-box']/a/img/@src").extract_first()
#         gzh_name = gzh.xpath("./div/div[@class='txt-box']/p[@class='tit']/a/text()").extract_first()
#         gzh_weixinhao = gzh.xpath("./div/div[@class='txt-box']/p[@class='info']/label/text()").extract_first()
#         # 获取文章列表
#         yield Request(news_url, meta={"selenium": True}, callback=self.parse_news_list)
#
#     def parse_news_list(self, response):
#         verify_img_url = response.xpath("//img[@id='verify_img']/@src").extract_first()
#         if len(verify_img_url) > 0:
#             verify_img_url = urljoin(response.url, verify_img_url)
#
#
#         src = response.xpath("/html/body/script[8]/text()").extract_first()
#         # 解析script
#         src_text = js2xml.parse(src, debug=False)
#         src_tree = js2xml.pretty_print(src_text)
#         # print(src_tree)
#         selector = etree.HTML(src_tree)
#         source = selector.xpath("//var[@name='name']/binaryoperation/left/string/text()")[0]
#         msg_list = selector.xpath("//property[@name='list']/array/object")
#         for msg in msg_list:
#             push_date = msg.xpath("./property[@name='comm_msg_info']/object/property[@name='datetime']/number/@value")[
#                 0]
#             push_date = time.localtime(int(push_date))
#             # 头条的消息
#             out_id = msg.xpath("./property[@name='app_msg_ext_info']/object/property[@name='fileid']/number/@value")[0]
#             title = msg.xpath("./property[@name='app_msg_ext_info']/object/property[@name='title']/string/text()")[0] \
#                 .replace("\n", "")
#             digest = msg.xpath("./property[@name='app_msg_ext_info']/object/property[@name='digest']/string/text()")[0]
#             # 新闻地址
#             msg_url = msg.xpath(
#                 "./property[@name='app_msg_ext_info']/object/property[@name='content_url']/string/text()")[0]
#             msg_url = msg_url.replace('&amp;', '&')
#             msg_url = urljoin(response.url, msg_url)
#             # print(msg_url)
#             Request(msg_url,
#                     callback=self.parse_detail,
#                     meta={'out_id': out_id,
#                           'push_date': push_date,
#                           'title': title,
#                           'source': source,
#                           'digest': digest}
#                     )
#             # 次条的消息
#             msg_item_list = msg.xpath("//property[@name='multi_app_msg_item_list']/array/object")
#             for msg_item in msg_item_list:
#                 out_id = msg_item.xpath("./property[@name='fileid']/number/@value")[0]
#                 title = msg_item.xpath("./property[@name='title']/string/text()")[0].replace("\n", "")
#                 digest = msg_item.xpath("./property[@name='digest']/string/text()")[0]
#                 # 新闻地址
#                 msg_url = msg_item.xpath("./property[@name='content_url']/string/text()")[0]
#                 msg_url = msg_url.replace('&amp;', '&')
#                 msg_url = urljoin(response.url, msg_url)
#                 # print(msg_url)
#                 yield Request(msg_url,
#                               callback=self.parse_detail,
#                               meta={'out_id': out_id,
#                                     'push_date': push_date,
#                                     'title': title,
#                                     'source': source,
#                                     'digest': digest}
#                               )
#
#     def parse_detail(self, response):
#         if "qq.com" in response.url:
#             content = response.xpath("//div[@class='rich_media_content ']").extract_first()
#             # print(content)
#             self.insert_new(
#                 response.meta['out_id'],
#                 response.meta['push_date'],
#                 response.meta['title'],
#                 None,
#                 response.meta['source'],
#                 response.meta['digest'],
#                 content,
#                 response.url,
#                 1001
#             )
#
#     def spider_closed(self):
#         self.log("spider closed")
#         # 当爬虫退出的时关闭浏览器
#         self.browser.quit()
