
import komgaApi
import bangumiApi
from config import *
from log import logger


def update_read_progress(force_refresh_list=[]):
    '''
    更新阅读进度
    '''
    bgm = bangumiApi.BangumiApi(BANGUMI_ACCESS_TOKEN)
    # Initialize the komga API and get all book series
    komga = komgaApi.KomgaApi(
        KOMGA_BASE_URL, KOMGA_EMAIL, KOMGA_EMAIL_PASSWORD)
    all_series = komga.get_all_series()

    series_name = series['name']

    for series in all_series['content']:
        force_refresh_flag = series['id'] in force_refresh_list
        # Skip the series if it's not in the force refresh list
        if len(force_refresh_list) > 0 and not force_refresh_flag:
            continue

        books_read_count = series['booksReadCount']
        try:
            for link in series['metadata']['links']:
                if link['label'].lower() == "bangumi":
                    subject_id = link['url'].split("/")[-1]
                    break
        except ValueError as e:
            logger.exception(e)
            logger.error("Update read progress for "+series_name+" failed:")
            continue

        # TODO 添加是否同步判断逻辑，比如：是否`在读`
        if bgm.update_reading_progress(subject_id, books_read_count):
            logger.info("Successfully update: "+series_name +
                        " series read progress: "+books_read_count)
        else:
            logger.error("Failed to update: "+series_name +
                         " series read progress: "+books_read_count)


update_read_progress(FORCE_REFRESH_LIST)
