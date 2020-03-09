import requests
import re
import time
from random import random
import csv
import os

class post(object):
    def __init__(self):
        self.tag = {}
        self.repliesNo = {}
        self.starter = {}
        self.views = {}
        self.startDate = {}
        self.lastAct = {}
        self.comment = {}
        self.section = []

    def findSection(self):
        url='https://forum.lowyat.net/'
        get = requests.get(url)
        js = get.content.decode('utf-8')
        section = re.findall('href="\/(.*?)"',js)
        for s in section:
            if '.' not in s and '/' not in s:
                s = re.sub('&amp;','&',s)
                self.section.append(s)
        print("Section crawled completed")

    def findPost(self,section,pageComment,pagePost):
        url='https://forum.lowyat.net/' + section
        lim = 0
        get = requests.get(url)
        js = get.content.decode('utf-8')   
        maxPagePost = re.findall('<span class="pagelink"><a title="Jump to page\.\.\." href="javascript:multi_page_jump\(.*?\);">(.*?) Pages<\/a><\/span>',js)[0]
        while lim / 30 < pagePost and lim < int(maxPagePost):
            get = requests.get(url)
            js = get.content.decode('utf-8')    
            result = re.findall(r'<!-- Begin Topic Entry.*-->((.|\n)*?)<!-- End Topic.*?>',js)
            for r in result:
                postID = '-999'
                try:
                    postID = re.findall('<a href="\/topic\/(.*?)" title="This topic was started:.*?">',r[0])[0]
                    tag = re.findall("<img src=\"https:\/\/forum.lowyat.net\/style_images\/1\/.*?\" border='0'  alt='(.*?)' \/>",r[0])[0]
                    repliesNo = re.findall('<a href="javascript:who_posted\(.*?\);">(.*?)<\/a>',r[0])[0]
                    repliesNo = re.sub(',','',repliesNo)
                    starter = re.findall('<td align="center" class="row2" id=".*?"><a href=\'https:\/\/forum\.lowyat\.net\/index\.php\?s=.*?;showuser=.*?\'>(.*?)<\/a>',r[0])[0]
                    views = re.findall('<td align="center" class="row2" id="forum_topic_views">\n.*?<.*?>\n.*?s = "(.*?)"',r[0])[0]
                    startDate = re.findall('<a href="\/topic\/.*?" title="This topic was started:(.*?)">',r[0])[0]
                    lastAct = re.findall('<td class="row2" id="forum_topic_lastaction">\n.*?<span class="lastaction">(.*?)<br \/>',r[0])[0]
                    self.inputPost(postID,tag,repliesNo,starter,views,startDate,lastAct,pageComment)
                    self.printPostInfo(postID)
                    self.outputCSV(section)
                    self.__init__()
                except KeyError as e:
                    print("Post {} crawl failed with error {}".format(postID,e))
            lim += 30


    def inputPost(self,postID,tag,repliesNo,starter,views,startDate,lastAct,pageComment):
        self.tag[postID] = tag
        self.repliesNo[postID] = repliesNo
        self.starter[postID] = starter
        self.views[postID] = views
        self.startDate[postID] = startDate
        self.lastAct[postID] = lastAct
        self.findComment(postID,pageComment)

    def printPostInfo(self,postID):
        print("-----\nPost ID: {}\nStarter: {}\nTag: {}\nReplies: {}\nViews: {}\nStart Date: {}\nLast Action: {}\nTotal Comment:{}\n-----".format(
                postID,self.starter[postID],self.tag[postID],self.repliesNo[postID],self.views[postID],
                self.startDate[postID],self.lastAct[postID],len(self.comment[postID])))
        
    def printComment(self,postID):
        for c in self.comment[postID]:
            print(c)

    def findComment(self,postID,pageComment):
        lim = 0
        self.comment[postID] = []
        while lim < int(self.repliesNo[postID]) + 1 and lim / 20 < pageComment:
            url = 'https://forum.lowyat.net/topic/' + postID + '/+' + str(lim)
            getcomment = requests.get(url)
            js = getcomment.content.decode('utf-8',errors='ignore')
            segcomment = re.findall("<!--Begin Msg Number.*?-->((.|\n)*?)<\/table>",js)
            for s in segcomment:
                name = re.findall("<a href=\\'\/user\/.*?\\'>(.*?)<\/a>",s[0])[0]
                comment = re.findall('<!-- THE POST.*?-->((.|\n)*?)<div class="postcolor post_text" data-postid=".*?">(.*?)<!--IBF\.ATTACHMENT_.*?--><\/div>\\n\\t\\t\\t<div class="signature" data-postid=".*?">',s[0])
                if comment:
                    comment = re.sub('<(.*?|\n)*?>|QUOTE\(.*?\)|&.*?;','',comment[0][2])
                    self.comment[postID].append([name,comment])
            time.sleep(random()*10)
            lim += 20
            print("Crawling comment {}+".format(lim))
            
    def outputCSV(self,section):
        folder = "lowyat/{}/{}".format(section,"allpost.csv")
        mfolder = "lowyat/{}".format(section)
        if not os.path.exists(mfolder):
            os.makedirs(mfolder)
        
        fieldnames = ['name', 'post', 'emotion']
        if not os.path.exists(folder):
            commentFile = open(folder,'a+',encoding='utf-8',newline="")
            writer = csv.DictWriter(commentFile, fieldnames=fieldnames)
            writer.writeheader()
            commentFile.close()     

        commentFile = open(folder.format(section,"allpost.csv"),'a+',encoding='utf-8',newline="")
        writer = csv.DictWriter(commentFile, fieldnames=fieldnames)
        for postID in self.comment.keys():
            for comment in self.comment[postID]:
                writer.writerow({'name':comment[0],'post':comment[1]})
        commentFile.close()
    
    def crawl(self,pageComment,pagePost,numPostClearMemo):
        self.findSection()
        for s in self.section:
            print("Crawling section {}".format(s))
            self.findPost(s,pagePost,pageComment)
            
p = post()
p.crawl(5,3,10)