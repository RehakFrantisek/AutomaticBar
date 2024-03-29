import sqlite3, time

from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal


class ThreadClass(QThread):
    refresh = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(ThreadClass, self).__init__(parent)
        self.is_running = True

    def empty_bottle_check(self):
        global new_record, new_line
        new_record = None
        new_line = None
        while True:
            time.sleep(5)
            actual_time = datetime.now()
            edited_time = (str(actual_time)[:-9]+'%',)
            try:
                conn = sqlite3.connect("db/tags.db")
                cur = conn.cursor()
                for line in cur.execute("SELECT * FROM activetags WHERE status = 'active' AND DATETIME(datetime, '+9 seconds') < ?", (actual_time,)):
                    new_line = line

                for record in cur.execute("SELECT idtag FROM activetags WHERE status = 'expired'"):
                    new_record = record
                if new_line:
                    for row in cur.execute(
                            "SELECT idtag, COUNT(*) as cnt FROM (SELECT idtag FROM (SELECT * FROM tagslog WHERE datetime LIKE ?)) GROUP BY idtag", edited_time):
                        if row[1] > 23:
                            if row[0] != new_record:
                                print(new_line[1])
                                if row[0] == new_line[1]:
                                    self.update_tag(row, conn)
                                    new_record = row[0]
                                    new_line = None
                        else:
                            print("Neni nad minutu")
            except Exception as e:
                print(e)


    def update_tag(self, row, conn):
        edit_row = (row[0],)
        conn.execute("UPDATE activetags SET status = 'expired' WHERE idtag LIKE ? AND status == 'active'", edit_row)
        conn.commit()
        self.refresh.emit(True)

    def run(self):
        time.sleep(90) #zpozdeni checkovani (osetreni nacteni hodnot na zacatku)
        self.empty_bottle_check()
