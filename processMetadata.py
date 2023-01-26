# -*- coding: utf-8 -*- #
# ------------------------------------------------------------------
# Description: 处理komga漫画元数据
# ------------------------------------------------------------------

import re
import zhconv

from bangumiApi import *
from komgaApi import *


def __setTags(manga_metadata, manga):
    taglist = []
    for info in manga["tags"]:
        if info["count"] >= 3:
            taglist.append(info["name"])

    manga_metadata.tags = taglist


def __setGenres(manga_metadata, manga):
    genrelist = []
    # TODO 修正元数据值
    # bangumi并没有将漫画划分流派，后续可以考虑从tags中提取匹配
    genrelist.append(manga["platform"])
    for info in manga["infobox"]:
        if info["key"] == "连载杂志":
            print(type(info["value"]))
            if type(info["value"]) == list:
                for v in info["value"]:
                    genrelist.append(v["v"])
            else:
                genrelist.append(info["value"])
    # komga无评分/评级，暂时先将分数添加到流派字段中
    genrelist.append(str(round(manga["rating"]["score"]))+"分")

    manga_metadata.genres = genrelist


def __setStatus(manga_metadata, manga):
    # TODO 判断漫画刊载情况
    runningLang = ["放送", "放送（連載）中"]
    abandonedLang = ["打ち切り"]
    endedLang = ["完結", "结束", "连载结束"]

    for info in manga["infobox"]:
        if(info["key"] in runningLang):
            casestatus = "ONGOING"
        elif(info["key"] in abandonedLang):
            casestatus = "ABANDONED"
        elif(info["key"] in endedLang):
            casestatus = "ENDED"
        else:
            casestatus = "ONGOING"

    manga_metadata.status = casestatus


def __setTotalBookCount(manga_metadata, subjectRelations):
    totalBookCount = 0
    for relation in subjectRelations:
        # TODO 冷门漫画可能无关联条目，需要完善总册数判断逻辑
        if relation["relation"] == "单行本":
            totalBookCount = totalBookCount+1
    manga_metadata.totalBookCount = totalBookCount if totalBookCount == 0 else 1


def __setLanguage(manga_metadata, manga_filename):
    languageTypes = ["日版"]
    for languageType in languageTypes:
        if(languageType in manga_filename):
            manga_metadata.language = "ja-JP"


def __setAlternateTitles(manga_metadata, manga):
    alternateTitles = []
    if manga["name_cn"] != '':
        title = {
            "label": "Bangumi",
            "title": manga["name_cn"]
        }
        alternateTitles.append(title)
    manga_metadata.alternateTitles = alternateTitles


def __setPublisher(manga_metadata, manga):
    for info in manga["infobox"]:
        if info["key"] == "出版社":
            manga_metadata.publisher = info["value"]


def __setAgeRating(manga_metadata, manga):
    if manga["nsfw"] == True:
        manga_metadata.ageRating = 18


def __setTitle(manga_metadata, manga):
    # 优先使用中文标题
    if manga["name_cn"] != '':
        manga_metadata.title = manga["name_cn"]
    else:
        manga_metadata.title = manga["name"]


def __setSummary(manga_metadata, manga):
    manga_metadata.summary = manga["summary"]


def __setLinks(manga_metadata, manga, subject_url, subjectRelations):
    # TODO 可以考虑替换komga漫画系列封面图。目前默认为第一本的封面
    links = [
        {
            "label": "Bangumi", "url": subject_url
        },
        {
            "label": "Bangumi Image", "url": manga["images"]["large"]
        }
    ]
    for relation in subjectRelations:
        if relation["relation"] == "动画":
            link = {"label": "动画："+relation["name"],
                    "url": "https://bgm.tv/subject/"+str(relation["id"])}
            links.append(link)
        if relation["relation"] == "书籍":
            link = {"label": "书籍："+relation["name"],
                    "url": "https://bgm.tv/subject/"+str(relation["id"])}
            links.append(link)
    manga_metadata.links = links


def __guessMangaName(query):
    '''
    猜测漫画名，并返回猜测结果
    '''
    # 将繁体转为简体
    cc = zhconv.convert(query, 'zh-cn')

    # 一般以[]分割，
    pattern = re.compile(r'(?<=\[).+?(?=\])')
    result = pattern.findall(cc)

    if len(result) == 0:
        return cc, cc
    # 第一组为作者名，第二组大概率为漫画名（位置可能互换）
    if len(result) >= 2:
        return result[1], result[0]
    # 如果不足两组，返回正则未匹配到的字符串
    if len(result) < 2:
        temp = cc.replace('[', '').replace(result[0], '').replace(']', '')
        # 去除特殊字符
        temp = re.sub(r'[\W]', '', temp)
        return temp, temp


