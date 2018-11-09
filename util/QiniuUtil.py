# -*- coding: utf-8 -*-
import time
import urllib3
from qiniu import Auth, put_data, BucketManager
from util import cy_logger as logger

# 需要填写你的 Access Key 和 Secret Key
access_key = 'p0tMQL52alFIkq0kCm1lhxWODR-b3b06CDOF8tzn'
secret_key = 'Eefm3b78pFa1Dc3ZH28iMGuyrnwIVGibpU6kgBDG'
# 要上传的空间
bucket = 'xsb-dyly'
qiniu_url = "https://img1.dyly.com/"
# 构建鉴权对象
q = Auth(access_key, secret_key)
bm = BucketManager(q)
urllib3.disable_warnings()
http = urllib3.PoolManager()


def upload(url, filename, gen_folde):
    """
    上传网络文件
    :param url: 网络文件地址
    :param filename: 文件名
    :param gen_folde: 目录类别 image、media、authent、voice、file
    :return: 上传七牛返回的地址、文件大小
    """
    try:
        if url is None or filename is None:
            return
        if "image".__eq__(gen_folde):
            gen_folde = "image"
        elif "media".__eq__(gen_folde):
            gen_folde = "yvd"
        elif "authent".__eq__(gen_folde):
            gen_folde = "important"
        elif "voice".__eq__(gen_folde):
            gen_folde = "voice"
        else:
            gen_folde = "file"
        # 生成上传 Token
        token = q.upload_token(bucket)
        data = http.request("GET", url).data
        ret, info = put_data(
            token,
            gen_folde + "/" + time.strftime("%Y%m%d", time.localtime()) + "/" + filename,
            data,
            mime_type=None
        )
        return qiniu_url + ret['key'], round(len(data)/1024, 2)
    except Exception as e:
        logger.error("exception===> " + str(e))


def delete(url):
    """
    删除指定文件
    :param url: 牛文件地址
    :return:
    """
    try:
        if url is not None:
            url = url.replace(qiniu_url, "")
            ret, info = bm.delete(bucket, url)
            print(info)
            print(ret)
    except Exception as e:
        logger.error("exception===> " + str(e))


if __name__ == '__main__':
    # print(upload("https://p.ishowx.com/uploads/allimg/170526/648-1F5261GH5-50.jpg", "zly6", "image"))
    delete("https://img1.dyly.com/image/2018-10-25/zly3")


