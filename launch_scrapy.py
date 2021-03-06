import scrapy
from scrapy.crawler import CrawlerProcess
from blog_scrapy.spiders.scrapy_blog_spider import ScrapyBlogSpiderSpider
from urllib.parse import urlparse


def execute_spider(url_list: list, item_list: list):

    domain_list = []

    # URLをパースする
    for url in url_list:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        domain_list.append(domain)

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15'
    })

    process.crawl(ScrapyBlogSpiderSpider, target_domains=domain_list, target_urls=url_list, blog_scrapy_items=item_list)
    process.start() # the script will block here until the crawling is finished


if __name__ == '__main__':

    import excel_setting

    # 検索リストファイルの読み込み（全て欠損値がある行は読み込まない）
    setting_df = excel_setting.read_excel_setting("./設定ファイル.xlsx", "設定", 0, "A:D")

    url_list = []
    for i in range(0, len(setting_df)):
        url = setting_df.iloc[i]['URL']
        if url:
            url_list.append(url)

        site_name = setting_df.iloc[i]['サイト名']
        exclusion_str = setting_df.iloc[i]['除外ワード']

    execute_spider(url_list)