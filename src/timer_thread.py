import sqlite3, time, math

from PyQt5.QtCore import QThread, pyqtSignal


class TimerThread(QThread):
    update_thread = pyqtSignal()

    def __init__(self, parent=None):
        super(TimerThread, self).__init__(parent)
        self.is_running = True

    def timer_update(self):
        while True:
            self.update_thread.emit()
            time.sleep(30)


    def run(self):
        self.timer_update()
