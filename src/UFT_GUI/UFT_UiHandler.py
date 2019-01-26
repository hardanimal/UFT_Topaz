#!/usr/bin/env python
# encoding: utf-8

import sys
import re
from PyQt4 import QtGui, QtSql
from UFT_GUI.UFT_Ui import Ui_Form as UFT_UiForm
from UFT.config import RESULT_DB, RESOURCE

BARCODE_PATTERN = re.compile(r'^(?P<SN>(?P<PN>AGIGA\d{4}-\d{3}\w{3})'
                             r'(?P<VV>\d{2})(?P<YY>[1-2][0-9])'
                             r'(?P<WW>[0-4][0-9]|5[0-3])'
                             r'(?P<ID>\d{8})-(?P<RR>\d{2}))$')


class UFT_UiHandler(UFT_UiForm):
    def __init__(self, parent=None):
        UFT_UiForm.__init__(self)

        # setup log db, view and model
        self.log_db = QtSql.QSqlDatabase.addDatabase("QSQLITE", "log")
        self.log_db.setDatabaseName(RESULT_DB)
        result = self.log_db.open()
        if (not result):
            msgbox = QtGui.QMessageBox()
            msg = self.log_db.lastError().text()
            msgbox.critical(msgbox, "error", msg + " db=" + RESULT_DB)
        # self.log_tableView
        self.log_model = QtSql.QSqlTableModel(db=self.log_db)

    def setupWidget(self, wobj):
        wobj.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(RESOURCE + "logo.png")))

        # setup log model
        self.log_model.setTable("dut")

        # set log view
        self.log_tableView.setModel(self.log_model)

    def auto_enable_disable_widgets(self, ch_is_alive):
        if ch_is_alive:
            self.start_pushButton.setDisabled(True)
            self.sn_lineEdit_1.setDisabled(True)
            self.sn_lineEdit_2.setDisabled(True)
            self.sn_lineEdit_3.setDisabled(True)
            self.sn_lineEdit_4.setDisabled(True)
        else:
            self.start_pushButton.setEnabled(True)
            self.sn_lineEdit_1.setEnabled(True)
            self.sn_lineEdit_2.setEnabled(True)
            self.sn_lineEdit_3.setEnabled(True)
            self.sn_lineEdit_4.setEnabled(True)

            # back to first
            self.sn_lineEdit_1.setFocus()
            self.sn_lineEdit_1.selectAll()

    def append_format_data(self, data):
        if data:
            self.info_textBrowser.append(data)
        else:
            pass

    def set_label(self, label, slotnum, status):
        status_list = ["Idle", "Pass", "Fail", "Testing", "ALL_TEST_PASS"]
        color_list = ["background-color: wheat",
                      "background-color: green",
                      "background-color: red",
                      "background-color: yellow",
                      "background-color: green"]
        label[slotnum].setText(status_list[status])
        label[slotnum].setStyleSheet(color_list[status])

    def set_dut_status_1(self, slotnum, status):
        label = [self.label_1]
        self.set_label(label, slotnum, status)
        sn = [self.sn_lineEdit_1]
        if status == 1:
            sn[slotnum].clear()

    def set_dut_status_2(self, slotnum, status):
        label = [self.label_2]
        self.set_label(label, slotnum, status)
        sn = [self.sn_lineEdit_2]
        if status == 1:
            sn[slotnum].clear()

    def set_dut_status_3(self, slotnum, status):
        label = [self.label_3]
        self.set_label(label, slotnum, status)
        sn = [self.sn_lineEdit_3]
        if status == 1:
            sn[slotnum].clear()

    def set_dut_status_4(self, slotnum, status):
        label = [self.label_4]
        self.set_label(label, slotnum, status)
        sn = [self.sn_lineEdit_4]
        if status == 1:
            sn[slotnum].clear()

    def barcodes_1(self):
        barcodes = [str(self.sn_lineEdit_1.text())]
        for i in barcodes:
            if not i:
                i = ""
        return barcodes

    def barcodes_2(self):
        barcodes = [str(self.sn_lineEdit_2.text())]
        for i in barcodes:
            if not i:
                i = ""
        return barcodes

    def barcodes_3(self):
        barcodes = [str(self.sn_lineEdit_3.text())]
        for i in barcodes:
            if not i:
                i = ""
        return barcodes

    def barcodes_4(self):
        barcodes = [str(self.sn_lineEdit_4.text())]
        for i in barcodes:
            if not i:
                i = ""
        return barcodes

    def search(self):
        if self.search_lineEdit.text():
            self.search_result_label.setText("")
            barcode = str(self.search_lineEdit.text())

            self.log_model.record().indexOf("id")
            self.log_model.setFilter("barcode = '" + barcode + "'")
            self.log_model.select()

            if self.log_model.rowCount() == 0:
                self.search_result_label.setText("No Item Found")

            self.log_tableView.resizeColumnsToContents()

    def print_time(self, sec):
        min = sec // 60
        sec -= min * 60
        sec = str(sec) if sec >= 10 else "0" + str(sec)
        self.lcdNumber.display(str(min) + ":" + sec)


if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    w = UFT_UiHandler()
    w.setupUi(Form)
    w.setupWidget(Form)
    Form.show()
    sys.exit(a.exec_())
