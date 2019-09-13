#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""    _
      /  |     | __  _ __  _
     /   |    /  |_||_|| ||
    /    |   /   |  |\ | ||_
   /____ |__/\ . |  | \|_|\_|
   __________________________ .

Created on Wed Jun 19 09:38:20 2019

@author: chrisunderwood

    Testing Load data to numpy

"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# Load my module of functions
import mirage_analysis
import ta2_hrr_2019.utils
ta2_hrrta2_hrr_2019.utils.setup_mirage_analysis()
from ta2_hrrta2_hrr_2019.utils.Probe import CUnderwood_Functions3 as func
from ta2_hrrta2_hrr_2019.utils.Probe import loadDataToNumpy_class
import unittest

class test_loadDataToNumpy(unittest.TestCase):

	def test_loading_tiff(self):
        #
		rootExperimentFolder = "/Volumes/GoogleDrive/Shared drives/Murphy Group/GeminiRR_2019/"
		filePath = rootExperimentFolder + "20190208/20190208r011/20190208r011s001_Probe_Interfero.tiff"

		ld = loadDataToNumpy_class.loadInDataToNumpy(filePath)
		im =ld.loadData()
		typeName = str(type(im))
		ndarray = False
		if "ndarray" in typeName:
			ndarray = True
		self.assertEqual(ndarray, True)

	def test_loading_txt(self):
        #
		rootExperimentFolder = "/Volumes/GoogleDrive/My Drive/2019 RR Analysis/BG_sub_Rot_F2Vert/"
		filePath = rootExperimentFolder + "cropROI20190211r008s103.txt"

		ld = loadDataToNumpy_class.loadInDataToNumpy(filePath)
		im =ld.loadData()
		typeName = str(type(im))
		ndarray = False
		if "ndarray" in typeName:
			ndarray = True
		self.assertEqual(ndarray, True)


if __name__ == "__main__":
	unittest.main()
