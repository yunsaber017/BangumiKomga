
import re
from tools.getTitle import get_title
import processMetadata
from time import strftime, localtime
from tools.env import *
from tools.log import logger
from tools.notification import send_notification
from tools.db import initSqlite3, record_series_status, record_book_status


def refresh_metadata(force_refresh_list=[]):
    '''
    刷新书籍系列元数据
    '''
    env = InitEnv()

    bgm = env.bgm
    komga = env.komga
    all_series = env.all_series

    cursor, conn = initSqlite3()

    # 批量获取所有series_id
    series_ids = [series['id'] for series in all_series]
    # 执行一次查询获取所有series_id对应的记录
    series_records = cursor.execute("SELECT * FROM refreshed_series WHERE series_id IN ({})".format(
        ','.join('?' for _ in series_ids)), series_ids).fetchall()

    success_count = 0
    failed_count = 0
    success_comic = ''
    failed_comic = ''

    failed_series_ids = []

    # Loop through each book series
    for series in all_series:
        series_id = series['id']
        series_name = series['name']

        force_refresh_flag = series_id in force_refresh_list
        # Skip the series if it's not in the force refresh list
        if len(force_refresh_list) > 0 and not force_refresh_flag:
            continue
        # 找到对应的series_record
        series_record = next(
            (record for record in series_records if record[0] == series_id), None)
        # series_record=c.execute("SELECT * FROM refreshed_series WHERE series_id=?", (series_id,)).fetchone()
        # Check if the series has already been refreshed
        if series_record and not force_refresh_flag:
            if series_record[2] == 1:
                subject_id = cursor.execute(
                    "SELECT subject_id FROM refreshed_series WHERE series_id=?", (series_id,)).fetchone()[0]
                refresh_book_metadata(bgm, komga, subject_id,
                                      series_id, conn, force_refresh_flag)
                continue

            # recheck or skip failed series
            elif series_record[2] == 0 and not RECHECK_FAILED_SERIES:
                logger.debug("skip falied series: "+series_name)
                continue

        # Get the subject id from the Correct Bgm Link (CBL) if it exists
        subject_id = None
        for link in series['metadata']['links']:
            if link['label'].lower() == "cbl":
                subject_id = link['url'].split("/")[-1]
                # Get the metadata for the series from bangumi
                metadata = bgm.get_subject_metadata(subject_id)
                break

        # Use the bangumi API to search for the series by title on komga
        if subject_id == None:
            title = get_title(series_name)
            if title == None:
                failed_count, failed_comic = record_series_status(
                    conn, series_id, subject_id, 0, series_name, "None", failed_count, failed_comic)
                failed_series_ids.append(series_id)
                continue
            search_results = bgm.search_subjects(title)
            if len(search_results) > 0:
                subject_id = search_results[0]['id']
                metadata = search_results[0]
            else:
                failed_count, failed_comic = record_series_status(
                    conn, series_id, subject_id, 0, series_name, "no subject in bangumi", failed_count, failed_comic)
                failed_series_ids.append(series_id)
                continue

        komga_metadata = processMetadata.setKomangaSeriesMetadata(
            metadata, series_name, bgm)

        if(komga_metadata.isvalid == False):
            failed_count, failed_comic = record_series_status(
                conn, series_id, subject_id, 0, series_name, komga_metadata.title+" metadata invalid", failed_count, failed_comic)
            failed_series_ids.append(series_id)
            continue

        series_data = {
            "status": komga_metadata.status,
            "summary": komga_metadata.summary,
            "publisher": komga_metadata.publisher,
            "genres": komga_metadata.genres,
            "tags": komga_metadata.tags,
            "title": komga_metadata.title,
            "alternateTitles": komga_metadata.alternateTitles,
            "ageRating": komga_metadata.ageRating,
            "links": komga_metadata.links,
            "totalBookCount": komga_metadata.totalBookCount,
            "language": komga_metadata.language
        }

        # Update the metadata for the series on komga
        isSuccessed = komga.update_series_metadata(series_id, series_data)
        if(isSuccessed):
            success_count, success_comic = record_series_status(
                conn, series_id, subject_id, 1, series_name, komga_metadata.title, success_count, success_comic)
            # 使用 Bangumi 图片替换原封面
            # 确保没有上传过海报，避免重复上传
            if USE_BANGUMI_THUMBNAIL and len(komga.get_series_thumbnails(series_id)) == 0:
                thumbnail=bgm.get_subject_thumbnail(metadata)
                replace_thumbnail_result=komga.update_series_thumbnail(series_id, thumbnail)
                if replace_thumbnail_result:
                    logger.debug("replace thumbnail for series: "+series_name)
                else:
                    logger.error("Failed to replace thumbnail for series: "+series_name)
        else:
            failed_count, failed_comic = record_series_status(
                conn, series_id, subject_id, 0, series_name, "komga update failed", failed_count, failed_comic)
            failed_series_ids.append(series_id)
            continue
        
        if UPDATE_BOOK_METADATA:
            refresh_book_metadata(bgm, komga, subject_id,
                              series_id, conn, force_refresh_flag)

    # Add the series that failed to obtain metadata to the collection
    if CREATE_FAILED_COLLECTION and failed_series_ids:
        collection_name="FAILED_COLLECTION"
        if komga.replace_collection(collection_name, False, failed_series_ids):
            logger.info(
                "Successfully replace collection: "+collection_name)
        else:
            logger.error("Failed to replace collection: "+collection_name)
            
    logger.info("Finish! succeed: "+str(success_count) +
                ", failed: "+str(failed_count))
    send_notification("已完成刷新！", "<font color='green'>已成功刷新："+str(success_count)+"</font> \n ---\n 包含以下条目：\n"+success_comic+"\n" +
                      "<font color='red'>失败数："+str(failed_count)+"</font>\n\n包含以下条目：\n"+failed_comic+"\n" +
                      strftime('%Y-%m-%d %H:%M:%S', localtime()))


