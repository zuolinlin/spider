# dyly_spider
**项目结构** 
```
dyly_spider
├─bin 执行脚本
│  ├─git-pull.bat 更新代码（windows）
│  ├─git-pull.sh 更新代码（mac、linux）
│  ├─robo_report.bat 萝卜-研报 执行脚本（windows）
│  ├─run.bat 执行（windows）
│  └─run.sh  执行（mac、linux）
├─dyly_spider 爬虫相关
│  │─file 谷歌浏览器驱动文件（需浏览器渲染完才能抓取时使用）
│  │─spiders 爬虫
│  │    ├─zdb 投资界
│  │    │   ├─ZdbSeleniumSpider.py 投资人物（浏览器渲染）
│  │    │   └─ZdbSpider.py 投资人物
│  │    └─BaseSpider.py  爬虫父类
│  ├─items.py 指定保存文件的数据结构
│  ├─middlewares.py  中间件，处理request和reponse等相关配置
│  └─pipelines.py 项目管道，可以输出items
│  └─settings.py  设置文件，指定项目的一些配置
├─util 工具类
│  ├─db 数据库
│  ├─CookieUtil.py cookie
│  ├─cy_logger.py 日志
│  ├─date_util.py 日期
│  ├─QiniuUtil.py 七牛文件管理工具类
│  └─XPathUtil.py xpath相关
├─scrapy.cfg scrapy配置 
├─README.md 说明文件
├─requirements.txt 依赖包
├─shells.txt  爬虫解析相关
└─run.py 执行
```
**依赖包**
```
命令行安装
pip install scrapy
pip install pymysql
pip install selenium
pip install qiniu
pip install DBUtils
pip install pypiwin32（mac、linux 不需要安装）
也可以使用下面命令批量安装
pip install -r requirements.txt
```
**如windows安装scrapy失败手动下载安装twisted，后安装scrapy**
- [下载twisted](https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted)
- pip install Twisted-18.9.0-cp37-cp37m-win_amd64.whl

**执行**
```
根目录执行
scrapy crawl 爬虫名称 -s LOG_FILE=/logs/spider.log
```