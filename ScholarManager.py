import requests
import time
from bs4 import BeautifulSoup
import sqlite3


class ScholarManager():
    def __init__(self):
        self.db = 'gscholar.db'
        self.table = 'scholars'
        self.conn = []
        self.cursor = []

    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.cursor = []

    def create_table(self):
        self.connect()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS " +
                            self.table +
                            " (id integer, name text, url text, citations integer)")
        self.disconnect()

    def create_scholar(self, name, url):
        self.connect()
        query = ("INSERT INTO " +
                 self.table +
                 " (id, name, url, citations)" +
                 " VALUES (" +
                 str(self._get_max_id() + 1) +
                 ", '" + name + "'" +
                 ", '" + url + "'" +
                 ", 0)")
        self.cursor.execute(query)
        self.conn.commit()
        self.disconnect()

    def readall_scholars(self):
        self.connect()
        query = "SELECT * FROM scholars"
        val = self.cursor.execute(query).fetchall()
        self.disconnect()
        return val

    def update_scholar_url(self, name, url):
        self.connect()
        query = ("UPDATE " +
                 self.table +
                 " SET url = '" + url + "'" +
                 " WHERE name = '" + name + "'")
        self.cursor.execute(query)
        self.conn.commit()
        self.disconnect()

    def update_scholar_citations(self, scholar_id, citations):
        self.connect()
        query = ("UPDATE " +
                 self.table +
                 " SET citations = '" + str(citations) + "'" +
                 " WHERE id = '" + str(scholar_id) + "'")
        self.cursor.execute(query)
        self.conn.commit()
        self.disconnect()

    def update_all_citations(self):
        self.connect()
        scholars = self.readall_scholars()
        for scholar in scholars:
            scholar_id = scholar[0]
            name = scholar[1]
            url = scholar[2]
            prev_citations = scholar[3]
            response = requests.get(url)
            if not response.ok:
                print("Failed to connect for: " + name)
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            new_citations = int(soup.find_all("td", {"class": "gsc_rsb_std"})[0].string)
            print(name + ": " + str(new_citations))
            if new_citations > prev_citations:
                print("+" + str(new_citations - prev_citations) + " for " + name)
                self.update_scholar_citations(scholar_id, new_citations)
            time.sleep(1)
        self.disconnect()
        return response

    def delete_scholar_by_name(self, name):
        self.connect()
        query = ("DELETE FROM " +
                 self.table +
                 " WHERE name = '" + name + "'")
        self.cursor.execute(query)
        self.conn.commit()
        self.disconnect()

    def delete_scholar_by_id(self, scholar_id):
        self.connect()
        query = ("DELETE FROM " +
                 self.table +
                 " WHERE id = '" + str(scholar_id) + "'")
        self.cursor.execute(query)
        self.conn.commit()
        self.disconnect()

    def _get_max_id(self):
        if self.conn and self.cursor:
            self.cursor.execute("SELECT MAX(id) FROM " +
                                self.table)
            val = self.cursor.fetchall()[0][0]
            if not val:
                return 0
            else:
                return val

    def get_scholar(self, name):
        self.connect()
        query = ("SELECT * FROM " +
                 self.table +
                 " WHERE name = '" +
                 name + "'")
        self.cursor.execute(query)
        val = self.cursor.fetchall()
        self.disconnect()
        return val
