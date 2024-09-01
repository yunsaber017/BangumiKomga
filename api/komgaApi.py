# -*- coding: utf-8 -*- #
# ------------------------------------------------------------------
# Description: Komga API(https://github.com/gotson/komga/blob/master/komga/docs/openapi.json)
# ------------------------------------------------------------------


import requests
from tools.log import logger
from requests.adapters import HTTPAdapter

class KomgaApi:
    def __init__(self, base_url, username, password):
        # store the base URL and authentication information for use in other methods
        self.base_url = base_url + '/api/v1'
        self.auth = (username, password)

        self.r = requests.Session()
        self.r.mount('http://', HTTPAdapter(max_retries=3))
        self.r.mount('https://', HTTPAdapter(max_retries=3))
        
        url = f'{self.base_url}/login/set-cookie'
        response = self.r.get(url, auth=self.auth,headers = {
            'User-Agent': 'chu-shen/BangumiKomga (https://github.com/chu-shen/BangumiKomga)'})
        if response.status_code != 204:
            logger.error("Komga: login failed!")
            exit(1)


    def get_all_series(self, parameters=None):
        '''
        Retrieves all series in the komga comic.

        https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L4859
        '''
        url = f'{self.base_url}/series'
        if parameters:
            # 取消默认分页（大小为 2000），以便一次性获取所有系列
            url += f'?{parameters}&size=50000&unpaged=true'
        else:
            url += '?size=50000&unpaged=true'
        try:
            # make a GET request to the URL to retrieve all series
            response = self.r.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            return []
        # return the response as a JSON object
        return response.json()

    def get_series_with_libaryid(self, library_id):
        '''
        Retrieves all series in a specified library in the komga comic.

        https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L4875
        '''
        return self.get_all_series(f'library_id={library_id}')

    def get_series_with_collection(self, collection_id):
        '''
        Retrieves all series with a specified collection in the komga comic.
        '''
        return self.get_all_series(f'collection_id={collection_id}')

    def get_series_with_read_status(self, read_status):
        '''
        Retrieves all series with a specified read status in the komga comic.

        Status options: "UNREAD", "READ", "IN_PROGRESS"
        '''
        return self.get_all_series(f'read_status={read_status}')

    def get_series_with_readlist(self, readlist_id):
        '''
        Retrieves all series with a specified readlist in the komga comic.
        '''
        try:
            response = self.r.get(
                f'{self.base_url}/readlists/{readlist_id}')
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            return []
        # return the response as a JSON object
        return response.json()

    def get_series_books(self, series_id):
        '''
        Retrieves all books in a specified series in the komga comic.

        https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L5373
        '''
        try:
            # make a GET request to the URL to retrieve all books in a given series
            response = self.r.get(
                f'{self.base_url}/series/{series_id}/books?size=50000&unpaged=true')
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            return []
        # return the response as a JSON object
        return response.json()
    
    def get_series_thumbnails(self, series_id):
        '''
        Retrieves all thumbnails in a specified series in the komga comic.
        '''
        try:
            # make a GET request to the URL to retrieve all thumbnails in a given series
            response = self.r.get(
                f'{self.base_url}/series/{series_id}/thumbnails')
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            return []
        # return the response as a JSON object
        return response.json()

    
    def get_book_thumbnails(self, book_id):
        '''
        Retrieves all thumbnails in a specified book in the komga comic.
        '''
        try:
            # make a GET request to the URL to retrieve all thumbnails in a given series
            response = self.r.get(
                f'{self.base_url}/books/{book_id}/thumbnails')
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            return []
        # return the response as a JSON object
        return response.json()

    def update_series_metadata(self, series_id, metadata):
        '''
        Updates the metadata of a specified comic series.
        '''
        try:
            # make a PATCH request to the URL to update the metadata for a given series
            response = self.r.patch(
                f'{self.base_url}/series/{series_id}/metadata', json=metadata)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
        # return True if the status code indicates success, False otherwise
        return response.status_code == 204
    
    def update_series_thumbnail(self, series_id, thumbnail):
        '''
        Updates the thumbnail of a specified comic series.
        '''
        try:
            # make a POST request to the URL to update the thumbnail for a given series
            response = self.r.post(
                f'{self.base_url}/series/{series_id}/thumbnails?selected=true', files=thumbnail)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
        # return True if the status code indicates success, False otherwise
        return response.status_code == 200

    def update_book_metadata(self, book_id, metadata):
        '''
        Updates the metadata of a specified comic book.

        https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L2935
        '''
        if not UPDATE_BOOK_NUMBER:
            metadata.pop('number', None)
        try:
            # make a PATCH request to the URL to update the metadata for a given book
            response = self.r.patch(
                f'{self.base_url}/books/{book_id}/metadata', json=metadata)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
        # return True if the status code indicates success, False otherwise
        return response.status_code == 204
    
    
    def update_book_thumbnail(self, book_id, thumbnail):
        '''
        Updates the thumbnail of a specified comic book.
        '''
        try:
            # make a POST request to the URL to update the thumbnail for a given series
            response = self.r.post(
                f'{self.base_url}/books/{book_id}/thumbnails?selected=true', files=thumbnail)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
        # return True if the status code indicates success, False otherwise
        return response.status_code == 200
    
    def add_collection(self, name, ordered, seriesIds):
        '''
        add new collection.
        '''
        try:
            response = self.r.post(
                f'{self.base_url}/collections', json={"name": name, "ordered": ordered, "seriesIds": seriesIds})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
        # return True if the status code indicates success, False otherwise
        return response.status_code == 200

    def get_collection_id_by_search_name(self, name):
        '''
        search collection by name
        return collection id.
        '''
        try:
            response = self.r.get(
                f'{self.base_url}/collections?search={name}')
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
        collection = response.json()['content']
        if collection:        
            return collection[0]['id']
        else:
            return None
    def delete_collection(self, id):
        '''
        delete collection.
        '''
        try:
            response = self.r.delete(
                f'{self.base_url}/collections/{id}')
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
        # return True if the status code indicates success, False otherwise
        return response.status_code == 204
    
    def replace_collection(self, name, ordered, seriesIds):
        id=self.get_collection_id_by_search_name(name)
        if id is None or self.delete_collection(id):
            return self.add_collection(name, ordered, seriesIds)


class seriesMetadata:
    '''
    Class to represent Komga series metadata fields. 

    See https://github.com/gotson/komga/blob/master/komga/docs/openapi.json#L10449 for fields. 
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
        self.totalBookCount = 1  # must be greater than 0

        self.isvalid = False


class bookMetadata:
    '''
    Class to represent Komga book metadata fields.
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
        self.numberSort = 0  # 短序号

        self.isvalid = False
