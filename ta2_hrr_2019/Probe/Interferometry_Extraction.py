#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""    _ 
      /  |     | __  _ __  _
     /   |    /  |_||_|| ||
    /    |   /   |  |\ | ||_
   /____ |__/\ . |  | \|_|\_|
   __________________________ .
   
Created on Wed Jun 19 09:30:37 2019

@author: chrisunderwood
    
    Interferometry Data Extraction.
    - Turns phase shifts into density
    
"""
import numpy as np
import matplotlib as mpl
mpl.rcParams['figure.figsize'] = [6.0,4.0]
import matplotlib.pyplot as plt
import CUnderwood_Functions3 as func

import loadDataToNumpy_class
import rotateArray
import backgroundRemover_class
import createRefenceFromImage_class
import createPhase_class
import createDensity_class
import unwrapPhase_class


class Interferometry():
    def __init__(self, filePath):
        # The input is the whole file path
        self.filePath = filePath
        self.fileIdentifier = self.filePath.split("/")[-1].split("_")[0]
        
        ld = loadDataToNumpy_class.loadInDataToNumpy(filePath)
        self.im_raw = ld.loadData()
        
    def plotRawImage(self, ax = None):
        # Plot the input raw image
        if ax == None:
            flag = 1
            ax = plt.gca()
        else:
            flag = 0
        ax.set_title(self.fileIdentifier)
        ax.imshow(self.im_raw)
        if flag == 0:
            return ax
        else:
            plt.show()
        
    def rotateImage_VertFringes(self, angleDeg = True, cropRegion = [], plotting = True):
        # Run the rotateArray class, rotate so the fringes are vertical
        # By default will search for angle, but if angle is given, it will just use
        # that.
        ''' May need to give region to find fringes in '''

        rotAnal = rotateArray.rotateFringesToVertical(self.im_raw) # Initialise Class
        if angleDeg == True:
            # Finding angle of fringes
            angleDeg = rotAnal.findRotation(startIndex = cropRegion[0], 
                                endIndex = cropRegion[1],
                                horzStart = cropRegion[2], horzEnd = cropRegion[3], 
                                plotting = plotting)
            print (angleDeg)
        self.vertFringesIm = rotAnal.applyRotation(angleDeg, plotting = plotting)
        self.fringe_rotationAngle = angleDeg
    
    def removeBackground_CropROI(self, ROI_btlr, plotting = False):
        # Remove the background and crop to the region of interest
        # This also removes a blurred version, to get large scale intensity
        # flucuations in the laser spot
        bc = backgroundRemover_class.backgroundRemoverAndCrop()
        if hasattr(self, "vertFringesIm"):
            im = self.vertFringesIm
        else:
            im = self.im_raw

        bc.load_arrIntoClass(im)
        bc.blur(bc.im, 11)
        bot, top , left , right = ROI_btlr
        self.im_bg_removed = bc.sub_blurredIm(bot, top, left, right)   
        if hasattr(self, "ref"):
            self.ref = self.ref[bot: top, left: right]
        if plotting:
            plt.figure(figsize=(6,4))
            plt.imshow(self.im_bg_removed)
            plt.title("Background Removed")
            plt.colorbar()
            plt.show()
        
    def createReference(self, line_of_pchannel, width_pchannel, plotting = False):
        ref = createRefenceFromImage_class.createReference()
        
        self.line_of_pchannel = line_of_pchannel
        self.width_pchannel = width_pchannel
    
        ref.load_arrIntoClass(self.im_bg_removed, self.line_of_pchannel, self.width_pchannel)
        if plotting:
            ref.display_marking_PlasmaChannel()
    
        ref.createAveragedLineout()
        
        ref.create_ref_From_lineouts(plotting=False)
        self.ref = ref.reference_CreatedFromLineouts
        
    def loadReference(self, filepath, plotting = False):
        ld = loadDataToNumpy_class.loadInDataToNumpy(filepath)
        self.ref = ld.loadData()
        if plotting:
            plt.imshow(self.ref); plt.colorbar(); plt.title("Reference Image")
            plt.show()
   
    def crop_plasma_channel(self, plasmaChannel, plotting = True, 
                            paddingX = 10, paddingY = 10,padSize = 100):
        self.ps = createPhase_class.phaseShift()
        if hasattr(self, "im_bg_removed"):
            self.ps.load_arrIntoClass(self.im_bg_removed, self.ref)
        else:
            self.ps.load_arrIntoClass(self.im_raw, self.ref)
     
        self.ps.cropToPlasmaChannel(plasmaChannel, plotting, 
                                    paddingX = paddingX, paddingY = paddingY,
                                    padSize = padSize)
        
        # Create two variables at the top level for the cropped region.
        self.im_PlasmaChannel = self.ps.im_PlasmaChannel
        self.ref_PlasmaChannel = self.ps.ref_PlasmaChannel
                
    def createPhase(self, fftCropRegion = None,
                    plot_fft_plasma = False,
                    plotCropFFTPeak = False,
                    plot_moveFFTCentre = False,  
                    plot_fft_space = False, 
                    plot_final_result = True,
                    peakRelHeight = 0.3):
        self.ps.fft_of_plasma(plotting = plot_fft_plasma)

    
        if fftCropRegion is not None:
            # If a region is given to crop to, use it
            self.ps.crop_to_FFT_peak(fftCropRegion, GausPower = 10,
                            plot_crop_window_and_peak = plotCropFFTPeak, 
                            plot_fft_space = plot_fft_space,
                            peakRelHeight = peakRelHeight)
        else:
            # Else automatically create a crop region
            fftCropRegion = self.ps.auto_select_FT_peak(yPercRange = 0.25, xPercRange = 0.25, 
                        peakRelHeight = peakRelHeight,
                        plot_fft_space = True, plotting_cropping = False,
                        plot_found_peaks = False)
        
        self.ps.move_CroppedRegion_To_Centre(plotting = plot_moveFFTCentre) 
        self.ps.createPhase_inverseFT(plotting = plot_final_result)       

        self.phase = self.ps.phaseShift
        print ("Phase Produced")
        return fftCropRegion
    
            
    def unwrap_raw_phase(self, plotSkimage = True, plotOutput = True, plotInverting = True,
                         angle_arr_start = 15, angle_arr_end  = None,
                         mask_threshold_level = 0.2, peakThresholdHeightForAngle = 0.35):      
        
        unwrap = unwrapPhase_class.unwrapPhase()
        unwrap.load_arrIntoClass(self.phase)
        unwrap.unwrap_skimage(plotting = plotSkimage)      
        
        unwrap.correct_phase_sign(plotting = plotInverting)

        unwrap.mask_pc(peakCenterFraction = peakThresholdHeightForAngle, plotMask = True, mask_threshold_level = mask_threshold_level)
        self.phase_mask = unwrap.maskArr
        unwrap.fit_background()
        rotationAngle = unwrap.rotate_plasmaC_to_Horz(start = angle_arr_start, end = angle_arr_end)

        
        self.phase_unwrapped = unwrap.unwrappedPhase    
        if plotOutput:
            plt.imshow(self.phase_unwrapped, 
                       norm = func.MidpointNormalize(midpoint = 0),
                       cmap = plt.cm.seismic)
            plt.title("Unwrapped and background corrected phase")
            cbar = plt.colorbar()
            tickPositions = np.arange(int(self.phase_unwrapped.min() / np.pi), 1 + int(self.phase_unwrapped.max() / np.pi)) * np.pi
            cbar.set_ticks(tickPositions)
            labels = []
            for t in tickPositions:
                labels.append(r"{:1.0f}$\pi$".format(t / np.pi))
            cbar.set_ticklabels(labels)
            plt.show()      
        return rotationAngle

    def recreateElectronDensity(self, laserwavelength_m = 800e-9, mPerPix = 42.2e-6, 
                                plot_raw_abel = False, 
                                plot_n_e_result = True,
                                pixelsAroundPlasmaChannel = 10,
                                abelMethod = "hansenlaw", plot_n_e = True):       
        ne_calc = createDensity_class.deltaPhaseToDensity(laserwavelength_m = laserwavelength_m, mPerPix = mPerPix)
        ne_calc.load_arrIntoClass(self.phase_unwrapped)
            
        ne_calc.inverse_abel_transform(plotting = plot_raw_abel, method = abelMethod)
        img, lineout = ne_calc.convert_Inverse_Abel_to_Ne(
                                    pixelsAroundPlasmaChannel = pixelsAroundPlasmaChannel,
                                    plotting = plot_n_e)        
        return img, lineout
        
        
    
if __name__ == "__main__":
    # rootExperimentFolder = "/Volumes/GoogleDrive/Shared drives/Murphy Group/GeminiRR_2019/"
    # filePath = rootExperimentFolder + "20190208/20190208r011/20190208r011s024_Probe_Interfero.tiff"    
    # RotateIm = True
    # makeReference = True    
    # cropRegion = [40, 300, 100, 500] # [5, 200, 200, 450]    
    # plasmaChannel = [120, 200, 10, 380]
    # fftCropRegion = [80, 250, 350, 450]  
    # # fftCropRegion = None
    # mask_threshold_level = 0.1
    # peakThresholdHeightForAngle = 0.1
    # # The phase angle
    # start_xcoor, end_xcoor = [100, 330]    
    
    
    rootExperimentFolder = "/Volumes/GoogleDrive/My Drive/2019_Streeter_TA2/Probe_Interferometry/"
    filePath = rootExperimentFolder + "20190725/run010/Shot12.tiff"
    referencePath = rootExperimentFolder + "20190725/run010/Shot5.tiff"
    RotateIm = False    # This is only needed if making reference
    makeReference = False
    cropRegion = [500, 1000, 900, 1400] # btlr
    plasmaChannel = [195, 380, 120, 380]
    fftCropRegion = [150, 270, 333, 360]    
    fftCropRegion = None    
    mask_threshold_level = 0.8
    peakRelHeight = 0.8
    peakThresholdHeightForAngle = 0.35
    
    # The phase angle
    start_nos, end_nos = [20, 220]
    
    analysis = Interferometry(filePath)
    analysis.plotRawImage()
    if RotateIm:
        # If angle is given it just rotates this angle
        analysis.rotateImage_VertFringes(angleDeg = 0.9056665989200845)
        # analysis.rotateImage_VertFringes(cropRegion = cropRegion)
    
    if makeReference:
        analysis.removeBackground_CropROI(cropRegion, plotting = True)        
        analysis.createReference(line_of_pchannel = 160, width_pchannel = 18)
    else:
        analysis.loadReference(referencePath, plotting = True)
        analysis.removeBackground_CropROI(cropRegion, plotting = True)
    analysis.crop_plasma_channel(plasmaChannel, paddingX = 10, paddingY = 10,padSize = 100)
    analysis.createPhase(fftCropRegion = fftCropRegion, peakRelHeight = peakRelHeight,
                    plot_fft_plasma = False,
                    plotCropFFTPeak = False,
                    plot_moveFFTCentre = False,  
                    plot_fft_space = True,          # This is the important one to plot
                    plot_final_result = True
                    )
    rotationAngle = analysis.unwrap_raw_phase(angle_arr_start = start_nos, angle_arr_end = end_nos, 
                              mask_threshold_level = mask_threshold_level, peakThresholdHeightForAngle = peakThresholdHeightForAngle)
    
    ne_im, ne_lineout = analysis.recreateElectronDensity(pixelsAroundPlasmaChannel = 20)
