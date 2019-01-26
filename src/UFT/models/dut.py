#!/usr/bin/env python
# encoding: utf-8
"""Base Model for Cororado PGEM I2C functions
"""
__version__ = "0.1"
__author__ = "@fanmuzhi, @boqiling"
__all__ = ["PGEMBase"]

"""test sqlalchemy orm
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float

SQLBase = declarative_base()


class DUT_STATUS(object):
    Idle = 0  # wait to test
    Pass = 1  # pass the test
    Fail = 2  # fail in test
    Testing = 3
    ALL_TEST_PASS = 4


class DUT(SQLBase):
    __tablename__ = "dut"

    id = Column(Integer, primary_key=True)
    barcode = Column(String(30), nullable=False)
    input_voltage = Column(Float)
    charge_voltage = Column(Float)
    charge_time = Column(Integer)
    vpd_program = Column(String(5))
    cap_voltage_1 = Column(Float)
    cap_voltage_2 = Column(Float)
    cap_voltage_3 = Column(Float)
    cap_voltage_4 = Column(Float)
    cap_voltage_5 = Column(Float)
    cap_voltage_6 = Column(Float)
    capacitance_1 = Column(Integer)
    capacitance_2 = Column(Integer)
    capacitance_3 = Column(Integer)
    capacitance_4 = Column(Integer)
    capacitance_5 = Column(Integer)
    switch_voltage = Column(Float)
    test_start_time = Column(DateTime)
    test_finish_time = Column(DateTime)
    test_result = Column(String(5))
    error_code = Column(Integer)

    def to_dict(self):
        return {"barcode": self.barcode,
                "input_voltage": self.input_voltage,
                "charge_voltage": self.charge_voltage,
                "charge_time": self.charge_time,
                "vpd_program": self.vpd_program,
                "cap_voltage_1": self.cap_voltage_1,
                "cap_voltage_2": self.cap_voltage_2,
                "cap_voltage_3": self.cap_voltage_3,
                "cap_voltage_4": self.cap_voltage_4,
                "cap_voltage_5": self.cap_voltage_5,
                "cap_voltage_6": self.cap_voltage_6,
                "capacitance_1": self.capacitance_1,
                "capacitance_2": self.capacitance_2,
                "capacitance_3": self.capacitance_3,
                "capacitance_4": self.capacitance_4,
                "capacitance_5": self.capacitance_5,
                "switch_voltage": self.switch_voltage,
                "test_start_time": self.test_start_time,
                "test_finish_time": self.test_finish_time,
                "test_result": self.test_result,
                "error_code": self.error_code
                }

