# -*- coding: utf-8 -*-
import time

from scrapy import Request, FormRequest
from dyly_spider.spiders.itjuzi.ApiCompanyListSpider import ApiCompanyListSpider


class ApiCompanyInfoSpider(ApiCompanyListSpider):
    """
    IT桔子公司详情接口数据抓取
    """

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 8,
        "CONCURRENT_REQUESTS": 1,
    }

    name = 'itjuzi_api_company_info'

    limit = 1

    def __init__(self, current_page=1, *args, **kwargs):
        super(ApiCompanyInfoSpider, self).__init__(*args, **kwargs)
        if current_page is not None and type(current_page) == int:
            self.current_page = current_page
        self.company_info_url = self.domain + "/company/get_newly_added_com_info?com_id={com_id}"

    def start_requests(self):
        yield FormRequest(
            url=self.get_token_url,
            formdata=self.get_token_form,
        )

    def parse(self, response):
        data = self.get_data(response).get("data", {})
        self.headers.update({
            "AUTHORIZATION": "Bearer {access_token}".format(access_token=data.get("access_token"))
        })
        self.refresh_token = data.get("refresh_token")
        self.log("headers========> " + str(self.headers))
        self.log("refresh_token========> " + self.refresh_token)
        company = self.fetchone("SELECT com_id FROM `itjuzi_company` WHERE need_sync=%s "
                                "ORDER BY modify_date DESC LIMIT 1" % 1)
        if company is not None:
            yield Request(
                url=self.company_info_url.format(com_id=company[0]),
                headers=self.headers,
                dont_filter=True,
                callback=self.company_info
            )

    def company_info(self, response):
        self.exec_refresh_token()
        self.save(self.get_data(response).get("data", {}))
        company = self.fetchone("SELECT com_id FROM `itjuzi_company` WHERE need_sync=%s "
                                "ORDER BY modify_date DESC LIMIT 1" % 1)
        if company is not None:
            yield Request(
                url=self.company_info_url.format(com_id=company[0]),
                headers=self.headers,
                dont_filter=True,
                callback=self.company_info
            )

    def save(self, data):
        if data is None or type(data) != dict:
            return
        # 使用cursor()方法获取操作游标
        connection = self.db.get_connection()
        com_id = data.get("com_id")
        params_list = []
        try:
            # 执行sql语句
            with connection.cursor() as cursor:
                sql, params = self.get_company(data)
                cursor.execute(sql, self.set_sql_params(params))

                params_list.append(self.get_company_foreign_investment(com_id, data))
                params_list.append(self.get_company_tags(com_id, data))
                params_list.append(self.get_company_team(com_id, data))
                params_list.append(self.get_company_team_education(data))
                params_list.append(self.get_company_team_everjob(data))
                params_list.append(self.get_company_invest(com_id, data))
                params_list.append(self.get_company_invest_invst(data))
                params_list.append(self.get_company_invest_fa(data))
                params_list.append(self.get_company_product(com_id, data))
                params_list.append(self.get_company_foreign_merger(com_id, data))
                params_list.append(self.get_company_news(com_id, data))
                params_list.append(self.get_company_milestone(com_id, data))
                params_list.append(self.get_company_similar_company(com_id, data))

                for params in params_list:
                    if params is not None and params[1] is not None and len(params[1]) > 0:
                        cursor.executemany(params[0], self.set_sql_params(params[1]))
                connection.commit()
            self.log("executes successfully")
        except Exception as e:
            self.log_error(str(e))
            # 发生错误时回滚
            connection.rollback()
        finally:
            # 关闭数据库连接
            connection.close()

    def get_company_foreign_merger(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        company_foreign_merger = data.get("company_foreign_merger", [])
        if len(company_foreign_merger) > 0:
            params = []
            for foreign_merger in company_foreign_merger:
                params.append((
                    com_id,
                    foreign_merger.get("merger_id"),
                    foreign_merger.get("merger_show"),
                    foreign_merger.get("merger_title"),
                    foreign_merger.get("merger_company_id"),
                    foreign_merger.get("com_name"),
                    foreign_merger.get("merger_organ_type"),
                    foreign_merger.get("merger_show_year"),
                    foreign_merger.get("merger_show_month"),
                    foreign_merger.get("merger_show_day"),
                    foreign_merger.get("merger_equity_ratio"),
                    foreign_merger.get("merger_detail_money"),
                    foreign_merger.get("invse_assess_money_name"),
                    foreign_merger.get("merger_nearly_money_id"),
                    foreign_merger.get("merger_currency_id"),
                    foreign_merger.get("invse_currency_name"),
                    foreign_merger.get("merger_des"),
                    foreign_merger.get("merger_type"),
                    foreign_merger.get("combine_name")
                ))
            return """
                    INSERT INTO `xsbbiz`.`itjuzi_company_foreign_merger` (
                      `com_id`,
                      `merger_id`,
                      `merger_show`,
                      `merger_title`,
                      `merger_company_id`,
                      `com_name`,
                      `merger_organ_type`,
                      `merger_show_year`,
                      `merger_show_month`,
                      `merger_show_day`,
                      `merger_equity_ratio`,
                      `merger_detail_money`,
                      `invse_assess_money_name`,
                      `merger_nearly_money_id`,
                      `merger_currency_id`,
                      `invse_currency_name`,
                      `merger_des`,
                      `merger_type`,
                      `combine_name`
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, params

    def get_company_news(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        news = data.get("news", [])
        if len(news) > 0:
            params = []
            for new in news:
                params.append((
                    com_id,
                    new.get("com_new_name"),
                    new.get("com_new_url"),
                    new.get("com_new_year"),
                    new.get("com_new_month"),
                    new.get("com_new_day"),
                    new.get("com_new_type_name")
                ))
            return """
                    INSERT INTO `xsbbiz`.`itjuzi_company_news` (
                      `com_id`,
                      `com_new_name`,
                      `com_new_url`,
                      `com_new_year`,
                      `com_new_month`,
                      `com_new_day`,
                      `com_new_type_name`
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, params

    def get_company_milestone(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        milestone = data.get("milestone", [])
        if len(milestone) > 0:
            params = []
            for me in milestone:
                params.append((
                    com_id,
                    me.get("com_mil_year"),
                    me.get("com_mil_month"),
                    me.get("com_mil_detail")
                ))
            return """
                    INSERT INTO `itjuzi_company_milestone` (
                      `com_id`,
                      `com_mil_year`,
                      `com_mil_month`,
                      `com_mil_detail`
                    ) 
                    VALUES (%s, %s, %s, %s)
            """, params

    def get_company_similar_company(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        similar_company = data.get("similar_company", [])
        if len(similar_company) > 0:
            params = []
            for similar in similar_company:
                params.append((
                    com_id,
                    similar.get("com_name"),
                    similar.get("com_logo"),
                    similar.get("com_logo_archive"),
                    similar.get("com_prov"),
                    similar.get("com_born_year"),
                    similar.get("com_born_month"),
                    similar.get("invse_year"),
                    similar.get("invse_month"),
                    similar.get("invese_round_name"),
                    similar.get("invse_detail_money"),
                    similar.get("similar"),
                    similar.get("invse_currency_name"),
                    similar.get("cat_name"),
                    similar.get("cat_name_order")
                ))
            return """
                    INSERT INTO `xsbbiz`.`itjuzi_company_similar_company` (
                      `com_id`,
                      `com_name`,
                      `com_logo`,
                      `com_logo_archive`,
                      `com_prov`,
                      `com_born_year`,
                      `com_born_month`,
                      `invse_year`,
                      `invse_month`,
                      `invese_round_name`,
                      `invse_detail_money`,
                      `similar`,
                      `invse_currency_name`,
                      `cat_name`,
                      `cat_name_order`
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, params

    def get_company_product(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        products = data.get("product", [])
        if len(products) > 0:
            params = []
            for product in products:
                params.append((
                    com_id,
                    product.get("com_pro_id"),
                    product.get("com_pro_name"),
                    product.get("com_pro_type_id"),
                    product.get("com_pro_type_name"),
                    product.get("com_pro_ur"),
                    product.get("com_pro_detail")
                ))
            return """
                    INSERT INTO `itjuzi_company_product` (
                                  `com_id`,
                                  `com_pro_id`,
                                  `com_pro_name`,
                                  `com_pro_type_id`,
                                  `com_pro_type_name`,
                                  `com_pro_ur`,
                                  `com_pro_detail`
                                ) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, params

    def get_company_invest_fa(self, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        invests = data.get("invest", [])
        if len(invests) > 0:
            params = []
            for invest in invests:
                invse_id = invest.get("invse_id")
                items = invest.get("fa", [])
                for item in items:
                    params.append((
                        invse_id,
                        item.get("fa_id"),
                        item.get("fa_name")
                    ))
            return """
                    INSERT INTO `itjuzi_company_invest_fa` (`invse_id`, `fa_id`, `fa_name`) 
                    VALUES (%s, %s, %s)
            """, params

    def get_company_invest_invst(self, data):
        """

        :param data:
        :return:
        """
        invests = data.get("invest", [])
        if len(invests) > 0:
            params = []
            for invest in invests:
                invse_id = invest.get("invse_id")
                items = invest.get("ling_invst", [])
                for item in items:
                    if type(item) == dict:
                        params.append((
                            invse_id,
                            item.get("id"),
                            item.get("logo"),
                            item.get("name"),
                            item.get("type"),
                            0
                        ))
                items = invest.get("sec_invst", [])
                for item in items:
                    if type(item) == dict:
                        params.append((
                            invse_id,
                            item.get("id"),
                            item.get("logo"),
                            item.get("name"),
                            item.get("type"),
                            1
                        ))
                items = invest.get("invsp_or_fund", [])
                for item in items:
                    if type(item) == dict:
                        params.append((
                            invse_id,
                            item.get("id"),
                            item.get("logo"),
                            item.get("name"),
                            item.get("type"),
                            2
                        ))
            return """
                    INSERT INTO `itjuzi_company_invest_invst` (
                                      `invse_id`,
                                      `id`,
                                      `logo`,
                                      `name`,
                                      `type`,
                                      `data_type`
                                    )  VALUES (%s, %s, %s, %s, %s, %s)
            """, params

    def get_company_invest(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        invests = data.get("invest", [])
        if len(invests) > 0:
            params = []
            for invest in invests:
                params.append((
                    com_id,
                    invest.get("invse_id"),
                    invest.get("invse_year"),
                    invest.get("invse_month"),
                    invest.get("invse_day"),
                    invest.get("invse_round_id"),
                    invest.get("invse_round_name"),
                    invest.get("invse_similar_money_id"),
                    invest.get("invse_similar_money_name"),
                    invest.get("invse_detail_money"),
                    invest.get("invse_currency_id"),
                    invest.get("invse_currency_name"),
                    invest.get("invse_stock_ownership"),
                    invest.get("invse_guess_particulars"),
                    invest.get("invse_assess_money_id"),
                    invest.get("invse_assess_money_name"),
                    invest.get("fa_id"),
                ))
            return """
                        INSERT INTO `itjuzi_company_invest` (
                                      `com_id`,
                                      `invse_id`,
                                      `invse_year`,
                                      `invse_month`,
                                      `invse_day`,
                                      `invse_round_id`,
                                      `invse_round_name`,
                                      `invse_similar_money_id`,
                                      `invse_similar_money_name`,
                                      `invse_detail_money`,
                                      `invse_currency_id`,
                                      `invse_currency_name`,
                                      `invse_stock_ownership`,
                                      `invse_guess_particulars`,
                                      `invse_assess_money_id`,
                                      `invse_assess_money_name`,
                                      `fa_id`
                                    ) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, params

    def get_company_team_everjob(self, data):
        """

        :param data:
        :return:
        """
        teams = data.get("team", [])
        if len(teams) > 0:
            params = []
            for team in teams:
                per_id = team.get("per_id")
                items = team.get("everjob", [])
                for item in items:
                    params.append((
                        per_id,
                        item.get("per_ever_job_name")
                    ))
            return """
                    INSERT INTO `itjuzi_company_team_everjob` (`per_id`, `per_ever_job_name`) 
                    VALUES (%s, %s)
            """, params

    def get_company_team_education(self, data):
        """

        :param data:
        :return:
        """
        teams = data.get("team", [])
        if len(teams) > 0:
            params = []
            for team in teams:
                per_id = team.get("per_id")
                items = team.get("education", [])
                for item in items:
                    params.append((
                        per_id,
                        item.get("per_education_name")
                    ))
            return """
                    INSERT INTO `itjuzi_company_team_education` (`per_id`, `per_education_name`) 
                    VALUES (%s, %s)
            """, params

    def get_company_team(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        teams = data.get("team", [])
        if len(teams) > 0:
            params = []
            for team in teams:
                params.append((
                    com_id,
                    team.get("per_id"),
                    team.get("per_name"),
                    team.get("per_logo"),
                    team.get("des"),
                    team.get("per_weibo"),
                    team.get("per_linkedin"),
                    team.get("introduce")
                ))
            return """
            INSERT INTO `itjuzi_company_team` (
                                      `com_id`,
                                      `per_id`,
                                      `per_name`,
                                      `per_logo`,
                                      `des`,
                                      `per_weibo`,
                                      `per_linkedin`,
                                      `introduce`
                                    ) 
                                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            """, params

    def get_company_tags(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        tags = data.get("tags", [])
        if len(tags) > 0:
            params = []
            for tag in tags:
                params.append((
                    com_id,
                    tag.get("tag_id"),
                    tag.get("tag_name")
                ))
            return """
                    INSERT INTO `itjuzi_company_tags` (`com_id`, `tag_id`, `tag_name`) 
                    VALUES (%s, %s, %s)
            """, params

    def get_company_foreign_investment(self, com_id, data):
        """

        :param com_id:
        :param data:
        :return:
        """
        foreign_investments = data.get("company_foreign_investment", [])
        if len(foreign_investments) > 0:
            params = []
            for foreign_investment in foreign_investments:
                params.append((
                    com_id,
                    foreign_investment.get("invse_id"),
                    foreign_investment.get("f_com_id"),
                    foreign_investment.get("com_name"),
                    foreign_investment.get("invse_date"),
                    foreign_investment.get("invse_money"),
                    foreign_investment.get("invse_currency_name"),
                    foreign_investment.get("invse_round_name")
                ))
            return """
                    INSERT INTO `xsbbiz`.`itjuzi_company_foreign_investment` (
                              `com_id`,
                              `invse_id`,
                              `f_com_id`,
                              `com_name`,
                              `invse_date`,
                              `invse_money`,
                              `invse_currency_name`,
                              `invse_round_name`
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, params

    def get_company(self, company):
        """
        公司基本信息
        :param company:
        :return:
        """
        return """
            UPDATE 
              `itjuzi_company` 
            SET
              `com_name` = %s,
              `com_sec_name` = %s,
              `com_registered_name` = %s,
              `com_slogan` = %s,
              `com_logo` = %s,
              `com_logo_archive` = %s,
              `com_video` = %s,
              `horse_club` = %s,
              `com_des` = %s,
              `com_url` = %s,
              `com_born_year` = %s,
              `com_location` = %s,
              `com_born_month` = %s,
              `com_prov` = %s,
              `com_city` = %s,
              `com_status_name` = %s,
              `com_stage_name` = %s,
              `com_fund_needs_name` = %s,
              `com_scale_name` = %s,
              `com_fund_status_name` = %s,
              `com_weibo_url` = %s,
              `com_weixin_url` = %s,
              `com_cont_tel` = %s,
              `com_cont_email` = %s,
              `com_cont_addr` = %s,
              `cat_id` = %s,
              `cat_name` = %s,
              `sub_cat_id` = %s,
              `sub_cat_name` = %s,
              `com_relative_invst` = %s,
              `invse_total_money` = %s,
              `com_type` = %s,
              `create_time` = %s,
              `update_time` = %s,
              `modify_date` = %s,
              `need_sync` = %s 
            WHERE `com_id` = %s
               """, (
            company.get("com_name"),
            company.get("com_sec_name"),
            company.get("com_registered_name"),
            company.get("com_slogan"),
            company.get("com_logo"),
            company.get("com_logo_archive"),
            company.get("com_video"),
            company.get("horse_club"),
            company.get("com_des"),
            company.get("com_url"),
            company.get("com_born_year"),
            company.get("com_location"),
            company.get("com_born_month"),
            company.get("com_prov"),
            company.get("com_city"),
            company.get("com_status_name"),
            company.get("com_stage_name"),
            company.get("com_fund_needs_name"),
            company.get("com_scale_name"),
            company.get("com_fund_status_name"),
            company.get("com_weibo_url"),
            company.get("com_weixin_url"),
            company.get("com_cont_tel"),
            company.get("com_cont_email"),
            company.get("com_cont_addr"),
            company.get("cat_id"),
            company.get("cat_name"),
            company.get("sub_cat_id"),
            company.get("sub_cat_name"),
            company.get("com_relative_invst"),
            company.get("invse_total_money"),
            company.get("com_type"),
            company.get("create_time"),
            company.get("update_time"),
            time.localtime(),
            False,
            company.get("com_id")
        )

    def set_sql_params(self, params):
        if type(params) == list:
            for i, items in enumerate(params):
                params_list = list(items)
                for j, item in enumerate(params_list):
                    params_list[j] = self.set_sql_value(item)
                    params[i] = tuple(params_list)
        elif type(params) == tuple:
            params_list = list(params)
            for i, item in enumerate(params_list):
                params_list[i] = self.set_sql_value(item)
                params = tuple(params_list)
        return params

    def set_sql_value(self, value):
        if len(str(value)) == 0:
            value = None
        return value
