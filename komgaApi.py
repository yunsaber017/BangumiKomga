# -*- coding: utf-8 -*- #
# ------------------------------------------------------------------
# Description: Komga API(https://github.com/gotson/komga/blob/master/komga/docs/openapi.json)
# ------------------------------------------------------------------

import requests
import json
from config import *


class seriesMetadata:
    '''
    漫画系列元数据字段

    https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L10449
    '''

    def __init__(self):
        self.title = ""
        self.status = ""  # 状态
        self.summary = ""  # 概要
        self.publisher = ""  # 出版商
        self.genres = "[]"  # 流派
        self.tags = "[]"    # 标签
        self.alternateTitles = "[]"  # 别名
        self.ageRating = 12  # 分级
        self.language = "zh-CN"  # 语言 https://www.ietf.org/rfc/bcp/bcp47.txt
        self.links = "[]"  # 链接
        self.totalBookCount = None

        self.isvalid = False


class bookMetadata:
    '''
    漫画单册元数据字段
    '''

    def __init__(self):
        self.title = ""
        self.summary = ""
        self.number = 0  # 序号
        self.isbn = ""
        self.authors = "[]"  # 作者
        self.tags = "[]"    # 标签
        self.releaseDate = None  # 发布日期
        self.links = "[]"  # 链接

        self.isvalid = False


def emptyMetadata():
    '''
    清空旧元数据
    '''
    return seriesMetadata()


def getKomangaSeries(parameter=None):
    '''
    获取komga中所有漫画系列

    https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L4859
    '''
    parameters = '?size=50000'
    if parameter != None:
        parameters = parameters+'&'+parameter

    x = requests.get(komgaurl + '/api/v1/series'+parameters,
                     auth=(komgaemail, komgapassword))
    return json.loads(x.text)


def getKomangaSeriesWithLibraryID(libraryID):
    '''
    获取komga指定库中所有漫画系列
    '''
    return getKomangaSeries("library_id="+libraryID)


def getKomangaSeriesWithStatus(status):
    '''
    获取komga指定状态下所有漫画系列

    "enum": [
                  "ENDED",
                  "ONGOING",
                  "ABANDONED",
                  "HIATUS"
                ]
    '''
    return getKomangaSeries("status="+status)


def updateKomangaSeriesMetadata(seriesID, jsondata):
    '''
    更新漫画系列元数据
    '''
    headers = {'Content-Type': 'application/json', 'accept': '*/*'}
    patch = requests.patch(komgaurl + "/api/v1/series/" + seriesID + "/metadata",
                           data=str.encode(jsondata), auth=(komgaemail, komgapassword), headers=headers)
    return patch


def getKomangaBooks(parameter=None):
    '''
    获取komga中所有漫画单册

    https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L7231
    '''
    parameters = '?size=50000'
    if parameter != None:
        parameters = parameters+'&'+parameter

    x = requests.get(komgaurl + '/api/v1/books'+parameters,
                     auth=(komgaemail, komgapassword))
    return json.loads(x.text)


def getKomangaSeriesBooks(seriesID):
    '''
    获取komga中指定漫画系列下所有漫画单册

    https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L5373
    '''
    x = requests.get(komgaurl + '/api/v1/series/' + seriesID + "/books?size=50000",
                     auth=(komgaemail, komgapassword))
    return json.loads(x.text)


def getKomangaSeriesMetadata(seriesID):
    '''
    获取komga中指定漫画系列的元数据

    https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L5373
    '''
    x = requests.get(komgaurl + '/api/v1/series/' + seriesID,
                     auth=(komgaemail, komgapassword))
    return json.loads(x.text)


def updateKomangaBookMetadata(bookID, jsondata):
    '''
    更新漫画单册元数据

    https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L2935
    '''
    headers = {'Content-Type': 'application/json', 'accept': '*/*'}
    patch = requests.patch(komgaurl + "/api/v1/books/" + bookID + "/metadata",
                           data=str.encode(jsondata), auth=(komgaemail, komgapassword), headers=headers)
    return patch
