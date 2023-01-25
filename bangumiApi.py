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
        keyword+"?responseGroup=large&type=1&limit=1"
    res = requests.get(url=url, headers=headers)

    content = res.text
    status_code = res.status_code

    if(status_code != 200):
        print("Status code was " + str(status_code) + ", so skipping...")
        if(status_code == 403):
            print(content)
        return "", ""

    try:
        searchResults = json.loads(content)["list"]
        searchResults.sort(key=sortByLevenshtein)

        subject_id = searchResults[0]['id']
        subject_url = searchResults[0]['url']
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
