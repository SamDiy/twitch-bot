import sys
from PyQt5 import QtWidgets, QtCore
import design
from db import Settings, Phrase
from threading import Thread
from bot import bot, chat_queue

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.tabs_tables = [
            {'tab': 'tab_settimgs', 'table': 'tableSetting', 'dbName': 'settings', 'dbData': Settings },
            {'tab': 'tab_phrase', 'table': 'tablePhrase', 'dbName': 'phrase', 'dbData': Phrase }
        ]
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.startButton.clicked.connect(self.on_press_start)
        self.stopButton.clicked.connect(self.on_press_stop)
        
        # dataSettings = Settings.select()
        self.fill_table(self.tableSetting, Settings)
        self.fill_table(self.tablePhrase, Phrase)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.menu = QtWidgets.QMenu(self)
        action_add = self.menu.addAction('Add row')
        action_remowe = self.menu.addAction('Delete row')
        action_add.triggered.connect(self.add_new_row)
        action_remowe.triggered.connect(self.remove_row)

        self.chat_timer = QtCore.QTimer(self)
        self.chat_timer.timeout.connect(self.check_chat_queue)
        self.chat_timer.start(1000)    

    def get_current_tab_data(self):
        return list(filter(lambda item: item['tab'] == self.tabWidget.currentWidget().objectName(), self.tabs_tables))[0]

    def show_context_menu(self, point):
        self.menu.exec(self.mapToGlobal(point))

    def fill_table(self, table, data):
        headerNames = list(data._meta.columns.keys())
        table.setColumnCount(len(headerNames))
        table.setRowCount(data.select().count())
        table.setHorizontalHeaderLabels(headerNames)
        rowCount = 0 
        for row in data.select():
            for colName in headerNames:
                cellinfo = QtWidgets.QTableWidgetItem(str(getattr(row, colName)))
                if colName == 'id':
                    cellinfo.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                    )
                table.setItem(rowCount, headerNames.index(colName), cellinfo)
            rowCount = rowCount + 1
        
        table.resizeColumnsToContents()
        table.itemChanged.connect(self.on_edit_item)

    def on_edit_item(self, item):
        tabData = self.get_current_tab_data()
        dbData = tabData['dbData']
        table = getattr(self, tabData['table'])
        fieldNames = list(dbData._meta.columns.keys())
        fieldName = fieldNames[item.column()]
        phrase = dbData[table.item(item.row(), fieldNames.index('id')).text()]
        setattr(phrase, fieldName, item.text())
        phrase.save()

    def start_bot(self):
        bot.run()
    
    def on_press_start(self):
        self.botThread = Thread(target=self.start_bot)
        self.botThread.start()
        self.add_text_to_chat("Bot start working")

    def on_press_stop(self):
        bot.stop()
        self.add_text_to_chat("Bot stop working")

    def add_new_row(self):
        item = self.get_current_tab_data()
        table = getattr(self, item['table'])
        isSelectedTable = False
        if item['dbName'] == "settings":
            isSelectedTable = True
            data = Settings
            newItem = Settings.create(name = "", value = "")
        elif item['dbName'] == "phrase":
            isSelectedTable = True
            data = Phrase
            newItem = Phrase.create(text = "", answer = "")
        
        if isSelectedTable:
            newItem.save()
            table.disconnect()
            self.fill_table(table, data)
            
    def remove_row(self):
        item = self.get_current_tab_data()
        table = getattr(self, item['table'])
        rowIndex = table.selectedIndexes()[0].row()
        dbData = item['dbData']
        fieldNames = list(dbData._meta.columns.keys())
        element = dbData[table.item(rowIndex, fieldNames.index('id')).text()]
        element.delete_instance()
        table.disconnect()
        self.fill_table(table, dbData)

    def add_text_to_chat(self, text):
       self.chatTextEdit.appendPlainText(text)

    def check_chat_queue(self):
        if not chat_queue.empty():
            self.add_text_to_chat(chat_queue.get())

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()