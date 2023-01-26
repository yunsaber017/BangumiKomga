# Bangumi metadata scraper for Komga

## Introduction

This Script gets a list of every manga available on your Komga instance,
looks it up one after another on [Bangumi](https://bgm.tv/) and gets the metadata for the specific series.
This metadata then gets converted to be compatible to Komga and then gets sent to the server instance and added to the manga entry.

## Features

### 已完成

- [x] 漫画系列添加元数据
- [x] 单册漫画添加元数据
- [x] 优先使用漫画系列配置的bangumi链接

### TODO

- [ ] 调整元数据处理逻辑
- [ ] 配置Bangumi登录
- [ ] 同步观看进度至Bangumi
- [ ] 添加同人志

## Requirements

- A Komga instance with access to the admin account
- Either Windows/Linux/MAc or alternatively Docker
- Python installed if using Windows, Linux or Mac natively

## Getting started (Native)

1. Install the requirements using `pip install -r requirements.txt`
2. Rename `config.template.py` to `config.py` and edit the url, email and password to match the ones of your komga instance (User needs to have permission to edit the metadata).

    The "mangas" array can be filled with the names of mangas which are supposed to be updated, if it is left empty every manga will be updated.

    "keepProgress" can be set to either "True" or "False". If it is set to true, successfully updated Mangas will be stored in a list and not be updated on the next run.

    "useExistBangumiLink" 如果设置为`True`，并且在系列元数据的链接中填入`Bangumi`和该漫画系列的bangumi地址，则后续处理将基于此链接地址

    "libraryID" 仅处理该库中的漫画。komga界面点击库即可获得，形如：`0B79XX3NP97K9`

3. Run the script using `python refreshMetadata.py` 注意：会覆盖旧元数据


## 致谢

本项目部分源码及思路来自[Pfuenzle/AnisearchKomga](https://github.com/Pfuenzle/AnisearchKomga)，在此表示感谢！

另外，也感谢以下优秀项目：
- [bangumi/api](https://github.com/bangumi/api)
- [gotson/komga](https://github.com/gotson/komga)