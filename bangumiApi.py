# -*- coding: utf-8 -*- #
# ------------------------------------------------------------------
# Description: Bangumi API(https://github.com/bangumi/api)
# ------------------------------------------------------------------

import requests
import json
from Levenshtein import distance

headers = {
    'User-Agent': 'chu-shen/BangumiKomga (https://github.com/chu-shen/BangumiKomga)'
}

sortKeyword = ''


def sortByLevenshtein(searchResult):
    '''
    将Bangumi搜索结果按照字符串相似度进行排序

    Bangumi搜索结果未排序，存在第一个结果非所需漫画的情况
    '''
    return min(distance(sortKeyword, searchResult["name"]), distance(
        sortKeyword, searchResult["name_cn"]))


def getUrlFromSearch(keyword):
    '''
    获取搜索结果
    '''
    global sortKeyword
    sortKeyword = keyword
    url = "https://api.bgm.tv/search/subject/" + \
        keyword+"?responseGroup=large&type=1"
    res = requests.get(url=url, headers=headers)

    content = res.text
    status_code = res.status_code

    subject_id = ''
    subject_url = ''

    if(status_code != 200):
        print("Status code was " + str(status_code) + ", so skipping...")
        if(status_code == 403):
            print(content)
        return "", ""

    try:
        searchResults = json.loads(content)["list"]
        searchResults.sort(key=sortByLevenshtein)

        # bangumi中漫画、小说都属于书籍类型。
        # 由于komga不支持小说文字的读取，这里直接忽略`小说`类型，避免返回错误结果
        comicCount = 0
        while comicCount < len(searchResults):
            platform = getSubject(searchResults[comicCount]['id'])["platform"]
            if platform == "漫画":
                subject_id = searchResults[0]['id']
                subject_url = searchResults[0]['url']
                break
            comicCount = comicCount+1
    except:
        return '', ''

    return subject_id, subject_url


def getSubject(id):
    '''
    获取漫画元数据
    '''
    url = "https://api.bgm.tv/v0/subjects/" + str(id)
    res = requests.get(url=url, headers=headers)

    content = res.text
    status_code = res.status_code

    if(status_code != 200):
        print("Status code was " + str(status_code) + ", so skipping...")
        if(status_code == 403):
            print(content)
        if(status_code == 404):
            print("try login")
        return ""

    return content


def getSubjectRelations(id):
    '''
    获取漫画的关联条目
    '''
    url = "https://api.bgm.tv/v0/subjects/" + str(id)+"/subjects"
    res = requests.get(url=url, headers=headers)

    content = res.text
    status_code = res.status_code

    if(status_code != 200):
        print("Status code was " + str(status_code) + ", so skipping...")
        if(status_code == 403):
            print(content)
        if(status_code == 404):
            print("try login")
        return ""

    return content
