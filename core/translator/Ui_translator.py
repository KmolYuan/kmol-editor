# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'translator.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.src_lang = QtWidgets.QComboBox(Form)
        self.src_lang.setEditable(True)
        self.src_lang.setObjectName("src_lang")
        self.horizontalLayout.addWidget(self.src_lang)
        self.swap_button = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.swap_button.sizePolicy().hasHeightForWidth())
        self.swap_button.setSizePolicy(sizePolicy)
        self.swap_button.setObjectName("swap_button")
        self.horizontalLayout.addWidget(self.swap_button)
        self.dest_lang = QtWidgets.QComboBox(Form)
        self.dest_lang.setEditable(True)
        self.dest_lang.setObjectName("dest_lang")
        self.horizontalLayout.addWidget(self.dest_lang)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.src_text = QtWidgets.QTextEdit(Form)
        self.src_text.setObjectName("src_text")
        self.horizontalLayout_2.addWidget(self.src_text)
        self.translate_button = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.translate_button.sizePolicy().hasHeightForWidth())
        self.translate_button.setSizePolicy(sizePolicy)
        self.translate_button.setObjectName("translate_button")
        self.horizontalLayout_2.addWidget(self.translate_button)
        self.dest_text = QtWidgets.QTextEdit(Form)
        self.dest_text.setObjectName("dest_text")
        self.horizontalLayout_2.addWidget(self.dest_text)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.swap_button.setText(_translate("Form", "Swap"))
        self.translate_button.setText(_translate("Form", "Translate"))

