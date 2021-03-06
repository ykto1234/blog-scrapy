import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from blog_scrapy.items import BlogScrapyItem
from scrapy.utils.project import get_project_settings
# import Crawler.settings

from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urlparse
import pandas as pd

import mylogger

# ログの定義
logger = mylogger.setup_logger(__name__)


class Parser(object):
    def __init__(self, html: str, url: str, exclusion_list: list):
        self._soup = BeautifulSoup(html, 'html.parser')
        self._url = url
        self._exclusion_list = exclusion_list

    def parse_title(self):
        return self._soup.find('title').get_text(strip=True)

    def pase_article(self):
        # scriptやstyleを含む要素を削除する
        tmp_soup = self._soup
        for script in tmp_soup(["script", "style"]):
            script.decompose()

        # footer以降を削除
        for tag in tmp_soup(["footer"]):
            for tag_next in tag.find_all_next():
                tag_next.decompose()

        # tileのテキストのみを取得=タグは全部取る
        title_text = "-"
        title_text = tmp_soup.find("title").get_text()

        # articleのテキストのみを取得=タグは全部取る
        contents_text = tmp_soup.find("article").get_text()
        if not len(contents_text):
            contents_text = tmp_soup.get_text()

        # textを改行ごとにリストに入れて、リスト内の要素の前後の空白を削除
        lines=[]
        lines.append("----------------URL-----------------")
        lines.append(self._url)
        lines.append("-------------タイトル---------------")
        lines.append(title_text)
        lines.append("----------------記事----------------")
        for line in contents_text.splitlines():
            # 除外ワードが入っている文章を削除する
            output_flg = True
            for exclusion_word in self._exclusion_list:
                if exclusion_word and exclusion_word in line:
                    output_flg = False
                    break

            if output_flg:
                lines.append(line.strip())

        out_text="\n".join(str(line) for line in lines if line)
        return out_text


class ScrapyBlogSpiderSpider(CrawlSpider):
    # scrapyをCLIから実行するときの識別子
    name = 'scrapy_blog_spider'
    # spiderに探査を許可するドメイン
    # allowed_domains = Crawler.settings.CRAWLER_DOMAINS
    # allowed_domains = domain
    # allowed_domains = []
    # 起点(探査を開始する)URL
    # start_urls = ['http://tensyokuknowhow.com/']

    # LinkExtractorの引数で特定のルール(例えばURLにnewを含むページのみスクレイプするなど)を指定可能だが、今回は全てのページを対象とするため引数はなし
    # Ruleにマッチしたページをダウンロードすると、callbackに指定した関数が呼ばれる
    # followをTrueにすると、再帰的に探査を行う
    rules = [Rule(LinkExtractor(), callback='parse_pageinfo', follow=True)]

    def __init__(self, target_domains=[], target_urls=[], item_list=[], *args, **kwargs):
        super(ScrapyBlogSpiderSpider, self).__init__(*args, **kwargs)

        logger.debug("ScrapyBlogSpiderSpider init")

        # spiderに探査を許可するドメイン
        self.allowed_domains = target_domains

        # 起点(探査を開始する)URL
        self.start_urls = target_urls

        # 検索リスト
        self.setting_df = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)

        # サイトメイ
        self.site_name = ""

        # 除外ワードリスト
        self.exclusion_list = []

        # Excelから読み込んだリスト
        self.item_list = item_list


    # def start_requests(self):
    #     # allowed_domains = ['tensyokuknowhow.com']
    #     yield scrapy.Request(url='http://tensyokuknowhow.com/',
    #                         #  callback=self.parse_pageinfo
    #                          )
    #     # allowed_domains = ['axxis.co.jp']
    #     yield scrapy.Request(url='https://axxis.co.jp/magazine/profile',
    #                         #  callback=self.parse_pageinfo
    #                          )
		# for url in ['http://tensyokuknowhow.com/', 'https://axxis.co.jp/magazine/profile']:
		# 	yield scrapy.Request(
		# 		url[0],
		# 		callback=self.parse_pageinfo
		# 	)


    def parse_pageinfo(self, response):

        import excel_setting

        # 検索リストファイルの読み込み（全て欠損値がある行は読み込まない）
        if len(self.setting_df) == 0:
           self.setting_df = excel_setting.read_excel_setting("./設定ファイル.xlsx", "設定", 0, "A:D")

        for i in range(0, len(self.setting_df)):
            url = self.setting_df.iloc[i]['URL']
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if domain in response.url:
                self.site_name = self.setting_df.iloc[i]['サイト名']
                exclusion_str = self.setting_df.iloc[i]['除外ワード']
                break

        self.exclusion_list = exclusion_str.split(",")
        logger.debug("exclusion_list: " + exclusion_str)
        logger.debug("site_name: " + self.site_name)

        # レスポンスから Parser オブジェクトを生成する
        parser = Parser(response.text, response.url, self.exclusion_list)
        title_text = parser.parse_title()
        article_text = parser.pase_article()
        sel = Selector(response)
        item = BlogScrapyItem()
        item['url'] = response.url
        item['title'] = title_text
        item['article'] = article_text
        logger.debug(item['url'])
        logger.debug(item['title'])

        # ファイル名に使えないものは置換
        folder_name = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', self.site_name)
        file_name = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', title_text)
        out_dir = './output/article/' + folder_name + '/'
        os.makedirs(out_dir, exist_ok=True)

        f = open(out_dir + file_name + '.txt', 'w', encoding='UTF-8')
        f.write(article_text)
        f.close()

        return item