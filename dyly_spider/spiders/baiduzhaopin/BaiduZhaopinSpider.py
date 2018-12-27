import logging
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

from dyly_spider.items import BaiduZhaopinItem
from dyly_spider.spiders.BaseSpider import BaseSpider
from util import cy_logger as logger


# 百度招聘
class BaiduZhaopinSpider(BaseSpider):
    name = "baidu_zhaopin"
    allowed_domains = ["baidu.com"]
    company_url = "https://zhaopin.baidu.com/quanzhi?query={}"

    # 自定义设置
    custom_settings = {
        "LOG_LEVEL": logging.INFO,
        "DOWNLOAD_DELAY": 1,
        'ITEM_PIPELINES': {
            'dyly_spider.pipelines.BaiduZhaopinSpiderPipeline': 100,
        },
    }

    def __init__(self, *a, **kw):
        super(BaiduZhaopinSpider, self).__init__(*a, **kw)
        self.chrome_options = Options()
        #  不打开浏览器窗口
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.browser = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
                                        chrome_options=self.chrome_options)
        self.browser.maximize_window()  # 窗口最大化
        # 隐性等待，最长等2秒
        self.browser.implicitly_wait(2)

        current_page = 1
        result = self.query_company_page(current_page)
        pages = result.get("pages")
        logger.log("公司总页数：" + str(pages))
        while current_page <= pages:
            result = self.query_company_page(current_page)
            for row in result.get("rows"):
                name = row[1]
                self.browser.get(self.company_url.format(name))
                # 解析数据
                job_list = self.browser.find_elements_by_xpath("//div[@id='qz-list-box']/a[@id='cktarget']")
                cur_num = 0
                if len(job_list) > 0:
                    while len(job_list) > cur_num:
                        cur_num = len(job_list)
                        # 满10条提交一次
                        if cur_num % 10 == 0:
                            for job in job_list[-10:]:
                                item = BaiduZhaopinItem()
                                item['company_name'] = job.find_element_by_xpath(
                                    "./div/div[@class='inlineblock percent33']/div[@class='company']/span[@class='inlineblock companyname']").text
                                item['job_name'] = job.find_element_by_xpath(
                                    "./div/div[@class='inlineblock percent47']/div[@class='title']").text
                                item['location'] = job.find_element_by_xpath(
                                    "./div/div[@class='inlineblock percent33']/div[@class='detail']/span[1]").text
                                item['education'] = job.find_element_by_xpath(
                                    "./div/div[@class='inlineblock percent33']/div[@class='detail']/span[3]").text
                                item['years'] = job.find_element_by_xpath(
                                    "./div/div[@class='inlineblock percent33']/div[@class='detail']/span[5]").text
                                salary_num = job.find_element_by_xpath(
                                    "./div/div[@class='inlineblock percent47']/div[@class='salaryarea top16']/span[@class='inlineblock num']").text
                                try:
                                    salary_unit = job.find_element_by_xpath(
                                        "./div/div[@class='inlineblock percent47']/div[@class='salaryarea top16']/span[@class='inlineblock unit']").text
                                except:
                                    salary_unit = ""
                                item['salary'] = salary_num + salary_unit
                                # 点击跳转详情
                                ActionChains(self.browser).move_to_element(job).click(job).perform()
                                handles = self.browser.window_handles  # 获取窗口句柄集合（列表类型）
                                for handle in handles:  # 切换到新窗口
                                    if handle != self.browser.current_window_handle:
                                        self.browser.switch_to_window(handle)
                                        break
                                item['release_time'] = self.browser.find_element_by_xpath(
                                    "//div[@class='job-desc-box inner home-inner clearfix']/div[@class='job-desc right-box']/div[@class='job-desc-item'][1]/div[@class='job-classfiy']/p[2]").text
                                item['platform'] = self.browser.find_element_by_xpath(
                                    "//div[@class='job-desc-box inner home-inner clearfix']/div[@class='job-desc right-box']/div[@class='job-desc-item'][3]/div[@class='media-item source']/div[@class='item-bd']/h4[@class='bd-tt']").text
                                self.browser.close()  # 关闭当前窗口
                                self.browser.switch_to_window(handles[0])  # 切换回原窗口
                                self.save_item(item)
                        # 滑到底部，加载更多
                        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                        job_list = self.browser.find_elements_by_xpath("//div[@id='qz-list-box']/a[@id='cktarget']")
                    # 提交剩余数据
                    for job in job_list[-10:]:
                        item = BaiduZhaopinItem()
                        item['company_name'] = job.find_element_by_xpath(
                            "./div/div[@class='inlineblock percent33']/div[@class='company']/span[@class='inlineblock companyname']").text
                        item['job_name'] = job.find_element_by_xpath(
                            "./div/div[@class='inlineblock percent47']/div[@class='title']").text
                        item['location'] = job.find_element_by_xpath(
                            "./div/div[@class='inlineblock percent33']/div[@class='detail']/span[1]").text
                        item['education'] = job.find_element_by_xpath(
                            "./div/div[@class='inlineblock percent33']/div[@class='detail']/span[3]").text
                        item['years'] = job.find_element_by_xpath(
                            "./div/div[@class='inlineblock percent33']/div[@class='detail']/span[5]").text
                        salary_num = job.find_element_by_xpath(
                            "./div/div[@class='inlineblock percent47']/div[@class='salaryarea top16']/span[@class='inlineblock num']").text
                        try:
                            salary_unit = job.find_element_by_xpath(
                                "./div/div[@class='inlineblock percent47']/div[@class='salaryarea top16']/span[@class='inlineblock unit']").text
                        except:
                            salary_unit = ""
                        item['salary'] = salary_num + salary_unit
                        # 点击跳转详情
                        ActionChains(self.browser).move_to_element(job).click(job).perform()
                        handles = self.browser.window_handles  # 获取窗口句柄集合（列表类型）
                        for handle in handles:  # 切换到新窗口
                            if handle != self.browser.current_window_handle:
                                self.browser.switch_to_window(handle)
                                break
                        item['release_time'] = self.browser.find_element_by_xpath(
                            "//div[@class='job-desc-box inner home-inner clearfix']/div[@class='job-desc right-box']/div[@class='job-desc-item'][1]/div[@class='job-classfiy']/p[2]").text
                        try:
                            item['platform'] = self.browser.find_element_by_xpath(
                                "//div[@class='job-desc-box inner home-inner clearfix']/div[@class='job-desc right-box']/div[@class='job-desc-item'][3]/div[@class='media-item source']/div[@class='item-bd']/h4[@class='bd-tt']").text
                        except:
                            item['platform'] = "百度"
                        self.browser.close()  # 关闭当前窗口
                        self.browser.switch_to_window(handles[0])  # 切换回原窗口
                        self.save_item(item)
            current_page += 1
        # 关闭浏览器
        self.browser.quit()

    # 获取公司列表
    def query_company_page(self, page_no=1):
        return self.select_rows_paper(
            sql="SELECT `full_name`,`name` FROM `yx_project`",
            page_no=page_no,
            page_size=20
        )

    def save_item(self, item):
        # logger.log("===> " + str(item))
        if item['company_name'] is not None and item['job_name'] is not None and item['platform'] is not None:
            job = self.fetchone(
                "SELECT 1 FROM `xsbbiz`.`baidu_recruitment` WHERE `company_name`='%s' AND `job_name`='%s' AND `platform`='%s'" % (
                    item['company_name'], item['job_name'], item['platform'])
            )
        else:
            return
        if job is None:
            self.insert(
                "INSERT INTO `xsbbiz`.`baidu_recruitment` (`company_name`, `job_name`, `location`, `education`, `years`, `salary`, `release_time`,  `platform`, `update_time`) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (item['company_name'], item['job_name'], item['location'], item['education'], item['years'],
                 item['salary'], item['release_time'], item['platform'], time.localtime()))
        else:
            self.insert(
                """
                UPDATE
                      `xsbbiz`.`baidu_recruitment`
                    SET
                      `location` = %s,
                      `education` = %s,
                      `years` = %s,
                      `salary` = %s,
                      `release_time` = %s,
                      `update_time` = %s
                    WHERE `company_name` = %s AND `job_name` = %s AND `platform` = %s
                """, (
                    item['location'],
                    item['education'],
                    item['years'],
                    item['salary'],
                    item['release_time'],
                    time.localtime(),
                    item['company_name'],
                    item['job_name'],
                    item['platform']
                )
            )
