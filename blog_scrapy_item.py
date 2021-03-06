from urllib.parse import urlparse

class ScrapyItems(object):
    def __init__(self, site_name: str, url: str, exclusion_str: str):
        self.site_name = site_name
        self.url = url
        self.exclusion_str = exclusion_str
        self.exclusion_list = exclusion_str.split(',')
        self.domain = None

        # URLをパースする
        parsed_url = urlparse(url)
        self.domain = parsed_url.netloc