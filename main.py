import sys
from ui.window import Window
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
#if not createDbAndTables("tags.sqlite"):
    #sys.exit(1)

window = Window()
window.show()
window.time_show()

# Start the event loop.
sys.exit(app.exec_())
QCoreApplication.quit()
