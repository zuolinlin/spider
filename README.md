# dyly_spider
**项目结构** 
```
cy-generator
├─dyly_spider 爬虫相关
│  └─spiders 爬虫
│  │    │─zdb 投资界
│  │    │   └─ZdbSpider.py 投资人物
│  │    └─BaseSpider.py  爬虫父类
│  ├─items.py 指定保存文件的数据结构
│  ├─middlewares.py  中间件，处理request和reponse等相关配置
│  └─pipelines.py 项目管道，可以输出items
│  └─settings.py  设置文件，指定项目的一些配置
├─util 工具类
│  ├─db 数据库
│  └─cy_logger.py 日志
├─scrapy.cfg scrapy配置 
└─run.py 执行
```