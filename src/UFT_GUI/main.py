#!/usr/bin/env python
# encoding: utf-8

__author__ = "dqli"
__version__ = "1.0"
__email__ = "dqli@cypress.com"

import sys
sys.path.append("./src/")

import logging
import time
from PyQt4.QtGui import QApplication
from PyQt4 import QtGui, QtCore
from UFT_GUI.UFT_UiHandler import UFT_UiHandler
from UFT_GUI import log_handler

app = QApplication(sys.argv)
app.setStyle("Plastique")

try:
    import UFT
    from UFT.channel import Channel
except Exception as e:
    msg = QtGui.QMessageBox()
    msg.critical(msg, "error", e.message)


class MainWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.ui = UFT_UiHandler()
        self.ui.setupUi(self)
        self.ui.setupWidget(self)
        self.__setupSignal()

    def __setupSignal(self):

        handler = log_handler.QtHandler()
        handler.setFormatter(UFT.formatter)
        UFT.logger.addHandler(handler)
        UFT.logger.setLevel(logging.INFO)
        log_handler.XStream.stdout().messageWritten.connect(
            self.ui.append_format_data)
        self.ui.start_pushButton.clicked.connect(self.start_click)
        self.ui.search_lineEdit.returnPressed.connect(self.ui.search)
        self.ui.search_pushButton.clicked.connect(self.ui.search)

        self.u = Update()

    def start_click(self):
        try:
            # TOPAZ FCT #1
            db_1 = self.ui.barcodes_1()
            # TOPAZ FCT #2
            db_2 = self.ui.barcodes_2()
            # TOPAZ FCT #3
            db_3 = self.ui.barcodes_3()
            # TOPAZ FCT #4
            db_4 = self.ui.barcodes_4()

            self.u.loaddata(db_1, db_2, db_3, db_4)
            self.connect(self.u, QtCore.SIGNAL('progress_bar'), self.ui.progressBar.setValue)
            self.connect(self.u, QtCore.SIGNAL('is_alive'), self.ui.auto_enable_disable_widgets)
            self.connect(self.u, QtCore.SIGNAL("dut_status_1"), self.ui.set_dut_status_1)
            self.connect(self.u, QtCore.SIGNAL("dut_status_2"), self.ui.set_dut_status_2)
            self.connect(self.u, QtCore.SIGNAL("dut_status_3"), self.ui.set_dut_status_3)
            self.connect(self.u, QtCore.SIGNAL("dut_status_4"), self.ui.set_dut_status_4)
            self.connect(self.u, QtCore.SIGNAL('time_used'), self.ui.print_time)
            self.u.start()

        except Exception as e:
            msg = QtGui.QMessageBox()
            msg.critical(self, "error", e.message)


class Update(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def isEmpty(self, bclist):
        rtn = True
        for i in bclist:
            if i != "":
                rtn = False
        return rtn

    def loaddata(self, barcodes_1, barcodes_2, barcodes_3, barcodes_4):
        # TOPAZ FCT #1
        self.barcodes_1 = barcodes_1
        self.erie1_is_empty = self.isEmpty(barcodes_1)
        # TOPAZ FCT #2
        self.barcodes_2 = barcodes_2
        self.erie2_is_empty = self.isEmpty(barcodes_2)
        # TOPAZ FCT #3
        self.barcodes_3 = barcodes_3
        self.erie3_is_empty = self.isEmpty(barcodes_3)
        # TOPAZ FCT #4
        self.barcodes_4 = barcodes_4
        self.erie4_is_empty = self.isEmpty(barcodes_4)

    def getcurrentprocessbar(self, f_ch1, bar1,
                             f_ch2, bar2,
                             f_ch3, bar3,
                             f_ch4, bar4):
        if not f_ch1:
            bar1 = 100
        if not f_ch2:
            bar2 = 100
        if not f_ch3:
            bar3 = 100
        if not f_ch4:
            bar4 = 100
        return min(bar1, bar2, bar3, bar4)

    def single_run(self):
        sec_count = 0
        ch1 = Channel(barcode_list=self.barcodes_1, channel_id=0, name="UFT_CHANNEL")
        ch2 = Channel(barcode_list=self.barcodes_2, channel_id=1, name="UFT_CHANNEL")
        ch3 = Channel(barcode_list=self.barcodes_3, channel_id=2, name="UFT_CHANNEL")
        ch4 = Channel(barcode_list=self.barcodes_4, channel_id=3, name="UFT_CHANNEL")
        if not self.erie1_is_empty:
            ch1.auto_test()
        if not self.erie2_is_empty:
            ch2.auto_test()
        if not self.erie3_is_empty:
            ch3.auto_test()
        if not self.erie4_is_empty:
            ch4.auto_test()
        self.emit(QtCore.SIGNAL("is_alive"), 1)
        while ch1.isAlive() or ch2.isAlive() or ch3.isAlive() or ch4.isAlive():
            sec_count += 1
            c_process = self.getcurrentprocessbar(ch1.isAlive(), ch1.progressbar,
                                                  ch2.isAlive(), ch2.progressbar,
                                                  ch3.isAlive(), ch3.progressbar,
                                                  ch4.isAlive(), ch4.progressbar)
            self.emit(QtCore.SIGNAL("progress_bar"), c_process)
            self.emit(QtCore.SIGNAL("time_used"), sec_count)
            for dut in ch1.dut_list:
                if dut is not None:
                    self.emit(QtCore.SIGNAL("dut_status_1"), dut.slotnum,
                              dut.status)
            for dut in ch2.dut_list:
                if dut is not None:
                    self.emit(QtCore.SIGNAL("dut_status_2"), dut.slotnum,
                              dut.status)
            for dut in ch3.dut_list:
                if dut is not None:
                    self.emit(QtCore.SIGNAL("dut_status_3"), dut.slotnum,
                              dut.status)
            for dut in ch4.dut_list:
                if dut is not None:
                    self.emit(QtCore.SIGNAL("dut_status_4"), dut.slotnum,
                              dut.status)
            time.sleep(1)

        self.emit(QtCore.SIGNAL("progress_bar"), 100)
        for dut in ch1.dut_list:
            if dut is not None:
                self.emit(QtCore.SIGNAL("dut_status_1"), dut.slotnum, dut.status)
        for dut in ch2.dut_list:
            if dut is not None:
                self.emit(QtCore.SIGNAL("dut_status_2"), dut.slotnum, dut.status)
        for dut in ch3.dut_list:
            if dut is not None:
                self.emit(QtCore.SIGNAL("dut_status_3"), dut.slotnum, dut.status)
        for dut in ch4.dut_list:
            if dut is not None:
                self.emit(QtCore.SIGNAL("dut_status_4"), dut.slotnum, dut.status)

        # clean resource
        if ch1 is not None:
            ch1.save_db()
            time.sleep(0.2)
            del ch1
        if ch2 is not None:
            ch2.save_db()
            time.sleep(0.2)
            del ch2
        if ch3 is not None:
            ch3.save_db()
            time.sleep(0.2)
            del ch3
        if ch4 is not None:
            ch4.save_db()
            time.sleep(0.2)
            del ch4
        self.emit(QtCore.SIGNAL("is_alive"), 0)

    def run(self):
        self.single_run()


def main():
    # app = QApplication(sys.argv)
    # app.setStyle("Plastique")
    widget = MainWidget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
