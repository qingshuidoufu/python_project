# coding=utf-8
import urllib
import requests
import re
from bs4 import BeautifulSoup
import random
import time


def parser_apks(count=300, category="topList"):
    _root_url = "http://app.mi.com"  # 应用市场主页网址
    res_parser = {}
    # 设置爬取的页面，从第一页开始爬取，第一页爬完爬取第二页，以此类推(至少从第二页开始爬取,从第二页开始链接开始有规律)
    page_num = 2
    while count:
        # 获取应用列表页面
        print("进入循环 count=" + str(count))
        wbdata = requests.get("http://app.mi.com/"+category+"?page=" + str(page_num)).text
        print("开始爬取第" + category + "页面" + str(page_num) + "页")
        # 解析应用列表页面内容
        soup = BeautifulSoup(wbdata, "html.parser")
        links = soup.find_all("a", href=re.compile("/details\?id="), class_="", alt="")
        # 正则表达使用/?来匹配?,更精准匹配避免匹配到其他页面去
        if len(links) == 0:
            print("==============links空了=================")
            break

        for link in links:
            # 获取应用详情页面的链接
            detail_link = urllib.parse.urljoin(_root_url, str(link["href"]))
            package_name = detail_link.split("=")[1]
            download_page = requests.get(detail_link).text
            # 解析应用详情页面
            soup1 = BeautifulSoup(download_page, "html.parser")
            download_link = soup1.find(class_="download")["href"]
            # 获取直接下载的链接
            download_url = urllib.parse.urljoin(_root_url, str(download_link))
            # 解析后会有重复的结果，通过判断去重
            if package_name not in res_parser.keys():
                if count > 0:
                    res_parser[package_name] = download_url
                    count = count - 1
                else:
                    break
            if count == 0:
                break
        if count > 0:
            page_num = page_num + 1


    print("爬取apk数量为: " + str(len(res_parser)))
    return res_parser


user_agent_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
    "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]


def auto_down(url, filename):
    try:
        opener = urllib.request.build_opener()
        # opener.addheaders = [('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30')]
        opener.addheaders = [('User-Agent', random.choice(user_agent_list))]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, filename)
    except urllib.request.ContentTooShortError:
        print('Network conditions is not good.Reloading.')
        auto_down(url, filename)
    except urllib.error.HTTPError:
        print(str(urllib.error.HTTPError))
    except:
        # auto_down(url,filename)
        print("sssssss oh ssssssss  出错了 , 可能是本地对应文件夹未创建")


def craw_apks(count=300, category="topList", save_path="/home/liuzhe/ApkResources"):
    print("craw_apks count=" + str(count))
    res_dic = parser_apks(count, category)

    for apk in res_dic.keys():
        print("正在下载应用: " + apk)
        time.sleep(2)
        print("下载位置: " + str(res_dic[apk]))
       # urllib.request.urlretrieve(res_dic[apk], save_path + apk + ".apk")  #此处不用是因为无法实现自动更换ua功能
        auto_down(res_dic[apk], save_path + apk + ".apk")
        print("下载完成: " + apk)
    print(str(category) + "=category====finish=====")


if __name__ == "__main__":
    category = "topList"
    # category 为网页链接中的排行榜
    craw_apks(999, category, "D:\\miApk\\" + str(category) + "\\")
    # 需要在本地先建立miApk/topList 文件夹
    # craw_apks(50,category,"D:\\miApk\\")
    # category = category + 1

