# -*- coding: utf-8 -*-

"""Google translator by "goslate" module."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from py_translator import Translator
from py_translator.models import Translated, Detected
from core.QtModules import (
    pyqtSlot,
    QWidget,
)
from .Ui_translator import Ui_Form
_ts = Translator()


class TranslatorWidget(QWidget, Ui_Form):

    """Interface of Google translator."""

    def __init__(self, parent: QWidget):
        super(TranslatorWidget, self).__init__(parent)
        self.setupUi(self)

        languages = ('en', 'fr', 'de', 'ru', 'ko', 'ja', 'zh-CN', 'zh-TW')
        self.src_lang.addItems(languages + ('auto',))
        self.dest_lang.addItems(reversed(languages))

    @pyqtSlot(name='on_swap_button_clicked')
    def __swap(self):
        """Swap source and destination language."""
        tmp_text = self.src_text.toPlainText()

        tmp_lang = self.src_lang.currentText()
        if tmp_lang == 'auto':
            lang: Detected = _ts.detect(tmp_text)
            tmp_lang: str = lang.lang
        self.src_lang.setCurrentText(self.dest_lang.currentText())
        self.dest_lang.setCurrentText(tmp_lang)

        self.src_text.setPlainText(self.dest_text.toPlainText())
        self.dest_text.setPlainText(tmp_text)

    @pyqtSlot(name='on_translate_button_clicked')
    def __translate(self):
        """Translate text."""
        try:
            translated: Translated = _ts.translate(
                self.src_text.toPlainText(),
                src=self.src_lang.currentText(),
                dest=self.dest_lang.currentText()
            )
        except ValueError as error:
            self.dest_text.setPlainText(str(error))
        else:
            self.dest_text.setPlainText(translated.text)
