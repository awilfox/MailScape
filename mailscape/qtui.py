from PyQt4.QtCore import QObject, SIGNAL, QSize, QAbstractListModel, QModelIndex
from PyQt4.QtGui import QMainWindow, QPixmap, QIcon, QAction, QLineEdit, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QTextEdit, QSplitter, QWidget, QTabWidget, QListView, QFileDialog
from textwrap import TextWrapper
from .core import send
import os

class MessageAttachmentModel(QAbstractListModel):
    def __init__(self):
        super(MessageAttachmentModel, self).__init__()
        self.files = []

    def rowCount(self, parent):
        """ Provide the number of files attached to this message. """
        return len(self.files)

    def data(self, index, role):
        return self.files[index.row()]['name']

    def addFile(self, path):
        curr_count = len(self.files)
        self.beginInsertRows(QModelIndex(), curr_count, curr_count + 1)
        self.files.append({'name':os.path.basename(path),
                           'path':path,
                           'type':None})
        self.endInsertRows()

class MessageTextEdit(QTextEdit):
    """ Implements custom behaviour for message composing atop QTextEdit. """

    def canInsertFromMimeData(self, source):
        return source.hasText()

    def insertFromMimeData(self, source):
        text = source.text()
        paste = ''
        if getattr(self, 'wrapper', None) is None:
            self.wrapper = TextWrapper(initial_indent='> ',
                                       subsequent_indent='> ', width=78)
        for line in self.wrapper.wrap(text):
            paste += line + '\n'
        self.insertPlainText(paste)

class MessageWindow(QMainWindow):
    """ Implement most of the main/message window.

    Contains most of the UI logic.  Don't put actual behaviour in here! """

    def update_title(self, title):
        self.setWindowTitle('{} - Composition'.format(title))

    def send_message(self):
        print('Sending message')
        send(server_name='mail.wilcox-tech.com',
             to=['awilcox@wilcox-tech.com', 'corgiwolf@me.com'],
             subject=self.subject_line.text(),
             message=self.message.toPlainText(),
             files=self.attach_model.files)

#    def send_deferred(self):
#        return

    def paste_quote(self):
        self.message.paste()

    def show_addresses(self):
        return

    def show_attach_ui(self):
        self.tab_bar.setCurrentIndex(1)
        path = QFileDialog.getOpenFileName(self, 'Select attachment(s)')
        self.attach_model.addFile(path)
    
    def __init__(self):
        """ Create a new message window. """
        super(MessageWindow, self).__init__()
        self.__init_ui__()

    def __init_ui__(self):
        """ Initialise the interface. """
        self.setGeometry(300, 300, 500, 400)
        self.setWindowTitle('Composition')
        self.setWindowIcon(QIcon('res/message.ico'))

        self.__init_actions__()
        self.__init_widgets__()

        self.show()

    def __init_actions__(self):
        """ Initialise the actions (menus/toolbar) of the window. """
        menu_bar = self.menuBar()
        message_menu = menu_bar.addMenu('&Message')

        toolbar = self.addToolBar('Message actions')
        toolbar_pxm = QPixmap('res/msg_toolbar.png')

        send_action = QAction(QIcon(toolbar_pxm.copy(0, 0, 23, 20)), 'Send', self)
        send_action.setShortcut('Ctrl+Enter')
        send_action.setStatusTip('Send the message now')
        QObject.connect(send_action, SIGNAL('triggered()'), self.send_message)
        message_menu.addAction(send_action)
        toolbar.addAction(send_action)

#        defer_action = QAction('Send Later', self)
#        defer_action.setStatusTip('Queue the message for deferred delivery')
#        QObject.connect(defer_action, SIGNAL('triggered()'), self.send_deferred)
#        message_menu.addAction(defer_action)

        quote_action = QAction(QIcon(toolbar_pxm.copy(23, 0, 23, 20)), 'Quote', self)
        quote_action.setStatusTip('Paste the current clipboard text as a quoted snippet')
        QObject.connect(quote_action, SIGNAL('triggered()'), self.paste_quote)
        message_menu.addAction(quote_action)
        toolbar.addAction(quote_action)

        address_action = QAction(QIcon(toolbar_pxm.copy(46, 0, 23, 20)), 'Address', self)
        address_action.setEnabled(False)
        address_action.setStatusTip('Opens the Address Book to select recipients for the message')
        QObject.connect(address_action, SIGNAL('triggered()'), self.show_addresses)
        message_menu.addAction(address_action)
        toolbar.addAction(address_action)

        attach_action = QAction(QIcon('res/msg_attach.png'), 'Attach', self)
        attach_action.setStatusTip('Attach one or more files to the message')
        QObject.connect(attach_action, SIGNAL('triggered()'), self.show_attach_ui)
        message_menu.addAction(attach_action)
        toolbar.addAction(attach_action)

    def __init_widgets__(self):
        """ Initialise the widgets of the window. """
        # The Address/Attachment portion of the window
        self.attach_model = MessageAttachmentModel()

        attach_list = QListView()
        attach_list.setModel(self.attach_model)

        tab_bar_pxm = QPixmap('res/msg_tabbar_r.png')
        self.tab_bar = QTabWidget()
        self.tab_bar.setTabPosition(2)
        self.tab_bar.setIconSize(QSize(16, 16))
        self.tab_bar.addTab(QWidget(), QIcon(tab_bar_pxm.copy(0, 0, 16, 16)), '')
        self.tab_bar.addTab(attach_list, QIcon(tab_bar_pxm.copy(0, 16, 16, 16)), '')

        # The Composition Properties portion of the window
        self.subject_line = QLineEdit()
        self.subject_line.setPlaceholderText('Subject')
        QObject.connect(self.subject_line, SIGNAL('textEdited(QString)'), self.update_title)
        priority_label = QLabel('Priority:')
        priority_dropdown = QComboBox(self)
        priority_dropdown.addItems(['Highest','High','Normal','Low','Lowest'])

        subject_prio_layout = QHBoxLayout()
        subject_prio_layout.addWidget(self.subject_line)
#        subject_prio_layout.addStretch(1)
        subject_prio_layout.addWidget(priority_label)
        subject_prio_layout.addWidget(priority_dropdown)

        # The actual Composition portion of the window
        self.message = MessageTextEdit(self)
        
        # The bottom pane
        bottom_pane_layout = QVBoxLayout()
        bottom_pane_layout.addLayout(subject_prio_layout)
        bottom_pane_layout.addWidget(self.message)
        bottom_pane = QWidget()
        bottom_pane.setLayout(bottom_pane_layout)

        # Central widget is the splitter
        splitter = QSplitter()
        splitter.setOrientation(2)
        splitter.addWidget(self.tab_bar)
        splitter.addWidget(bottom_pane)

        self.setCentralWidget(splitter)
