# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urlparse import urljoin
import urllib2
import sqlite3
import re

# 無視すべき単語のリスト
ignore_words = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


class Crawler:
    # データベースの名前でクローラを初期化する
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)

    def __del__(self):
        self.conn.close()

    def dbcommit(self):
        self.conn.commit()

    # エントリIDを取得する。それが存在しない場合には追加
    def get_entry_id(self, table, field, value, create_new=True):
        cr = self.conn.execute("SELECT rowid FROM %s WHERE %s='%s'"
                               % (table, field, value))
        res = cr.fetchone()
        if res is None:
            cr = self.conn.execute("INSERT INTO %s (%s) VALUES ('%s')" %
                                   (table, field, value))
            return cr.lastrowid
        else:
            return res[0]

    def add_to_index(self, url, soup):
        if self.is_indexed(url):
            print('Already Indexed ' + url)
            return
        print('Indexing ' + url)

        # 単語を取得する
        text = self.get_text_only(soup)
        words = self.separate_words(text)

        # URL id を取得する
        url_id = self.get_entry_id('urls', 'url', url)

        # それぞれの単語と、このurlのリンク
        for i in range(len(words)):
            word = words[i]
            if word in ignore_words:
                continue
            word_id = self.get_entry_id('words', 'word', word)
            self.conn.execute(
                'INSERT INTO word_location(url_id, word_id, location) VALUES (%d, %d, %d)'
                % (url_id, word_id, i))

    # HTML のページからタグのない状態でテキストを抽出する
    def get_text_only(self, soup):
        v = soup.string
        if v is None:
            c = soup.contents
            result_text = ''
            for t in c:
                subtext = self.get_text_only(t)
                result_text += subtext + '\n'
            return result_text
        else:
            return v.strip()

    # 空白以外の文字で単語を分割する
    def separate_words(self, text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '']

    # URL が既にインデックスされていたら true を返す
    def is_indexed(self, url):
        u = self.conn.execute("SELECT rowid FROM urls WHERE url = '%s'" % url).fetchone()
        if u is not None:
            v = self.conn.execute('SELECT * FROM word_location WHERE url_id = %d' % u[0])\
                    .fetchone()
            if v is not None:
                return True
        return False

    # 2つのページの間にリンクを付け加える
    def add_link_ref(self, url_from, url_to, link_text):
        words = self.separate_words(link_text)
        from_id = self.get_entry_id('urls', 'url', url_from)
        to_id = self.get_entry_id('urls', 'url', url_to)
        if from_id == to_id:
            return
        cur = self.conn.execute(
            'INSERT INTO link(from_id, to_id) VALUES (%d, %d)' % (from_id, to_id))
        link_id = cur.lastrowid
        for word in words:
            if word in ignore_words:
                continue
            word_id = self.get_entry_id('words', 'word', word)
            self.conn.cursor().execute(
                'INSERT INTO link_words(link_id, word_id) VALUES (%d, %d)' %
                (link_id, word_id))

    # ページのリストを受け取り、当たられた深さで幅優先の探索を行い
    # ページをインデクシングする
    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print('Could not open ' + str(page))
                    continue
                soup = BeautifulSoup(c.read())
                self.add_to_index(page, soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        # アンカーを取り除く
                        url = url.split('#')[0]
                        if url[0:4] == 'http' and not self.is_indexed(url):
                            newpages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, url, link_text)
                self.dbcommit()
            pages = newpages

    # データベースのテーブルを作る
    def create_index_tables(self):
        pass

    # dbのデーブル作成
    def create_index_tables(self):
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS urls(url)')
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS words(word)')
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS ' +
            'word_location(url_id, word_id, location)')
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS link(from_id integer, to_id integer)')
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS link_words(word_id, link_id)')
        self.conn.execute(
            'CREATE INDEX IF NOT EXISTS wordidx on words(word)')
        self.conn.execute(
            'CREATE INDEX IF NOT EXISTS urlidx on urls(url)')
        self.conn.execute(
            'CREATE INDEX IF NOT EXISTS wordurlidx on word_location(word_id)')
        self.conn.execute(
            'CREATE INDEX IF NOT EXISTS urltoidx on link(to_id)')
        self.conn.execute(
            'CREATE INDEX IF NOT EXISTS urlfromidx on link(from_id)')
        self.dbcommit()


class Searcher:
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)

    def __del__(self):
        self.conn.close()

    def get_match_rows(self, q):
        # クエリを作るための文字列
        field_list = 'w0.url_id'
        table_list = ''
        clause_list = ''
        word_ids = []

        # 空白で単語を分ける
        words = q.split(' ')
        table_number = 0

        for word in words:
            # 単語のIDを取得
            word_row = self.conn.execute(
                "SELECT rowid FROM words WHERE word = '%s'" % word).fetchone()
            if word_row is not None:
                word_id = word_row[0]
                word_ids.append(word_id)
                if table_number > 0:
                    table_list += ','
                    clause_list += ' and '
                    clause_list += 'w%d.url_id=w%d.url_id and ' % \
                                   (table_number - 1, table_number)
                field_list += ', w%d.location' % table_number
                table_list += 'word_location w%d' % table_number
                clause_list += 'w%d.word_id=%d' % (table_number, word_id)
                table_number += 1

        # 分割されたパーツからクエリを構築
        full_query = 'SELECT %s FROM %s WHERE %s' % \
                     (field_list, table_list, clause_list)
        print(full_query)
        cur = self.conn.execute(full_query)
        rows = [row for row in cur]

        return rows, word_ids

    def get_scored_list(self, rows, word_ids):
        total_scores = dict([(row[0], 0) for row in rows])

        # TODO ここには後ほどスコアリング関数を入れる
        weights = []

        for (weight, scores) in weights:
            for url in total_scores:
                total_scores[url] += weight * scores[url]
        return total_scores

    def get_url_name(self, id):
        return self.conn.execute(
            "SELECT url FROM urls WHERE rowid = %d" % id).fetchone()[0]

    def query(self, q):
        rows, word_ids = self.get_match_rows(q)
        scores = self.get_scored_list(rows, word_ids)
        ranked_scores = \
            sorted([(score, url) for (url, score) in scores.items()], reverse=1)

        for (score, url_id) in ranked_scores[0: 10]:
            print '%f\t%s' % (score, self.get_url_name(url_id))

# pagelist = ['https://news.ycombinator.com/']
# crawler = Crawler('')
# crawler.crawl(pagelist)
