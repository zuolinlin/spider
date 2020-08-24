import json
import time

import scrapy
from scrapy import Request

from spider.spiders.DBMTSpider import DBMTSpider
from util import RandomUtil


class MtSpider(DBMTSpider):
    name = "meituan"
    allowed_domains = ["meituan.com"]
    # cid_list = [
    #     {"code": 76, "name": "美容美体", "serverId": "14"},
    #     {"code": 75, "name": "美甲美睫", "serverId": "15"},
    #     {"code": 20422, "name": "瘦身纤体", "serverId": "16"},
    #     {"code": 20419, "name": "韩式定装", "serverId": "17"},
    #     {"code": 20421, "name": "祛痘", "serverId": "18"},
    # ]

    cid_list = [
        {"code": 20421, "name": "祛痘", "serverId": "18"},
    ]

    start_url = "https://i.meituan.com/shenzhen/all/?cid={cid}&p={page}&cateType=poi"

    def start_requests(self):
        list = self.fetchall("SELECT * FROM `mrb_store`.`spider_source_project`  ")
        for data in list:
            print(data)
            url = data[12]
            fild = str(url).split("/")[4]

            print(fild)
            start_url = "https://i.meituan.com/poi/" + fild
            yield scrapy.Request(
                url=start_url,
                meta={
                    "fild": fild,
                    "serverId":18
                },
                callback=self.store_detail,
                dont_filter=True
            )

    def __init__(self, *a, **kw):
        super(MtSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def parse(self, response):

        data_list = response.xpath('//div[@id="deals"]/dl')
        # 下一页
        if len(data_list) > 0:
            page = response.meta.get("page") + 1
            response.meta.update({"page": page})
            yield Request(
                self.start_url.format(page=page, cid=response.meta.get("code")),
                meta=response.meta,
                dont_filter=True
            )
            time.sleep(1)
        print(data_list)
        print(response.meta.get('serverId'))
        if data_list is not None:
            for data in data_list:
                # 门店 详情页Url
                detail_url = "https:"+str(data.xpath("./dd/a/@href").extract_first())
                print(detail_url)
                yield Request(
                    url=detail_url,
                    meta={"serverId": response.meta.get('serverId')},
                    dont_filter=True,
                    callback=self.store_detail
                )
                time.sleep(1)

    # 门店详情页
    def store_detail(self, response):

        url = response.url
        out_id = str(url).split("/")[-1]
        # 美团对应门店的唯一标识，做数据库重插校验
        # 服务类别
        serverId = response.meta.get('serverId')
        # 门店logo
        store_logo = response.xpath('//*[@id="deal-list"]/div[3]/div[1]/@data-src').extract_first()
        # 门店名称
        store_name = response.xpath('//*[@id="deal-list"]/dl[1]/dd/dl/dd[1]/div/h1/text()').extract_first()
        # 门店星级
        store_star = response.xpath('//*[@id="deal-list"]/dl[1]/dd/dl/dd[1]/div/div/span[1]/span/em/text()').extract_first()
        # 门店地图的详情地址
        address = response.xpath(
            '//*[@id="deal-list"]/dl[1]/dd/dl/dd[2]/div/h6/a/@href').extract_first()

        # 获取门店的经纬度
        # 经度
        store_longitude = str(address).split("coord:")[1].split(";title")[0].split(",")[0]
        # 纬度
        store_latitude = str(address).split("coord:")[1].split(";title")[0].split(",")[1]
        #  具体地址，街道楼号门牌号
        store_specific_addr = response.xpath(
            '//*[@id="deal-list"]/dl[1]/dd/dl/dd[2]/div/h6/a/div/text()').extract_first()
        # 门店电话
        store_tel = response.xpath('//*[@id="deal-list"]/dl[1]/dd/dl/dd[2]/div/p/a/@data-tele').extract_first()

        # 营业时间
        try:
            business_time = response.xpath('//*[@id="poi-summary"]/dd/dl/dd[@class="dd-padding open-time kv-line"]/p/text()').extract_first()
            business_time = str(business_time).replace("\n", ' ')
            business_time_str = str(business_time).split(" ")
            lenth = len(business_time_str)
            business_time_1 = business_time_str[1]
            business_time_list = business_time_1.split("-")
            business_start_time = business_time_list[0]
            business_end_time = business_time_list[1]
            print("门店名称: " + store_name + " 门店logo: "+store_logo +
                  " 门店星级: " + store_star+" 经度: " + store_longitude +
                  " 纬度: " + store_latitude+" 具体地址，街道楼号门牌号: " +
                    store_specific_addr + " 门店电话: " + store_tel +
                   " 营业时间: " + business_time)
        except:
            business_start_time = "09:00"
            business_end_time = "22:00"
        # 获取门店下的项目数据
        store_project_list = response.xpath('//*[@id="deal-list"]/dl[2]/dd/dl//dd')
        if store_project_list is not None:
            for store_project in store_project_list:

                project_out_id = str(store_project.xpath("./a/div/@data-did").extract_first())
                stid = str(store_project.xpath("./a/@data-stid").extract_first())

                store_project_detail = "https://i.meituan.com/general/platform/mttgdetail/mtdealbasegn.json?dealid={dealid}&shopid={shopid}&eventpromochannel=&stid={stid}&lat=&lng="
                yield Request(
                    url=store_project_detail.format(dealid=project_out_id,shopid=out_id,stid=stid),
                    meta={"out_id": out_id,
                          "serverId": serverId,
                          "store_name": store_name,
                          "store_logo": store_logo,
                          "store_star": store_star,
                          "store_longitude": store_longitude,
                          "store_latitude": store_latitude,
                          "store_specific_addr": store_specific_addr,
                          "business_start_time": business_start_time,
                          "business_end_time": business_end_time,
                          "store_tel": store_tel,
                          "project_out_id": project_out_id
                          },
                    callback=self.store_project_detail
                )
        pass

    # 门店项目详情页
    def store_project_detail(self, response):
        store_out_id = response.meta.get('out_id')
        serverId = response.meta.get('serverId')
        store_name = response.meta.get('store_name')
        company_name = str(store_name).split("（")[0]
        store_logo = response.meta.get('store_logo')
        store_star = response.meta.get('store_star')
        store_longitude = response.meta.get('store_longitude')
        store_latitude = response.meta.get('store_latitude')
        store_specific_addr = response.meta.get('store_specific_addr')
        business_start_time = response.meta.get('business_start_time')
        business_end_time = response.meta.get('business_end_time')
        store_tel = response.meta.get('store_tel')
        settle_code = None
        if str(store_tel).__contains__("/"):
            store_tel = str(store_tel).split("/")[1]
        spider_settle = self.select_spider_settle_by_store_out_id(store_out_id)
        if spider_settle is None:
            #随机生成6位
            settle_code = RandomUtil.pwd();
            # 插入入驻公司数据 settle_code, company_name, company_addr, mobile, business_start_time, business_end_time, verify_state, is_delete
            self.insert_spider_settle(store_out_id,settle_code,company_name,store_specific_addr,store_tel,2,0)
        else:
            settle_code = spider_settle[2]
        # 插入门店数据    store_addr,specific_addr,company_name,logo,tel,star,business_start_time,business_end_time
        spider_store = self.select_spider_store_by_store_out_id(store_out_id)
        if spider_store is None:
            store_code = RandomUtil.pwd();
            self.insert_spider_store(store_out_id,settle_code, #out_id, settle_code,
                                     store_code,store_name,   #store_code, store_name,
                                     store_tel,0,         #  mobile, order_num,
                                     store_longitude,store_latitude, #longitude, latitude,
                                     store_specific_addr,store_specific_addr, #
                                     company_name,None,None,store_logo,
                                     store_tel,store_star,
                                     business_start_time,business_end_time,1,2,0)
        else:
            store_code = spider_store[3]
        # 项目Id
        project_out_id = response.meta.get('project_out_id')
        print(response.url)
        text = response.text
        #  获取详情页的json数据
        if text is not None:
            jsondata = json.loads(text)

            # 项目logo
            project_logo = jsondata['bigImgUrl']
            # 项目名称
            project_name = jsondata['brandName']
            # 项目副标题
            project_sub_title = jsondata['brandName']
            # 原价
            project_original_price = jsondata['originalPrice']
            # 最终价
            project_last_price = jsondata['price']
            # 销量
            project_sale_num = jsondata['solds']
            # 项目的文字详情
            project_structed_detailsm = jsondata['structedDetails'][2]['name']
            imgUrls = jsondata['imgUrls']
            bigImgUrl = jsondata['bigImgUrl']
            project = self.select_spider_project_by_store_out_id_project_out_id(store_out_id, project_out_id)
            if project is None:
                # 插入项目数据 self, out_id, settle_code, name, sub_title, original_price, last_price, sale_num, server_id, icon,state,del_state
                project_id = self.insert_spider_project(store_out_id,project_out_id, settle_code, project_name, project_sub_title,
                                                     project_original_price, project_last_price, project_sale_num, serverId,
                                                     project_logo, 2, 0)
                # 插入项目详情页数据
                if imgUrls is not None:
                    # 判断之前会否有正常插入
                    projectDetail = self.select_spider_project_detail_by_project_out_id( project_out_id)
                    if projectDetail is None:
                        self.insert_spider_project_detail(project_out_id,project_id,str(imgUrls))
                store_project = self.select_spider_store_project_by_store_out_id_project_out_id(store_out_id, project_out_id)
                if store_project is None:
                    # 插入项目与门店的关联表
                    self.insert_spider_store_project(store_code,project_id,store_out_id,project_out_id)
            else:
                store_project = self.select_spider_store_project_by_store_out_id_project_out_id(store_out_id,
                                                                                                project_out_id)
                # 插入项目详情页数据
                if imgUrls is not None:
                    # 判断之前会否有正常插入
                    projectDetail = self.select_spider_project_detail_by_project_out_id(project_out_id)
                    if projectDetail is None:
                        self.insert_spider_project_detail(project_out_id, project[0], str(imgUrls))
                if store_project is None:
                    # 插入项目与门店的关联表
                    self.insert_spider_store_project(store_code, project[2],store_out_id,project_out_id)
