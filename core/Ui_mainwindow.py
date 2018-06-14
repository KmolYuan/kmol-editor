# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Y:\tmp\github\kmol-editor\core\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(646, 573)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/kmol.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.h_splitter = QtWidgets.QSplitter(self.centralWidget)
        self.h_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.h_splitter.setObjectName("h_splitter")
        self.v_splitter = QtWidgets.QSplitter(self.h_splitter)
        self.v_splitter.setOrientation(QtCore.Qt.Vertical)
        self.v_splitter.setObjectName("v_splitter")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.v_splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.highlighter_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.highlighter_label.setObjectName("highlighter_label")
        self.horizontalLayout.addWidget(self.highlighter_label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.highlighter_option = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.highlighter_option.setObjectName("highlighter_option")
        self.highlighter_option.addItem("")
        self.highlighter_option.addItem("")
        self.highlighter_option.addItem("")
        self.horizontalLayout.addWidget(self.highlighter_option)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tree_widget = QtWidgets.QTreeWidget(self.verticalLayoutWidget)
        self.tree_widget.setObjectName("tree_widget")
        self.verticalLayout.addWidget(self.tree_widget)
        self.console = QtWidgets.QTextBrowser(self.v_splitter)
        self.console.setObjectName("console")
        self.verticalLayout_2.addWidget(self.h_splitter)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 646, 22))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Edit = QtWidgets.QMenu(self.menubar)
        self.menu_Edit.setObjectName("menu_Edit")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.action_New_project = QtWidgets.QAction(MainWindow)
        self.action_New_project.setObjectName("action_New_project")
        self.action_Open = QtWidgets.QAction(MainWindow)
        self.action_Open.setObjectName("action_Open")
        self.action_Save = QtWidgets.QAction(MainWindow)
        self.action_Save.setObjectName("action_Save")
        self.action_Close = QtWidgets.QAction(MainWindow)
        self.action_Close.setObjectName("action_Close")
        self.menu_File.addAction(self.action_New_project)
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.action_Save)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Close)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Kmol editor"))
        self.highlighter_label.setText(_translate("MainWindow", "Highlighter:"))
        self.highlighter_option.setItemText(0, _translate("MainWindow", "Markdown"))
        self.highlighter_option.setItemText(1, _translate("MainWindow", "HTML"))
        self.highlighter_option.setItemText(2, _translate("MainWindow", "Python"))
        self.tree_widget.headerItem().setText(0, _translate("MainWindow", "Name"))
        self.tree_widget.headerItem().setText(1, _translate("MainWindow", "Property"))
        self.tree_widget.headerItem().setText(2, _translate("MainWindow", "Line count"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Edit.setTitle(_translate("MainWindow", "&Edit"))
        self.action_New_project.setText(_translate("MainWindow", "New project"))
        self.action_New_project.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.action_Open.setText(_translate("MainWindow", "Open"))
        self.action_Open.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.action_Save.setText(_translate("MainWindow", "Save"))
        self.action_Save.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.action_Close.setText(_translate("MainWindow", "Close"))

import icons_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

