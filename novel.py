import requests
import re
import random
import os
import time
from concurrent.futures import ThreadPoolExecutor


#http://www.uu234.net/

# Match_dir = r"<li>.*</li>"
# Match_context = r'[\s\S]*a_336.*?</div>([\s\S]+?)</div'

#http://www.126shu.com/
# Match_dir = r"<dd>.*</dd>"
# Match_context = r'[\s\S]*<div id="content">[\s\S]*?</div>([\s\S]+?)<div'

# https://www.booktxt.net/
# Match_dir = r"<dd>.*</dd>"
# Match_context = r'[\s\S]*<div id="content">([\s\S]+?)</div'

#http://www.xs7.com/shu/
# Match_dir = r"<DIV class=dccss>[\s\S]*?<a href[\s\S]*?</DIV>"
# Match_context = r'[\s\S]*id=content[\s\S]*?<P>([\s\S]*?)</P>'

#https://www.vodtw.com/
# Match_dir = r"<li>.*title.*</li>"
# Match_context = r'[\s\S]*?<div id="trail"[\s\S]*?</div>([\s\S]*?)</div'

#http://www.biquyun.com/  笔趣阁
Match_dir = r"<dd>.*?</dd>"
Match_context = r'[\s\S]*<div id="content">([\s\S]+?)</div'


#https://www.qu.la/ 笔趣阁2
# Match_dir = r"<dd>.*?</dd>"
# Match_context = r'[\s\S]*<div id="content">([\s\S]+?)</br>'

#http://www.qiuxiaoshuo.com/   求小说网
# Match_dir = r"<li .*?read.*?</li>"
# Match_context = r'[\s\S]*<div id="txtContent">([\s\S]+?)</div>'
Match_title = r'[\s\S]*<(title|TITLE)>(.*?)[^\u4e00-\u9fa5]'
profix = ''
#添加前缀
# http://www.qiuxiaoshuo.com/read/17915.html
# /read/17915/5512624.html
def define_profix(dir_address, context_address):
    profix = ''
    a = context_address.replace("//", " ").replace("/", " ").split(" ")
    b = dir_address.replace("//", " ").replace("/", " ").split(" ")
    if (len(a) == 1):
        profix = dir_address
    elif (len(a) == 3 or len(a)==4):
        profix = b[0] + "//" + b[1]
    else:
        profix = ""
    print("dsjnf:"+profix)
    return profix
#   在线爬取代理ip
# def getIplist():
#     url = "https://www.kuaidaili.com/free/intr/"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
#     }
#     response = requests.get(url, headers=headers)
#     content_ip = re.findall(r"\"IP\">.*<", response.text)
#     content_port = re.findall(r"\"PORT\">.*<", response.text)
#     iplist = []
#     for i in range(len(content_ip)):
#         iplist.append(
#             "http://" + re.findall("[0-9|\.].*\d", content_ip[i])[0] + ":" +
#             re.findall("[0-9|\.].*\d", content_port[i])[0])
#
#     return iplist

#   读取本地存放的代理ip
def readIpList():
    list = open("iplist.txt", "r")
    Iplist = []
    for each_line in list:
        t = re.match(r'([0-9].*[0-9]).*(h.*[ps])', each_line)
        Iplist.append({t.group(2): t.group(2) + "://" + t.group(1)})
    return Iplist


#   获得网站编码格式
def getCharset(htmText):
    return  re.match(r'[\s\S]*?<meta.*?charset=.*?(.+?)"', htmText).group(1)

# 获得网页文章内容
def read_content(path='http://www.uu234.net/r11/20677.html',title="无", proxies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
    }
    if (proxies != None):
        response = requests.get(path, timeout=5, headers=headers, proxies=proxies)
    else:
        response = requests.get(path, timeout=5, headers=headers)

    response.encoding = getCharset(response.text)
    t = re.match(Match_context, response.text)
    if(response.status_code !=200):
        raise Exception("403错误")
    print("已加载：" + title+str(response.status_code))
    context=re.sub(re.compile(r"<.*?br.*?>", re.S), "\n", t.group(1).replace('\n',''))
    context = re.sub(re.compile(r"<.*?p.*?>", re.S), "\n", context)
    return title + "\n" + context.replace("&nbsp;", " ")+ "\n"


