import sqlite3

from PyQt5.QtCore import pyqtSignal

new_tag = pyqtSignal()


class Database:

    def __init__(self):
        self.delete_all()
        self.create_tables()

    def delete_all(self):
        conn = sqlite3.connect('db/tags.db')
        conn.execute('DELETE FROM activetags')
        conn.commit()
        conn.execute('DELETE FROM tagslog')
        conn.commit()
        conn.close()

    # vytvori databazi "tags.db" a v ni 2 tabulky (activetags a taglog)
    def create_tables(self):
        conn = sqlite3.connect('db/tags.db')
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS activetags(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                idtag TEXT NOT NULL,
                drink_name TEXT NOT NULL,
                table_number TEXT NOT NULL,
                datetime timestamp,
                status TEXT NOT NULL
            )
            '''
        )
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS tagslog(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                idtag TEXT NOT NULL,
                datetime timestamp,
                antenna TEXT NOT NULL
            )
            '''
        )
        conn.close()
        # print("Created")
        print("test db")

    def insert_data(self, idtag, datetimenow, antennanumber):
        conn = sqlite3.connect('db/tags.db')
        conn.execute(
            "INSERT INTO tagslog (idtag, datetime, antenna) VALUES (?, ?, ?)", (idtag, datetimenow, antennanumber)
        )
        conn.commit()
        conn.close()

    def print_data_log(self, sqlquery):
        conn = sqlite3.connect('db/tags.db')

        cursor = conn.execute(sqlquery)
        for row in cursor:
            print("ID = ", row[0])
            print("tagID = ", row[1])
            print("datetime = ", row[2])
            print("antenna = ", row[3])

        conn.close()

    def insert_new_tag(self, new_idtag, new_date, table_number, drink_name):
        conn = sqlite3.connect('db/tags.db')
        conn.execute(
            "INSERT into activetags (idtag, datetime, drink, table_num, status) VALUES (?, ?, ?, ?, ?)",
            (new_idtag, new_date, drink_name, table_number, "active")
        )
        conn.commit()
        print(conn.execute("SELECT * FROM activetags"))
        conn.close


def insert_data(idtag, datetimenow, antennanumber):
    conn = sqlite3.connect('db/tags.db')
    conn.execute(
        "INSERT INTO tagslog (idtag, datetime, antenna) VALUES (?, ?, ?)", (idtag, datetimenow, antennanumber)
    )
    conn.commit()
    conn.close()
    print(idtag)
    print("Insert complete")


def print_data_log(sqlquery):
    conn = sqlite3.connect('db/tags.db')

    cursor = conn.execute(sqlquery)
    for row in cursor:
        print("ID = ", row[0])
        print("tagID = ", row[1])
        print("datetime = ", row[2])
        print("antenna = ", row[3])
    conn.close()


def add_tag(new_idtag, table_number, drink_name):
    conn = sqlite3.connect('db/tags.db')
    new_id = ""
    new_date = ""
    for row in conn.execute(
            "SELECT * FROM tagslog t WHERE t.idtag LIKE ? ORDER BY t.datetime DESC LIMIT 1",
            ('_________________________' + new_idtag,)):
        new_id = row[1]
        new_date = row[2]
    new_drink = drink_name
    try:
        if new_id != "":
            if new_date != "":
                if table_number != "":
                    if drink_name != "":
                        insert_new_tag(new_id, new_date, table_number, new_drink)
    except Exception as e:
        print(e)

    conn.close


def insert_new_tag(new_idtag, new_date, table_number, drink_name):
    conn = sqlite3.connect('db/tags.db')
    conn.execute(
        "INSERT into activetags (idtag, datetime, drink_name, table_number, status) VALUES (?, ?, ?, ?, ?)",
        (new_idtag, new_date, drink_name, table_number, "active")
    )
    conn.commit()
    conn.close


def delete_tag(idtag):
    conn = sqlite3.connect('db/tags.db')
    conn.execute("DELETE FROM activetags WHERE idtag LIKE ?", ('%' + idtag,))
    conn.commit()
    conn.close()
