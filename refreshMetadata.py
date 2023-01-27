# -*- coding: utf-8 -*- #
# ------------------------------------------------------------------
# Description: BangumiKomga(https://github.com/chu-shen/BangumiKomga)
# ------------------------------------------------------------------

import sys

from processMetadata import *
from komgaApi import *


def addMangaProgress(seriesID, filename):
    '''
    记录已处理的komga漫画`seriesID`至`filename`
    '''
    if(keepProgress == False):
        return
    progfile = open(filename, "a+")
    progfile.write(str(seriesID) + "\n")
    progfile.close()


def skipProcessedManga(filename):
    '''
    跳过`filename`中已处理的漫画
    '''
    progresslist = []
    if(keepProgress):
        print("Loading list of successfully updated mangas")
        try:
            with open(filename) as file:
                progresslist = [line.rstrip() for line in file]
        except:
            print("Failed to load list of mangas")
    return progresslist


def refreshBookMetadata(seriesID, fixBangumiInfo=True):
    '''
    更新漫画系列的单册元数据
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
    if bangumiSeriesLink != None and useExistBangumiLink == True:
        seriesSubject_url = bangumiSeriesLink
        seriesSubject_id = re.sub(r'\D', '', bangumiSeriesLink)
    else:
        first_name, second_name = guessMangaName(seriesMetadata["name"])
        print("Getting metadata for: " + first_name+", "+second_name)

        seriesSubject_id, seriesSubject_url = getSeriesUrlFromSearch(
            first_name)
        if(seriesSubject_url == ""):
            seriesSubject_id, seriesSubject_url = getSeriesUrlFromSearch(
                second_name)
            if(seriesSubject_url == ""):
                print("No result found or error occured")
                return komangaBookMetadata

    try:
        seriesSubjectRelations = json.loads(
            getSubjectRelations(seriesSubject_id))
    except:
        return komangaBookMetadata

    processedMangaBooks = "mangabooks.progress"
    skipBookLists = skipProcessedManga(processedMangaBooks)
    failedfile = open("failedBooks.txt", "w")
    # 处理系列下的单册漫画
    for book in getKomangaSeriesBooks(seriesID)['content']:
        bookName = book['name']
        bookID = book['id']
        if(str(bookID) in skipBookLists and fixBangumiInfo):
            print("Manga book " + str(bookName) +
                  " was already updated, skipping...")
            continue
        print("Updating book: " + str(bookName))
        md = setKomangaBookMetadata(
            book, komangaBookMetadata, seriesSubjectRelations)

        if(md.isvalid == False):
            print("----------------------------------------------------")
            print("Failed to update " + str(bookName))
            print("----------------------------------------------------")
            failedfile.write(str(bookID) + "\n")
            addMangaProgress(bookID, processedMangaBooks)
            continue

        # TODO komgaApi.metadata
        json_data = {
            "authors": md.authors,
            "summary": md.summary,
            "tags": md.tags,
            "title": md.title,
            "isbn": md.isbn,
            "number": md.number,
            "links": md.links,
            "releaseDate": md.releaseDate,
            "numberSort": md.numberSort
        }

        patch = updateKomangaBookMetadata(bookID, json.dumps(json_data))
        if(patch.status_code == 204):
            print("----------------------------------------------------")
            print("Successfully updated " + str(bookName))
            print("----------------------------------------------------")
            addMangaProgress(bookID, processedMangaBooks)
        else:
            try:
                print("----------------------------------------------------")
                print("Failed to update " + str(bookName))
                print("----------------------------------------------------")
                print(patch)
                print(patch.text)
                failedfile.write(str(bookID) + "\n")
                addMangaProgress(bookID, processedMangaBooks)
            except:
                pass
    failedfile.close()


def refreshMetadata():
    '''
    更新漫画元数据
    '''
    print("Using user: " + komgaemail)

    if libraryID == '':
        komanga_info = getKomangaSeries()
    else:
        komanga_info = getKomangaSeriesWithLibraryID(libraryID)

    # 总漫画数量
    try:
        expected = komanga_info['numberOfElements']
        print("Series to do: ", expected)
    except:
        print("Failed to get list of mangas, are the login infos correct?")
        sys.exit(1)

    failedfile = open("failedSeries.txt", "w")

    processedMangaSeries = "mangaseries.progress"
    skipSeriesLists = skipProcessedManga(processedMangaSeries)

    seriesnum = 0
    for series in komanga_info['content']:
        seriesnum += 1

        if(len(mangasTobeProcessed) > 0):
            if(series['name'] not in mangasTobeProcessed):
                continue
        print("Number: " + str(seriesnum) + "/" + str(expected))

        name = series['name']
        seriesID = series['id']

        # 优先使用已配置的bangumi链接进行查询
        bangumiLink = None
        for link in series['metadata']["links"]:
            if link["label"].lower() == "bangumi":
                bangumiLink = link["url"]
                break

        # 检查当前元数据与链接条目元数据是否一致(当前仅检查别名中的`Original`)
        fixBangumiInfo = True
        if bangumiLink != None:
            bangumiID = re.sub(r'\D', '', bangumiLink)
            bangumiName = json.loads(getSubject(bangumiID))["name"]
            for alternateTitle in series['metadata']["alternateTitles"]:
                if alternateTitle["label"] == "Original" and alternateTitle["title"] != bangumiName:
                    fixBangumiInfo = False

                    # 跳过已处理的漫画系列
        if(str(seriesID) in skipSeriesLists and bangumiLink != None and fixBangumiInfo):
            print("Manga " + str(name) + " was already updated, skipping...")
            refreshBookMetadata(seriesID, fixBangumiInfo)
            continue
        print("Updating: " + str(name))

        md = setKomangaSeriesMetadata(name, bangumiLink)

        if(md.isvalid == False):
            print("----------------------------------------------------")
            print("Failed to update " + str(name))
            print("----------------------------------------------------")
            failedfile.write(str(seriesID) + "\n")
            addMangaProgress(seriesID, processedMangaSeries)
            continue

        # TODO komgaApi.metadata
        json_data = {
            "status": md.status,
            "summary": md.summary,
            "publisher": md.publisher,
            "genres": md.genres,
            "tags": md.tags,
            "title": md.title,
            "alternateTitles": md.alternateTitles,
            "ageRating": md.ageRating,
            "links": md.links,
            "totalBookCount": md.totalBookCount,
            "language": md.language
        }

        patch = updateKomangaSeriesMetadata(seriesID, json.dumps(json_data))
        if(patch.status_code == 204):
            print("----------------------------------------------------")
            print("Successfully updated " + str(name))
            print("----------------------------------------------------")
            addMangaProgress(seriesID, processedMangaSeries)
        else:
            try:
                print("----------------------------------------------------")
                print("Failed to update " + str(name))
                print("----------------------------------------------------")
                print(patch)
                print(patch.text)
                failedfile.write(str(seriesID) + "\n")
                addMangaProgress(seriesID, processedMangaSeries)
            except:
                pass

        refreshBookMetadata(seriesID, fixBangumiInfo)

    failedfile.close()


refreshMetadata()
