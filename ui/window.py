import contextlib
import math, time
import sqlite3

from typing import Any
from PyQt5 import QtWidgets, QtGui

import db.database
from ui.main_window import Ui_MainWindow
from PyQt5.QtWidgets import *
from datetime import datetime
from PyQt5.QtCore import QTimer, pyqtSlot, QModelIndex
from db.database import Database
from src.reader import Reader
from src.empty_thread import ThreadClass
from src.timer_thread import TimerThread

active_radky = 0
expired_radky = 0

class Window(QtWidgets.QMainWindow, Ui_MainWindow, QProgressBar):
    db: Database = None
    reader: Reader = None
    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Automatic Bar")
        self.setWindowIcon(QtGui.QIcon('src/beer.png'))

        self.thread={}
        self.thread[1] = Reader()
        self.thread[1].start()

        self.thread[2] = ThreadClass(parent=None)
        self.thread[2].refresh.connect(self.test_method)
        self.thread[2].start()

        self.thread[3] = TimerThread()
        self.thread[3].update_thread.connect(self.load_table_data)
        self.thread[3].start()

        self.init_db()

        self.pushButton_Add.pressed.connect(self.add_record)
        self.tableWidget_Active.setCurrentIndex(QModelIndex())
        self.pushButton_Delete.pressed.connect(self.select_row)
        self.pushButton_Edit.pressed.connect(self.update_row)

        self.tableWidget_Active.horizontalHeader().sectionClicked.connect(self.header_sort)

        self.load_table_data()

        timer = QTimer()
        timer.timeout.connect(self.time_show)

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)

    def init_db(self):
        setattr(self, "db", Database())

    def print_test(self):
        print('test')

    def connect_database(self):
        conn = sqlite3.connect("db/tags.db")
        cur = conn.cursor()
        return cur


    def add_record(self):
        global active_radky
        print(self.textLine_TagId.text())
        if self.duplicity_check(self.textLine_TagId.text()) is False:
            db.database.add_tag(self.textLine_TagId.text(), self.textLine_TableNumber.text(), self.textLine_Drink.text())
            active_radky += 1
        else:
            message_box = QMessageBox()
            message_box.critical(None, "ERROR", "Chybny vstup", QMessageBox.Ok)
        self.textLine_TagId.clear()
        self.textLine_Drink.clear()
        self.textLine_TableNumber.clear()
        self.load_table_data()

    @pyqtSlot()
    def add_row_active(self):
        global active_radky
        active_radky += 1

    def duplicity_check(self, TagId):
        with contextlib.closing(sqlite3.connect("db/tags.db")) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cur:
                    for row in cur.execute("SELECT substr(idtag, 26) as id FROM activetags"):
                        if TagId == row[0]:
                            return True
        return False

    def select_row(self):
        index_active = self.tableWidget_Active.currentIndex()
        index_expired = self.tableWidget_Expired.currentIndex()
        newin_active = self.tableWidget_Active.model().index(index_active.row(), 0)
        newin_expired = self.tableWidget_Expired.model().index(index_expired.row(), 0)
        if newin_active.row() > -1:
            idtag = self.tableWidget_Active.item(newin_active.row(), 2)
            if idtag:
                self.delete_selected_row(idtag.text(), 'active')
                print(newin_active.row())
        if newin_expired.row() > -1:
            idtag = self.tableWidget_Expired.item(newin_expired.row(), 2)
            if idtag:
                self.delete_selected_row(idtag.text(), 'expired')
                print(newin_expired.row())
        self.tableWidget_Active.setCurrentIndex(QModelIndex())
        self.tableWidget_Expired.setCurrentIndex(QModelIndex())
        self.tableWidget_Active.clearSelection()
        self.tableWidget_Expired.clearSelection()

    def delete_selected_row(self, idtag, status):
        global active_radky, expired_radky
        db.database.delete_tag(idtag)
        if status == 'active':
            active_radky -= 1
        else:
            expired_radky -= 1
        self.test_method(False)

    def update_row(self):
        global active_radky, expired_radky
        index_active = self.tableWidget_Active.currentIndex()
        index_expired = self.tableWidget_Expired.currentIndex()
        newin_active = self.tableWidget_Active.model().index(index_active.row(), 0)
        newin_expired = self.tableWidget_Expired.model().index(index_expired.row(), 0)
        if newin_active.row() > -1:
            tabnum = self.tableWidget_Active.item(newin_active.row(), 0)
            drinkn = self.tableWidget_Active.item(newin_active.row(), 1)
            tagnum = self.tableWidget_Active.item(newin_active.row(), 2)
            if tagnum:
                print(tagnum.text())
                self.textLine_TableNumber.setText(tabnum.text())
                self.textLine_Drink.setText(drinkn.text())
                self.textLine_TagId.setText(tagnum.text())
            self.delete_selected_row(tagnum.text(), 'active')
        if newin_expired.row() > -1:
            tabnum = self.tableWidget_Expired.item(newin_active.row(), 0)
            drinkn = self.tableWidget_Expired.item(newin_active.row(), 1)
            tagnum = self.tableWidget_Expired.item(newin_active.row(), 2)
            if tagnum:
                self.textLine_TableNumber.setText(tabnum.text())
                self.textLine_Drink.setText(drinkn.text())
                self.textLine_TagId.setText(tagnum.text())
            self.delete_selected_row(tagnum.text(), 'expired')
        self.tableWidget_Active.setCurrentIndex(QModelIndex())
        self.tableWidget_Expired.setCurrentIndex(QModelIndex())
        self.tableWidget_Active.clearSelection()
        self.tableWidget_Expired.clearSelection()

    def read_table_data(self, row, column, status):
        for x in range(row):
            for y in range(column):
                if status == 'active':
                    table_item = self.tableWidget_Active.item(x,y)
                else:
                    table_item = self.tableWidget_Expired.item(x, y)
        print(table_item.text())

    def cell_is_clicked(self, selected):
        print('test')
        for ix in selected.indexes():
            print('test')
            print(ix.row())

    @pyqtSlot(bool)
    def test_method(self, status):
        global active_radky, expired_radky
        if status == True:
            active_radky -= 1
            expired_radky += 1
        self.tableWidget_Active.setRowCount(0)
        self.tableWidget_Expired.setRowCount(0)
        self.tableWidget_Active.setRowCount(active_radky)
        self.tableWidget_Expired.setRowCount(expired_radky)
        self.load_table_data()

    def load_table_data(self):
        print("test thread")
        global active_radky, expired_radky
        with contextlib.closing(sqlite3.connect("db/tags.db")) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cur:
                    sqlquery = "SELECT * FROM activetags"
                    self.tableWidget_Active.setRowCount(active_radky)
                    self.tableWidget_Expired.setRowCount(expired_radky)
                    index_active = 0
                    index_expired = 0
                    conn.commit()
                    for row in cur.execute(sqlquery):
                        if row[5] == 'expired':
                            self.tableWidget_Expired.setItem(index_expired, 0, QtWidgets.QTableWidgetItem(row[3]))
                            self.tableWidget_Expired.setItem(index_expired, 1, QtWidgets.QTableWidgetItem(row[2]))
                            self.tableWidget_Expired.setItem(index_expired, 2, QtWidgets.QTableWidgetItem(str(row[1])[-4:]))
                            index_expired += 1
                            conn.commit()
                        if row[5] == 'active':
                            self.tableWidget_Active.setItem(index_active, 0, QtWidgets.QTableWidgetItem(row[3]))
                            self.tableWidget_Active.setItem(index_active, 1, QtWidgets.QTableWidgetItem(row[2]))
                            self.tableWidget_Active.setItem(index_active, 2, QtWidgets.QTableWidgetItem(str(row[1])[-4:]))
                            load_time = datetime.now() - datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S.%f')
                            load_time = math.floor(load_time.total_seconds())
                            active_time = load_time / 60
                            self.tableWidget_Active.setItem(index_active, 3,
                                                            QtWidgets.QTableWidgetItem(str(math.floor(active_time)) + "m"))
                            index_active += 1
                            conn.commit()

    def header_sort(self, c):
        if c==3:
            self.load_table_data()
        self.tableWidget_Active.sortItems(c)

    def time_on_table(self):
        cur = self.connect_database()
        sqlquery = "SELECT * FROM activetags"
        while True:
            print('Test casu')
            time.sleep(60)
            for index, row in enumerate(cur.execute(sqlquery)):
                load_time = datetime.now() - datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S.%f')
                load_time = math.floor(load_time.total_seconds())
                active_time = load_time / 60
                self.tableWidget_Active.setItem(index, 3,
                                                QtWidgets.QTableWidgetItem(str(math.floor(active_time)) + "m"))
                QApplication.processEvents()
        cur.close()

    def print_sql_into_table(self):
        Database.print_data_log(self, 'SELECT * from tagslog')

    def time_show(self):
        self.load_table_data()
        while True:
            QApplication.processEvents()
            dt = datetime.now()
            date_time_str = dt.strftime("%d.%m.%Y %H:%M:%S")
            self.label_time.setText(date_time_str)
            self.tableWidget_Active.viewport().update()
