#!/usr/bin/env python
# encoding: utf-8
"""topazfct.py: API for TOPAZ FCT board
"""

__version__ = "0.0.1"
__author__ = '@dqli'
__all__ = ["topazfct"]

import serial, time
import logging
from UFT.config import FCT_DEBUG_INFOR

logger = logging.getLogger(__name__)
debugOut = FCT_DEBUG_INFOR


class topazfct(object):

    LastSending = ""
    LastReceiving = ""

    def __init__(self, port='COM1', baudrate=9600, **kvargs):
        timeout = kvargs.get('timeout', 1)
        parity = kvargs.get('parity', serial.PARITY_NONE)
        bytesize = kvargs.get('bytesize', serial.EIGHTBITS)
        stopbits = kvargs.get('stopbits', serial.STOPBITS_ONE)
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate,
                                     timeout=timeout, bytesize=bytesize,
                                     parity=parity, stopbits=stopbits)
        except Exception:
            raise Exception("Couldn't open serial port {0} - TOPAZ FCT Board does NOT exist or the serial port config error!".format(port))

        if not self.ser.isOpen():
            self.ser.open()
            self._cleanbuffer_()

    def __del__(self):
        self.ser.close()


    def _logging_(self, info):
        if debugOut == True:
            logger.info(info)

    def _displaylanguage_(self, content):
        display = "  transfering language: "
        for c in content:
            tmp = ord(c)
            display += "%x " % tmp
        self._logging_(display)

    def _erroroutinfor_(self):
        display = "  last sending command : "
        for c in self.LastSending:
            tmp = ord(c)
            display += "%x " % tmp
        logger.info(display)
        display = "  last receiving data : "
        for c in self.LastReceiving:
            tmp = ord(c)
            display += "%x " % tmp
        logger.info(display)

    def ConnectBoard(self):
        self._logging_("talking to FCT board...")
        cmd = 0x1F
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[2] != 0x1F:
            raise Exception("UART communication failure")
        if ret[6] != 0x99:
            return False
        else:
            return True

    def SetProType(self):
        self._logging_("set product type")
        cmd = 0x2F
        self._transfercommand_(cmd, 0x04, [0x0A, 0x00, 0x00, 0x00])
        ret = self._receiveresult_()
        if ret[6] != 0x0A:
            return False
        else:
            return True

    def Dynamic_Load_Test_By_Name(self, test_name, test_param=None):
        self._logging_("sending cmd: {0}".format(test_name))
        ret, data = eval("self."+test_name)(test_param)
        return ret, data

    def PGEM_POWER_ON(self, para):
        self._setTimeOut_(10)
        self._logging_("set power on")
        cmd = 0x50
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_IIC_AND_HW_READY_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check IIC & HW_Ready")
        cmd = 0x51
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_INPUT_VOLTAGE_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check input voltage")
        cmd = 0x52
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_BYPASS_OUTPUT_VOLTAGE_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check bypass output voltage")
        cmd = 0x53
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_CHARGING_GTG_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check charging GTG")
        cmd = 0x54
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_FULL_CHARGED_WAIT_CHECK(self, para):
        self._setTimeOut_(500)
        self._logging_("wait full charge finish")
        cmd = 0x55
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_CHARGE_TIME_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check charge time")
        cmd = 0x57
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_CHARGE_VOLTAGE_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check charge full vaoltage")
        cmd = 0x58
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_INDIVIDUAL_VCAP_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check individual vcap")
        cmd = 0x59
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_GTG_WARN_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check GTG_WARN")
        cmd = 0x5A
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_CAP_MEASURE_START_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("start cap measure")
        cmd = 0x5B
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_CAP_MEASURE_WAIT_CHECK(self, para):
        self._setTimeOut_(500)
        self._logging_("wait cap measurement finish")
        cmd = 0x5C
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_CAPACITANCE_VOLUME_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check capacitance volumn")
        cmd = 0x5E
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_CAP_MEASURE_FAULTY_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check cap measurement faulty")
        cmd = 0x5D
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_GTG_READY_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check GTG_READY")
        cmd = 0x56
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_VPD_PROGRAM_CHECK(self, para):
        self._setTimeOut_(150)
        self._logging_("program VPD")
        cmd = 0x5F
        self._transfercommand_(cmd, len(para), para)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_VPD_VEFIRY_CHECK(self, para):
        self._setTimeOut_(150)
        self._logging_("check VPD")
        cmd = 0x60
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_POWER_SWITCH_AND_VOLTAGE_DROP_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check power switch and voltage drop")
        cmd = 0x61
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_DISCHARGE_OUTPUT_VOLTAGE_CHECK(self, para):
        self._setTimeOut_(600)
        self._logging_("check discharge")
        cmd = 0x63
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def PGEM_DISCHARGE_END_OUTPUT_VOLTAGE_CHECK(self, para):
        self._setTimeOut_(10)
        self._logging_("check IIC & HW_Ready")
        cmd = 0x64
        self._transfercommand_(cmd)
        ret = self._receiveresult_()
        if ret[6] != 0x00:
            return False, ret
        else:
            return True, ret

    def _setTimeOut_(self, timeout):
        if serial.VERSION < "3.0":
            self.ser.setTimeout(timeout)
        else:
            self.ser.timeout = timeout
        time.sleep(0.2)
        pass

    def _cleanbuffer_(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def _transfercommand_(self, cmd, datalen=0, data=None):
        header0 = 0x55
        header1 = 0x77
        content = chr(header0) + chr(header1) + chr(cmd)

        if (datalen != 0) and (data is not None):
            sum = 0
            for d in data:
                sum = sum + d
            content += chr(sum & 0xFF)
        else:
            content += chr(0x01)

        content += chr(datalen & 0xFF)
        content += chr((datalen >> 8) & 0xFF)

        self.LastSending = content
        self._displaylanguage_(content)
        self._cleanbuffer_()
        self.ser.write(content)

        if (datalen != 0) and (data is not None):
            content=""
            time.sleep(1)
            for d in data:
                content += chr(d)
            self.LastSending = content
            self._displaylanguage_(content)
            self._cleanbuffer_()
            self.ser.write(content)

    def _receiveresult_(self):
        buff = []
        content = ""
        idx = 0
        datalen = 22

        while(datalen > 0):
            tmp = self.ser.read(1)
            if tmp == "":
                break
            idx += 1
            datalen -= 1
            content += tmp
            buff.append(ord(tmp))

        self.LastReceiving = content
        self._displaylanguage_(content)
        if len(buff) < 7:
            self._erroroutinfor_()
            raise Exception("Hardware is NOT ready")
        if False:
            if buff[0] != 0x55 or buff[1] != 0x77:
                self._erroroutinfor_()
                raise Exception("UART communication failure")
        return buff
