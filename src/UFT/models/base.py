#!/usr/bin/env python
# encoding: utf-8
"""Base Model for Cororado PGEM I2C functions
"""
__version__ = "0.1"
__author__ = "@dqli"
__all__ = ["PGEMBase"]

import logging
import struct
import re
import os
from dut import DUT

logger = logging.getLogger(__name__)

# EEPROM dict for coronado
EEP_MAP = [{"name": "SN", "addr": 0x28B, "length": 8, "type": "str"},
           {"name": "MFDATE", "addr": 0x29F, "length": 4, "type": "str"}
           ]

BARCODE_PATTERN = re.compile(
    r'^(?P<SN>(?P<PN>AGIGA\w{4}-\d{3}\w{3})(?P<VV>\d{2})(?P<YY>[1-2][0-9])'
    r'(?P<WW>[0-4][0-9]|5[0-3])(?P<ID>\d{8})-(?P<RR>\d{2}))$')


class PGEMException(Exception):
    """PGEM Exception
    """
    pass


class PGEMBase(DUT):
    """PGEM Base Class, All models should be inheret from this base class.
    """

    def __init__(self, barcode, **kvargs):
        # slot number for dut on fixture location.
        # from 0 to 3, totally 4 slots in UFT
        self.slotnum = kvargs.get("slot", 0)

        # barcode
        self.barcode = barcode
        r = BARCODE_PATTERN.search(barcode)
        if r:
            self.barcode_dict = r.groupdict()
            self.partnumber = self.barcode_dict["PN"]
            self.revision = self.barcode_dict["RR"]
        else:
            raise PGEMException("Unvalide barcode.")

    @staticmethod
    def _query_map(mymap, **kvargs):
        """method to search the map (the list of dict, [{}, {}])
        :params mymap:  the map to search
                kvargs: query conditon key=value, key should be in the dict.
        :return: the dict match the query contdtion or None.
        """
        r = mymap
        for k, v in kvargs.items():
            r = filter(lambda row: row[k] == v, r)
        return r

    def extract_data_from_file(self, filepath):
        if not os.path.exists(filepath):
            raise Exception("VPD file reading error")
        buffebf = self.load_bin_file(filepath)

        id = [ord(x) for x in self.barcode_dict['ID']]
        yyww = [ord(x) for x in (self.barcode_dict['YY'] +
                                 self.barcode_dict['WW'])]

        # id == SN == Product Serial Number
        eep = self._query_map(EEP_MAP, name="SN")[0]
        buffebf[eep["addr"]: eep["addr"] + eep["length"]] = id

        # yyww == MFDATE == Manufacture Date YY WW
        eep = self._query_map(EEP_MAP, name="MFDATE")[0]
        buffebf[eep["addr"]: eep["addr"] + eep["length"]] = yyww

        return buffebf

    @staticmethod
    def load_bin_file(filepath):
        """read a file and transfer to a binary list
        :param filepath: file path to load
        """
        datas = []
        f = open(filepath, 'rb')
        s = f.read()
        for x in s:
            rdata = struct.unpack("B", x)[0]
            datas.append(rdata)
        if len(datas) != 1024:
            raise Exception("VPD file reading error")
        return datas