#  定义一个线程爬 10 个章节
def every_ten(list_10, storeAdress):
    Iplist = readIpList()
    proxies = random.choice(Iplist)
    f = open(storeAdress, "a", encoding='utf-8')
    flag = 0
    for address in list_10:
        while True:
            try:
                text = read_content(address[0], address[1], proxies)
                f.write(text)
                flag = 0
            except Exception as e:
                # print('第二层', end='：')
                # print(e)
                flag = 1
                proxies = random.choice(Iplist)
            if (flag == 0):
                break
    f.close()


#    将各个进程的章节融合
def Convert_into_a_book(dir_address="data\将夜最新章节"):
    list = os.listdir(path=dir_address)
    list.sort(key=len)
    print(list)
    os.chdir(dir_address)
    fz = open(dir_address[5:] + ".txt", "a", encoding='utf-8')
    context = ''
    for text_address in list:
        print(text_address)
        ff = open(text_address, 'r', encoding='utf-8')
        context = context + ff.read()
        ff.close()
        os.remove(text_address)
    fz.write(context)
    fz.close()


'''
  最高30个进程
'''

#  获得章节列表
def downloads_list(dir_address):
    test_cookie=""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
    }
    Iplist = readIpList()
    proxies = random.choice(Iplist)
    while (1):
        try:

            response = requests.get(dir_address, timeout=10, headers=headers, proxies=proxies)
            response.encoding = response.apparent_encoding
            title = re.match(Match_title,response.text).group(2)
            print(title)
            # 创建一个操作目录
            if not os.path.exists("data"):
                os.mkdir("data")
            os.mkdir("data//" + title)
            temp = re.findall(Match_dir, response.text)
        except FileExistsError:
            rm_list=os.listdir("data//" + title)
            for i in rm_list:
                os.remove("data//"+title+"//"+i)
            os.rmdir("data//" + title)
            continue
        except Exception as e:
            print('第一层', end='：')
            # print(response.status_code, end='：')
            print(e)
            # print(response.text)
            proxies = random.choice(Iplist)
            continue
        charset = getCharset(response.text)
        response.encoding = charset
        print("网页编码格式: " + charset)
        print('Parent process %s.' % os.getpid())
        threadPool = ThreadPoolExecutor(30)  # 设置30个线程恰好合适
        numB = 0
        numA = 0
        list = []
        print("章节数  ："+str(len(temp)))
        print(temp[0])
        profix = define_profix(dir_address,re.match(r"[\s\S]*?<a[\s\S]+?href=['\"]([\s\S]*?html)['\"][\s\S]*?>([\s\S]+?)<", temp[0], re.M | re.I).group(1))
        print("前缀: "+profix)

        for t in temp:
            numA += 1
            a = re.match(r"[\s\S]*?<a[\s\S]+?href=['\"]([\s\S]*?html)['\"][\s\S]*?>([\s\S]+?)<", t, re.M | re.I)
            list.append([profix+a.group(1), a.group(2)])
            if (numA % 10 == 0 or numA == len(temp)):
                addrs = "data//" + title+ "//" + str(numB) + "_" + str(numA) + ".txt"
                threadPool.submit(every_ten,list,addrs)  #  有点坑，，必须这样传参，用args会报错
                numB = numA
                list = []
        return 0
        print("start")
        threadPool.shutdown() # 等待线程上的程序跑完
        print("end")
        Convert_into_a_book('data\\' + title)
        print("结束")
        break


if __name__ == "__main__":
    # print(read_content("http://www.biqu.cm/14_14772/8375934.html"))
    # 修改目录，文章，正则匹配式，
    req = 0
    print("Match_dir(默认):",Match_dir)
    req= input("是否修改（1 ：修改）:")
    if req:
        Match_dir = input("新的Match_dir：")
        req = 0
    print("Match_context(默认):",Match_context)
    req= input("是否修改（1 ：修改）:")
    if req:
        Match_dir = input("新的Match_context：")
    while 1:
        load_url = input("下载地址:")
        # time.sleep(3)
        start = time.time()
        downloads_list(load_url.strip())
        end = time.time()
        print('Task runs %0.2f seconds.' % ((end - start)))