def getNumber(s):
    # TODO 数字匹配，包括：I、一、1、①
    # Define the pattern to match decimal numbers in the format of "xx.xx"
    pattern = r"\d+\.\d"
    # e.g. 16-5
    s = s.replace('-', '.').replace('_', '.')
    # Use the `re.findall` function to search for all occurrences of the pattern in the input string
    numbers = re.findall(pattern, s)
    # If no decimal numbers are found, change the pattern to match integer numbers
    if not numbers:
        pattern = r"\d+"
        numbers = re.findall(pattern, s)

    # Return the list of found numbers
    return numbers

#只有卷时获取元数据
def isVolumn(book_name):
    #书名中匹配卷
    words = ["vol", "volume", "卷", "卷集", "卷"]
    if any(book_name.find(word) !=-1 for word in words):
        return True
    else:
        return False


def refresh_book_metadata(bgm, komga, subject_id, series_id, conn, force_refresh_flag):
    '''
    刷新书元数据
    '''
    if subject_id == None:
        return

    related_subjects = None
    subjects_numbers = []

    # Get all books in the series on komga
    books = komga.get_series_books(series_id)

    # 批量获取所有book_id
    book_ids = [book['id'] for book in books['content']]

    c = conn.cursor()
    # 执行一次查询获取所有book_id对应的记录
    book_records = c.execute("SELECT * FROM refreshed_books WHERE book_id IN ({})".format(
        ','.join('?' for _ in book_ids)), book_ids).fetchall()

    # Loop through each book in the series on komga
    for book in books['content']:
        book_id = book['id']
        book_name = book['name']

        # 找到对应的book_record
        book_record = next(
            (record for record in book_records if record[0] == book_id), None)
        if book_record and not force_refresh_flag:
            if book_record[2] == 1:
                continue

            # recheck or skip failed book
            elif book_record[2] == 0 and not RECHECK_FAILED_BOOKS:
                logger.debug("skip falied books: "+book_name)
                continue

        # If related_subjects is still empty[], skip
        if related_subjects is None:
            # Get the related subjects for the series from bangumi
            related_subjects = [subject for subject in bgm.get_related_subjects(
                subject_id) if subject['relation'] == "单行本"]

            # Get the number for each related subject by finding the last number in the name or name_cn field
            subjects_numbers = []
            for subject in related_subjects:
                numbers = getNumber(subject['name'] + subject['name_cn'])
                try:
                    subjects_numbers.append(
                        float(numbers[-1]) if numbers else float(1))
                except ValueError:
                    logger.error("Failed to extract number: " + book_id + ", " +
                                 subject['name'] + ", " + subject['name_cn'])

        # get nunmber from book name
        try:
            book_number = float(getNumber(book_name)[-1])
        except:
            book_number = float(1)
        ep_flag = True
        # Update the metadata for the book if its number matches a related subject number
        for i, number in enumerate(subjects_numbers):
            # todo 只考虑单行本匹配
            if book_number == number and isVolumn(book_name):
                ep_flag = False
                # Get the metadata for the book from bangumi
                book_metadata = processMetadata.setKomangaBookMetadata(
                    related_subjects[i]['id'], number, book_name, bgm)
                if(book_metadata.isvalid == False):
                    record_book_status(
                        conn, book_id, related_subjects[i]['id'], 0, book_name, "metadata invalid")
                    break

                book_data = {
                    "authors": book_metadata.authors,
                    "summary": book_metadata.summary,
                    "tags": book_metadata.tags,
                    "title": book_metadata.title,
                    "isbn": book_metadata.isbn,
                    "number": book_metadata.number,
                    "links": book_metadata.links,
                    "releaseDate": book_metadata.releaseDate,
                    "numberSort": book_metadata.numberSort
                }

                # Update the metadata for the series on komga
                isSuccessed = komga.update_book_metadata(
                    book_id, book_data)
                if(isSuccessed):
                    record_book_status(
                        conn, book_id, related_subjects[i]['id'], 1, book_name, "")
                    
                    # 使用 Bangumi 图片替换原封面
                    # 确保没有上传过海报，避免重复上传，排除 komga 生成的封面
                    if USE_BANGUMI_THUMBNAIL_FOR_BOOK and len(komga.get_book_thumbnails(book_id)) == 1:
                        thumbnail=bgm.get_subject_thumbnail(related_subjects[i])
                        replace_thumbnail_result=komga.update_book_thumbnail(book_id, thumbnail)
                        if replace_thumbnail_result:
                            logger.debug("replace thumbnail for book: "+book_name)
                        else:
                            logger.error("Failed to replace thumbnail for book: "+book_name)
                else:
                    record_book_status(
                        conn, book_id, related_subjects[i]['id'], 0, book_name, "komga update failed")
                break
        # 修正`话`序号
        if ep_flag and UPDATE_CHAPTER_METADATA:
            book_data = {
                "number": book_number,
                "numberSort": book_number
            }
            komga.update_book_metadata(
                book_id, book_data)
            record_book_status(
                conn, book_id, None, 0, book_name, "Only update book number")


refresh_metadata(FORCE_REFRESH_LIST)
