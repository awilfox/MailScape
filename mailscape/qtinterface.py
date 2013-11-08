import sys
from PyQt4.QtGui import QApplication
from .qtui import MessageWindow

# very simple start-up
app = QApplication(sys.argv)
w = MessageWindow()
sys.exit(app.exec_())
