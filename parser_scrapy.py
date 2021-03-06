from bs4 import BeautifulSoup


class MyParser(object):
    def __init__(self, html: str, url: str):
        self._soup = BeautifulSoup(html, 'html.parser')
        self._url = url

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
        lines.append("--------------url----------------")
        lines.append(self._url)
        lines.append("-------------title---------------")
        lines.append(title_text)
        lines.append("-------------contents------------")
        for line in contents_text.splitlines():
            # 除外ワードが入っている文章を削除する
            output_flg = True
            # for exclusion_word in exclusion_list:
            #     if exclusion_word and exclusion_word in line:
            #         output_flg = False
            #         break

            if output_flg:
                lines.append(line.strip())

        out_text="\n".join(str(line) for line in lines if line)
        return out_text