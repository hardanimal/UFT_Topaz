#!/usr/bin/env python
# encoding: utf-8
"""Description: pgem parallel test on UFT test fixture.
Currently supports 4 duts in parallel.
"""

__version__ = "0.1"
__author__ = "@dqli"
__all__ = ["Channel", "ChannelStates"]

import sys
sys.path.append("./src/")

import threading
from Queue import Queue
import logging
import time
import os
import traceback
import datetime

from UFT.devices import topazfct
from UFT.models import DUT_STATUS, DUT, PGEMBase
from UFT.backend.session import SessionManager
from UFT.backend import simplexml
from UFT.config import ALLOWED_PN, VPD_FILE, FCT_NO1, FCT_NO2, FCT_NO3, FCT_NO4, RESULT_DB, RESULT_LOG

logger = logging.getLogger(__name__)


class ChannelStates(object):
    EXIT = -1
    INIT = 0x0A
    CONNECT = 0x00
    SET_TYPE = 0x01
    PERFORM_TEST = 0x02


class Channel(threading.Thread):
    def __init__(self, name, barcode_list, channel_id=0):
        """initialize channel
        :param name: thread name
        :param barcode_list: list of 2D barcode of dut.
        :param channel_id: channel ID, from 0 to 7
        :return: None
        """
        # channel number for mother board.
        # 8 mother boards can be stacked from 0 to 7.
        # use 1 motherboard in default.
        self.channel = channel_id

        # setup dut_list
        self.dut_list = []
        self.barcode_list = barcode_list

        # progress bar, 0 to 100
        self.progressbar = 0

        # test cases
        self.test_cases = (["PGEM_POWER_ON", 0, "POWER_ON"],
                           ["PGEM_IIC_AND_HW_READY_CHECK", 1, "IIC_AND_HW_READY_CHECK"],
                           ["PGEM_INPUT_VOLTAGE_CHECK", 1, "INPUT_VOLTAGE_CHECK"],
                           ["PGEM_BYPASS_OUTPUT_VOLTAGE_CHECK", 1, "BYPASS_OUTPUT_VOLTAGE_CHECK"],
                           ["PGEM_CHARGING_GTG_CHECK", 1, "CHARGING_GTG_CHECK"],
                           ["PGEM_FULL_CHARGED_WAIT_CHECK", 1, "FULL_CHARGED_WAIT_CHECK"],
                           ["PGEM_CHARGE_TIME_CHECK", 1, "CHARGE_TIME_CHECK"],
                           ["PGEM_CHARGE_VOLTAGE_CHECK", 1, "CHARGE_VOLTAGE_CHECK"],
                           ["PGEM_INDIVIDUAL_VCAP_CHECK", 1, "INDIVIDUAL_VCAP_CHECK"],
                           ["PGEM_GTG_WARN_CHECK", 1, "GTG_WARN_CHECK"],
                           # ======== from here, no sequence change!!!===========
                           ["PGEM_POWER_ON", 0, "POWER_ON"],
                           ["PGEM_IIC_AND_HW_READY_CHECK", 1, "IIC_AND_HW_READY_CHECK"],
                           ["PGEM_FULL_CHARGED_WAIT_CHECK", 60, "FULL_CHARGED_WAIT_CHECK"],
                           ["PGEM_CAP_MEASURE_START_CHECK", 1, "CAP_MEASURE_START_CHECK"],
                           ["PGEM_CAP_MEASURE_WAIT_CHECK", 1, "CAP_MEASURE_WAIT_CHECK"],
                           ["PGEM_CAPACITANCE_VOLUME_CHECK", 1, "CAPACITANCE_VOLUME_CHECK"],
                           # ======== end here, no sequence change!!!===========
                           ["PGEM_CAP_MEASURE_FAULTY_CHECK", 0, "CAP_MEASURE_FAULTY_CHECK"],
                           ["PGEM_GTG_READY_CHECK", 0, "GTG_READY_CHECK"],
                           ["PGEM_VPD_PROGRAM_CHECK", 1, "VPD_PROGRAM_CHECK"],
                           ["PGEM_VPD_VEFIRY_CHECK", 1, "VPD_VEFIRY_CHECK"],
                           ["PGEM_POWER_SWITCH_AND_VOLTAGE_DROP_CHECK", 1, "POWER_SWITCH_AND_VOLTAGE_DROP_CHECK"],
                           ["PGEM_DISCHARGE_OUTPUT_VOLTAGE_CHECK", 0, "DISCHARGE_OUTPUT_VOLTAGE_CHECK"],
                           ["PGEM_DISCHARGE_END_OUTPUT_VOLTAGE_CHECK", 1, "DISCHARGE_END_OUTPUT_VOLTAGE_CHECK"]
                           )

        self.current_case_index = 0

        # 5 times cap measure retry
        self.cap_measure_count = 0
        self.retry_go_back_steps = 5

        # list to store capacitance and individual voltage
        self.c_cap = []
        self.v_cap = []

        # exit flag and queue for threading
        self.exit = False
        self.queue = Queue()
        super(Channel, self).__init__(name=name)

    def init(self):
        """ hardware initialize in when work loop starts.
        :return: None.
        """

        logger.info("Initiate Hardware of Channel {0}...".format(self.channel))
        #first setup Topaz FCT
        if self.channel == 0:
            self.topazfct = topazfct.topazfct(port=FCT_NO1, boardid=1)
        elif self.channel == 1:
            self.topazfct = topazfct.topazfct(port=FCT_NO2, boardid=2)
        elif self.channel == 2:
            self.topazfct = topazfct.topazfct(port=FCT_NO3, boardid=3)
        elif self.channel == 3:
            self.topazfct = topazfct.topazfct(port=FCT_NO4, boardid=4)

        time.sleep(1)

        # setup dut_list
        for i, bc in enumerate(self.barcode_list):
            if bc != "":
                logger.info("barcode= {0}".format(bc))
                # dut is present
                dut = PGEMBase(barcode=bc, slot=i)
                logger.info("dut: {0} SN is {1}"
                            .format(dut.slotnum, bc))
                if dut.partnumber not in ALLOWED_PN:
                    raise Exception("This partnumber {0} does not support the test".format(dut.partnumber))
                dut.status = DUT_STATUS.Idle
                dut.vpd_program = "FAIL"
                self.dut_list.append(dut)
            else:
                # dut is not loaded on fixture
                self.dut_list.append(None)
                self.config_list.append(None)

    def connect_to_board(self):
        for dut in self.dut_list:
            if dut is None:
                continue
            if dut.status != DUT_STATUS.Idle:
                continue

            if not self.topazfct.ConnectBoard():
                dut.status = DUT_STATUS.Fail
                dut.errormessage = "TOPAZ FCT board couldn't get connected."

    def set_product_type(self):
        for dut in self.dut_list:
            if dut is None:
                continue
            if dut.status != DUT_STATUS.Idle:
                continue

            if not self.topazfct.SetProType():
                dut.status = DUT_STATUS.Fail
                dut.errormessage = "TOPAZ FCT board couldn't set product type."

    def perform_test(self):
        for dut in self.dut_list:
            if dut is None:
                continue
            if dut.status != DUT_STATUS.Idle:
                continue
            dut.status = DUT_STATUS.Testing

            # set test start time
            dut.test_start_time = datetime.datetime.now()

            # the main test loop
            test_onfail_stop = False

            step = len(self.test_cases)
            while True:
                case = self.test_cases[self.current_case_index]
                logger.info(" perform test sequence = {0}, test name = {1}, delay = {2}".
                            format(self.current_case_index, case[2], case[1]))
                time.sleep(float(case[1]))
                self.progressbar += (90/step)

                param = None
                if case[0] == "PGEM_VPD_PROGRAM_CHECK":
                    param = dut.extract_data_from_file(VPD_FILE)

                # conduct test here
                ret, data = self.topazfct.Dynamic_Load_Test_By_Name(test_name=case[0], test_param=param)
                logger.info(" test result = {0}, test value = {1}".format(ret, data))

                dut.error_code = data[7]
                value = int(data[8]) + 256 * int(data[9]) + 65536 * int(data[10]) + 16777216 * int(data[11])

                # test fail
                if not ret:
                    # retry 5 time measure capacitance
                    if case[0] == "PGEM_CAPACITANCE_VOLUME_CHECK":
                        self.c_cap.append(value)
                        if self.cap_measure_count < 4:
                            self.current_case_index -= self.retry_go_back_steps
                            self.cap_measure_count += 1
                            self.progressbar -= self.retry_go_back_steps * (90/step)
                            continue
                        else:
                            test_onfail_stop = True
                            dut.errormessage = "Failed test case - {0}".format(case[0])
                            break
                    else:
                        test_onfail_stop = True
                        dut.errormessage = "Failed test case - {0}".format(case[0])
                        break

                # process test data
                if case[0] == "PGEM_CHARGE_TIME_CHECK":
                    dut.charge_time = str(value/1000.0)
                elif case[0] == "PGEM_INPUT_VOLTAGE_CHECK":
                    dut.input_voltage = str(float(value/1000.0))
                elif case[0] == "PGEM_CHARGE_VOLTAGE_CHECK":
                    dut.charge_voltage = str(float(value/1000.0))
                elif case[0] == "PGEM_INDIVIDUAL_VCAP_CHECK":
                    for i in range(6):
                        value = int(data[8+i*2]) + 256 * int(data[9+i*2])
                        self.v_cap.append(str(float(value/1000.0)))
                elif case[0] == "PGEM_CAPACITANCE_VOLUME_CHECK":
                    self.c_cap.append(value)
                elif case[0] == "PGEM_POWER_SWITCH_AND_VOLTAGE_DROP_CHECK":
                    dut.switch_voltage = str(float(value/1000.0))
                elif case[0] == "PGEM_VPD_VEFIRY_CHECK":
                    dut.vpd_program = "PASS"

                # loop end
                self.current_case_index += 1
                if self.current_case_index == step:
                    break

            # test finish
            time.sleep(1)
            self._proceed_test_result(dut)
            if not test_onfail_stop:
                dut.status = DUT_STATUS.ALL_TEST_PASS

            # set test finish time
            dut.test_finish_time = datetime.datetime.now()

    def _proceed_test_result(self, dut):
        for i in range(len(self.v_cap)):
            attr_name = "cap_voltage_" + str(i+1)
            setattr(dut, attr_name, self.v_cap[i])
        for i in range(len(self.c_cap)):
            attr_name = "capacitance_" + str(i+1)
            setattr(dut, attr_name, str(self.c_cap[i]) + "%")

    def save_db(self):
        # setup database
        # db should be prepared in cli.py

        try:
            sm = SessionManager()
            sm.prepare_db("sqlite:///" + RESULT_DB, [DUT])
            session = sm.get_session("sqlite:///" + RESULT_DB)

            for dut in self.dut_list:
                if dut is None:
                    continue
                session.add(dut)
                session.commit()
            session.close()
        except Exception as e:
            self.error(e)

    def save_file(self):
        """ save dut info to xml file
        :return:
        """

        for dut in self.dut_list:
            if dut is None:
                continue
            if not os.path.exists(RESULT_LOG):
                os.makedirs(RESULT_LOG)
            filename = dut.barcode + ".xml"
            filepath = os.path.join(RESULT_LOG, filename)
            i = 1
            while os.path.exists(filepath):
                filename = "{0}({1}).xml".format(dut.barcode, i)
                filepath = os.path.join(RESULT_LOG, filename)
                i += 1
            result = simplexml.dumps(dut.to_dict(), "entity")
            with open(filepath, "wb") as f:
                f.truncate()
                f.write(result)

    def prepare_to_exit(self):
        """ cleanup and save to database before exit.
        :return: None
        """

        for dut in self.dut_list:
            if dut is None:
                continue
            if dut.status == DUT_STATUS.ALL_TEST_PASS:
                dut.status = DUT_STATUS.Pass
                dut.test_result = "PASS"
                msg = "passed"
            else:
                dut.status = DUT_STATUS.Fail
                dut.test_result = "FAIL"
                msg = dut.errormessage
            logger.info("TEST RESULT: dut {0} ===> {1}".format(
                dut.slotnum, msg))

        # save to xml logs
        self.save_file()

    def run(self):
        """ override thread.run()
        :return: None
        """
        while not self.exit:
            state = self.queue.get()
            if state == ChannelStates.INIT:
                try:
                    logger.info("Channel: Initialize.")
                    self.init()
                    self.progressbar += 5
                except Exception as e:
                    self.error(e)
            elif state == ChannelStates.CONNECT:
                try:
                    logger.info("Channel: Connect to FCT Board.")
                    self.connect_to_board()
                    self.progressbar += 5
                except Exception as e:
                    self.error(e)
            elif state == ChannelStates.SET_TYPE:
                try:
                    logger.info("Channel: Set Product Type.")
                    self.set_product_type()
                    self.progressbar += 5
                except Exception as e:
                    self.error(e)
            elif state == ChannelStates.PERFORM_TEST:
                try:
                    logger.info("Channel: Perform Test Items.")
                    self.perform_test()
                except Exception as e:
                    self.error(e)
            elif state == ChannelStates.EXIT:
                try:
                    logger.info("Channel: Exit Test.")
                    self.prepare_to_exit()
                    self.exit = True
                except Exception as e:
                    self.error(e)
            else:
                logger.error("unknown dut state, exit...")
                self.exit = True

    def auto_test(self):
        self.queue.put(ChannelStates.INIT)
        self.queue.put(ChannelStates.CONNECT)
        self.queue.put(ChannelStates.SET_TYPE)
        self.queue.put(ChannelStates.PERFORM_TEST)
        self.queue.put(ChannelStates.EXIT)

        self.start()

    def empty(self):
        for i in range(self.queue.qsize()):
            self.queue.get()

    def error(self, e):
        exc = sys.exc_info()
        logger.error(traceback.format_exc(exc))
        self.exit = True
        raise e

    def quit(self):
        self.empty()
        self.queue.put(ChannelStates.EXIT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    barcode = ["AGIGA9IBM-501MCB02144800000002-08"]
    ch = Channel(barcode_list=barcode, channel_id=0,
                 name="UFT_CHANNEL")

    ch.auto_test()
