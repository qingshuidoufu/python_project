# -*- coding=utf-8 -*-

from bs4 import BeautifulSoup    # 网站解析获取数据
import re   # 正则表达,文字匹配
import urllib.request,urllib.request # 指定url获取网页数据
import xlwt # excel操作
import sqlite3  # sqlite操作
# 超链接规则
findLink=re.compile(r'<a href="(.*?)">')   # 创建正则表达式对象,表示规则(字符串的模式)
# 影片图片的超链接规则
findImgSrc=re.compile(r'<img.*src="(.*?)"',re.S) # re.S 让换行符包含在字符中
# 影片的片名规则
findTitle=re.compile(r'<span class="title">(.*)</span>')
# 影片的评分规则
findRating=re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 找到评价人数规则
findJudge=re.compile(r'<span>(\d*)人评价</span>')
# 找到概况规则
findInq=re.compile(r'<span class="inq">(.*)</span>')
# 找到影片的相关内容
findBD=re.compile(r'<p class="">(.*?)</p>',re.S)
# 爬取网页
def getData(baseurl):
    datalist=[]
    for i in range(0,10):  # 调用获取页面信息函数,10次
        url=baseurl+str(i*25)
        html=askURL(url)    # 保存获取到的网页源码
         # 逐一解析数据
        soup=BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item") : # 查找符合要求的字符串
          #  print(item)  测试查看页面
            data=[] #保存一部电影的所有信息
            item=str(item)

            # 获取超链接
            link=re.findall(findLink,item)[0]  # re库通过正则表达式查找指定的字符串
            data.append(link)       #添加链接

            # 获取图片
            imgSrc =re.findall(findImgSrc,item)[0]
            data.append(imgSrc)     # 添加图片

            # 获取名字
            titles=re.findall(findTitle,item)  #片名只有一个中文名,没有外文名
            if(len(titles)==2):
                ctitle=titles[0]
                data.append(ctitle)                 #添加中文名
                otitle=titles[1].replace("/","") #去掉无关符号
                otitle=" ".join(otitle.split())  # 去掉\xa0
                data.append(otitle)     #添加外文名
            else:
                data.append(titles[0])
                data.append('')            #外文名字留空

            # 获取排名
            rating=re.findall(findRating,item)[0]
            data.append(rating)         #添加评分

            #获取评价人数
            judgeNum=re.findall(findJudge,item)[0]
            data.append(judgeNum)      #添加评价人数

            # 获取概述
            inq=re.findall(findInq,item)
            if len(inq)!=0:
                inq=inq[0].replace("。","")  #去掉句号
                inq = " ".join(inq.split())  # 去掉\xa0
                data.append(inq)         #添加概述
            else:
                data.append('')       # 留空

            #获取相关内容
            bd=re.findall(findBD,item)[0]
            bd=re.sub('<br(\s+)?/>(\s+)'," ",bd)  # 去掉<br/>
            bd=re.sub('/'," ",bd) # 去掉/
            bd= " ".join(bd.split())  # 去掉\xa0
            data.append(bd.strip())  #去掉前后空格

            # 处理好的电影信息放进datalist
            datalist.append(data)
            print(data)
    return datalist
# 保存数据
def saveData(datalist,savePath):
    print("save")
    book=xlwt.Workbook(encoding="utf-8",style_compression=0)  # 创建workbook对象
    sheet=book.add_sheet('豆瓣电影Top250',cell_overwrite_ok=True) # 创建工作表
    col=("电影详情链接","图片链接","影片中文名","影片外国名","评分","评价数","概况","相关")
    for i in range(0,8):
        sheet.write(0,i,col[i]) #列名
    for i in range(0,250):
        print("第%d条"%(i+1))
        data=datalist[i]    #取出一部电影数据
        for j in range(0,8):
            sheet.write(i+1,j,data[j])   # 单元格写入
    book.save(savePath)   # 保存单元格

def saveData2DB(datalist,dbPath):

    init_DB(dbPath)
    conn=sqlite3.connect(dbPath)
    cur=conn.cursor();

    for data in datalist:
        for index  in range(len(data)):
            if index==4 or index==5: # 跳过两个numeric型的,不用加"变字符串
                continue
            data[index]='"'+data[index]+'"'

        # sql插入语句,
        sql= '''
            insert into movie250(
                info_link,pic_link,cname,ename,score,rated,introduction,info
            )
            values (%s)'''%",".join(data)   #字符串以, 拼接起来放到sql里面去
        print(sql)

        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()



    print("保存成功")

def init_DB(dbpath):
    # 创建数据表
    sql=''' 
        create table movie250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        introduction text,
        info text
        )
    '''
    #创建数据表
    conn=sqlite3.connect(dbpath)
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

# 得到指定url的网页内容
def askURL(url):
    # 用户代理表示用head伪装浏览器,告诉服务器我们能接受啥类型的文件
    head ={
        # 模拟豆瓣服务器,向服务器发送消息
        # user-agent不能有空格,注意复制过来的空格
        "User-Agent": "Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 86.0.4240.183Safari / 537.36"
    }
    request=urllib.request.Request(url,headers=head)
    html=""
    try:
        response=urllib.request.urlopen(request)
        html=response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html

def main():
    baseurl="http://movie.douban.com/top250?start="


    # 1.爬取网页
    datalist=getData(baseurl)

    # 3.保存数据
    # savaPath=".\\豆瓣电影top250.xls"
    dbPath="movie.db"
    #  saveData(datalist,savaPath)
    saveData2DB(datalist,dbPath)
if __name__ == '__main__':
    main()

