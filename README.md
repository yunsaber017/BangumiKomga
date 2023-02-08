# Bangumi metadata scraper for Komga

## Introduction

This Script gets a list of every manga available on your Komga instance,
looks it up one after another on [Bangumi](https://bgm.tv/) and gets the metadata for the specific series.
This metadata then gets converted to be compatible to Komga and then gets sent to the server instance and added to the manga entry.

![sample](sample.jpg)

## Features

### 已完成

- [x] 漫画系列添加元数据
- [x] 单册漫画添加元数据
- [x] 自动跳过已刷新元数据的条目
- [x] 优先使用漫画系列配置的bangumi链接
- [x] 配置Bangumi登录
- [x] 同步观看进度至Bangumi

### TODO

- [ ] 使用[bangumi/Archive](https://github.com/bangumi/Archive)离线数据代替联网查询
- [ ] ~~添加同人志~~ 推荐使用[LANraragi](https://github.com/Difegue/LANraragi)

## Requirements

- A Komga instance with access to the admin account
- Either Windows/Linux/MAc or alternatively Docker
- Python installed if using Windows, Linux or Mac natively

## 刷新元数据

1. Install the requirements using `pip install -r requirements.txt`
2. Rename `config.template.py` to `config.py` and edit the url, email and password to match the ones of your komga instance (User needs to have permission to edit the metadata).

    `BANGUMI_ACCESS_TOKEN` 用于读取NSFW条目，在https://next.bgm.tv/demo/access-token创建个人令牌

    `FORCE_REFRESH_LIST` 强制刷新的书籍系列，避免自动跳过。komga界面点击书籍系列（对应链接）即可获得，形如：`0B79XX3NP97K9`。建议搭配`cbl(Correct Bgm Link)`使用
    
    `cbl(Correct Bgm Link)` 在系列元数据的链接中填入`cbl`和该漫画系列的bangumi地址即可，后续操作将基于此链接地址。建议搭配`FORCE_REFRESH_LIST`使用，从而修正元数据错误的书籍系列。也可以单独使用，为刷新失败的系列手动匹配


3. Run the script using `python refreshMetadata.py` 注意：会自动跳过已处理的系列及书

**Tips:**

如果无需刷新已失败的系列：
- 可自行将`upsert_series_record`中`0`修改为`1`
- 或者自行修改数据库


如果漫画系列数量上千，请考虑使用[bangumi/Archive](https://github.com/bangumi/Archive)离线数据代替联网查询

## 同步阅读进度

_注意：当前仅为komga至bangumi单向同步_

1. 步骤同`刷新元数据`
2. 步骤同`刷新元数据`

    注意：
    - 如果配置了`FORCE_REFRESH_LIST`，则仅同步此列表配置的漫画系列进度
    - 如果未配置`FORCE_REFRESH_LIST`，则同步komga**所有系列**的漫画进度。**为避免污染时间线，请谨慎操作**
3. `python updateReadProgress.py`

## 命名建议

`[漫画名称][作者][出版社][卷数][其他1][其他2]`



- [漫画名称]：以漫画封面实际名称为准，繁体不必转简体。
- [作者]：作者名字亦以单行本所给名字为准
    - 繁体不转为简体，若有日文假名亦保留，如[島崎讓]、[天王寺きつね]；
    - 若作者为多人，则以`×`或`&`符号连接各作者（**注意：不是英文`x`**），将作画作者列于最后，如[矢立肇×有贺ヒトシ]、[手塚治虫×浦沢直树]、[堀田由美×小畑健]。
- [出版社]: 例如[玉皇朝]、[青文]。
- [卷数]：例如[Vol.01-Vol.12]。
- [其他1]、[其他2]：其他信息。例如[完结]、[来源]。

例如：

```
[碧蓝之海][井上堅二×吉岡公威][Vol.01-Vol.18]
[相合之物][浅野伦][Vol.01-Vol.13]
[海王但丁][皆川亮二×泉福朗][Vol.01-Vol.13][境外版]
```

_命名建议修改自某喵_

## Issues & Pull Requests

欢迎提交新规则、问题、功能……

## 致谢

本项目部分代码及思路来自[Pfuenzle/AnisearchKomga](https://github.com/Pfuenzle/AnisearchKomga)，部分代码生成自[chatgpt](https://chat.openai.com/)，在此表示感谢！


语料库数据来源，感谢公开：
- `bangumi_person.txt`文件提取自[bangumi/Archive](https://github.com/bangumi/Archive)
- `Japanese_Names_Corpus（18W）.txt`文件来自[wainshine/Chinese-Names-Corpus](https://github.com/wainshine/Chinese-Names-Corpus)


另外，也感谢以下优秀项目：
- [gotson/komga](https://github.com/gotson/komga)
- [bangumi/api](https://github.com/bangumi/api)