def setKomangaSeriesMetadata(mangaFileName, bangumiLink=None):
    '''
    获取漫画系列元数据
    '''
    # init
    komangaSeriesMetadata = seriesMetadata()

    # 优先使用已配置的bangumi链接进行查询
    if bangumiLink == None:
        first_name, second_name = __guessMangaName(mangaFileName)
        print("Getting metadata for: " + first_name+", "+second_name)

        subject_id, subject_url = getUrlFromSearch(first_name)
        if(subject_url == ""):
            subject_id, subject_url = getUrlFromSearch(second_name)
            if(subject_url == ""):
                print("No result found or error occured")
                return komangaSeriesMetadata
    else:
        subject_url = bangumiLink
        subject_id = re.sub('https://bgm.tv/subject/', '', bangumiLink)

    try:
        bangumiMetadata = json.loads(getSubject(subject_id))
    except:
        return komangaSeriesMetadata

    subjectRelations = json.loads(getSubjectRelations(subject_id))

    # link
    __setLinks(komangaSeriesMetadata, bangumiMetadata,
               subject_url, subjectRelations)

    # summary
    __setSummary(komangaSeriesMetadata, bangumiMetadata)

    # status
    __setStatus(komangaSeriesMetadata, bangumiMetadata)

    # genres
    __setGenres(komangaSeriesMetadata, bangumiMetadata)

    # tags
    __setTags(komangaSeriesMetadata, bangumiMetadata)

    # totalBookCount
    __setTotalBookCount(komangaSeriesMetadata, subjectRelations)

    # language
    __setLanguage(komangaSeriesMetadata, mangaFileName)

    # alternateTitles
    __setAlternateTitles(komangaSeriesMetadata, bangumiMetadata)

    # publisher
    __setPublisher(komangaSeriesMetadata, bangumiMetadata)

    # ageRating
    __setAgeRating(komangaSeriesMetadata, bangumiMetadata)

    # title
    __setTitle(komangaSeriesMetadata, bangumiMetadata)

    komangaSeriesMetadata.isvalid = True
    return komangaSeriesMetadata


def setKomangaBookMetadata(book, seriesID):
    '''
    获取漫画单册元数据
    '''
    # init
    komangaBookMetadata = bookMetadata()

    seriesMetadata = getKomangaSeriesMetadata(seriesID)

    # 跳过无bangumi链接的漫画系列
    try:
        bangumiSeriesLink = None
        for link in seriesMetadata['metadata']["links"]:
            if link["label"].lower() == "bangumi":
                bangumiSeriesLink = link["url"]
                break
        if bangumiSeriesLink == None:
            return komangaBookMetadata
    except:
        return komangaBookMetadata

    # 优先使用已配置的bangumi链接进行查询
    if bangumiSeriesLink == None:
        first_name, second_name = __guessMangaName(seriesMetadata["name"])
        print("Getting metadata for: " + first_name+", "+second_name)

        seriesSubject_id, seriesSubject_url = getUrlFromSearch(first_name)
        if(seriesSubject_url == ""):
            seriesSubject_id, seriesSubject_url = getUrlFromSearch(second_name)
            if(seriesSubject_url == ""):
                print("No result found or error occured")
                return komangaBookMetadata
    else:
        seriesSubject_url = bangumiSeriesLink
        seriesSubject_id = re.sub(
            'https://bgm.tv/subject/', '', bangumiSeriesLink)

    try:
        seriesSubjectRelations = json.loads(
            getSubjectRelations(seriesSubject_id))
    except:
        return komangaBookMetadata

    # 直接使用komga提取到的册数
    number = book["number"]

    # title 暂不做修改
    komangaBookMetadata.title = book["name"]
    # number 暂不做修改
    komangaBookMetadata.number = number

    for relation in seriesSubjectRelations:
        pattern = re.compile(r'[0-9]{1,5}')
        # TODO 确认单行本册数获取方法
        # 仅在漫画系列下的单行本中比较
        if relation["relation"] != '单行本':
            continue
        result = pattern.findall(relation["name"])
        if len(result) == 0:
            result = pattern.findall(relation["name_cn"])
        if len(result) == 0:
            continue
        # 取最后一个匹配的数字 e.g. 20世紀少年 (01)
        if int(result[-1]) == number:
            subject_id = relation["id"]

            bangumiMetadata = json.loads(getSubject(subject_id))
            subjectRelations = json.loads(
                getSubjectRelations(subject_id))
            subject_url = "https://bgm.tv/subject/"+str(relation["id"])

            # link
            __setLinks(komangaBookMetadata, bangumiMetadata,
                       subject_url, subjectRelations)

            # summary
            __setSummary(komangaBookMetadata, bangumiMetadata)

            # tags
            __setTags(komangaBookMetadata, bangumiMetadata)

            # authors
            authors = []
            for info in bangumiMetadata["infobox"]:
                if info["key"] == "作者":
                    '''
                    基础格式：{'name':'值','role':'角色类型'}
                    角色类型有：
                        writer:作者
                        inker:画图者
                        translator:翻译者
                        editor:主编
                        cover:封面
                        letterer:嵌字者
                        colorist:上色者
                        penciller:铅稿
                        自定义的角色类型值
                    '''
                    author = {
                        "name": info["value"],
                        "role": 'writer'
                    }
                    authors.append(author)
            komangaBookMetadata.authors = authors

            # releaseDate
            komangaBookMetadata.releaseDate = bangumiMetadata["date"]

            # isbn
            for info in bangumiMetadata["infobox"]:
                if info["key"] == "ISBN":
                    # invalid ISBN
                    # komangaBookMetadata.isbn = info["value"]
                    continue

            komangaBookMetadata.isvalid = True
            return komangaBookMetadata

    return komangaBookMetadata
