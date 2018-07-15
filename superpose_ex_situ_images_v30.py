# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 14:14:50 2017

@author: Wagner

This version can be executed from within spyder
uses opt.minimize with global method for the fit 
problem with crop of float image in 3rd tab : double cropped
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
              QGridLayout, QVBoxLayout, QHBoxLayout,
              QTabWidget, QButtonGroup, QRadioButton, 
              QPushButton, QCheckBox, QLabel, QFileDialog, QLineEdit)
from PyQt5.QtCore import Qt # for the focus from keyboeard

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure # better do not use pyplot (but it's possible)

from scipy import ndimage as ndi
from scipy import optimize as opt
import skimage.transform as SkiTra

import numpy as np
import matplotlib.pyplot as plt

import openpyxl as xl  # for writing excel files with multi line header

class mainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)

        ############      Get screen size.
        ScrSi = QApplication.desktop().size()
        # print(ScrSi)
        ScrSiX = ScrSi.width() 
        ScrSiY = ScrSi.height() 

        ############      Define window size, position and title.
        self.left = 0
        self.top = 40
        self.width = ScrSiX - 50
        self.height = ScrSiY- self.top - 50
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.title = 'Superpose ex-situ images v30'
        self.setWindowTitle(self.title)
        
        ############      Define main tab component.
        self.tw = MyTableWidget(self)
        self.setCentralWidget(self.tw)

        ############      defining the widgets

        

        self.statusBar().showMessage('Ready')
        self.show()
     


####################################################
class MyTableWidget(QWidget):        
 
    def __init__(self, parent):   
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
 
        ######################### Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.onTabChange)
        self.tab1 = QWidget()	
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tabs.resize(300,200) 
 
        ######################### Add tabs
        self.tabs.addTab(self.tab1,"Pretreat Im1")
        self.tabs.addTab(self.tab2,"Pretreat Im2")
        self.tabs.addTab(self.tab3,"Superpose laterally")
        self.tabs.addTab(self.tab4,"Export Z-data")
 
        ######################### Create 1st tab
        ############ create the widgets
        ### For loading the image file
        self.LbFile1Name = QLabel('Click "Load File" to start')  # label (actif)
        self.BtLoadFile1 = QPushButton('2. Load file')
        self.BtLoadFile1.clicked.connect(self.Load_File1)

        ### For plotting the image
        # a figure instance to plot the loaded image file
        self.figureIM1 = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvasIM1 = FigureCanvas(self.figureIM1)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbarIM1 = NavigationToolbar(self.canvasIM1, self)
        
        # Connect a function that gets the key that is pressed
        self.canvasIM1.mpl_connect('key_press_event',self.GetKeyIm1)
        # Configure the canvas widget to process keyboard events
        self.canvasIM1.setFocusPolicy(Qt.StrongFocus) # listen to keyboard too!
        # Connect a function that gets the mouse position on every move
        self.canvasIM1.mpl_connect('motion_notify_event',self.GetMouseIm1)
        
        ### For pixel size input
        self.LbPiSi1 = QLabel('1. Linear pixel size:')  # label (passif)
        self.EdPiSi1 = QLineEdit('0.67857')  # edit 
        self.LbPiSi1Unit = QLabel('µm')  # label (passif)
        self.LbPiInfo1 = QLabel()  # label (actif)
        
        ### For display choice radiobt
        rdBtLayout = QHBoxLayout()  # layout for the radio button widget
        self.rdBtwidget1 = QWidget(self)  # radio button widget
        self.rdBtwidget1.setLayout(rdBtLayout)
    
        self.rdbtgroup1 = QButtonGroup(self.rdBtwidget1) 
        rdbtAsLoaded=QRadioButton("As loaded")
        rdbtAsLoaded.setChecked(True)   # check one button on creation
        self.rdbtgroup1.addButton(rdbtAsLoaded,0) # 0 is the id in the group
        rdbtFiltered=QRadioButton("Filtered")
        self.rdbtgroup1.addButton(rdbtFiltered,1)
        rdbtFandDwnSampled=QRadioButton("F + downsampled")
        self.rdbtgroup1.addButton(rdbtFandDwnSampled,2)
        
        rdBtLayout.addWidget(rdbtAsLoaded)
        rdBtLayout.addWidget(rdbtFiltered)
        rdBtLayout.addWidget(rdbtFandDwnSampled)
        self.rdbtgroup1.buttonClicked[int].connect(self.rdbt1Tog)
        
        ### for info labels above image
        self.LbInfo11 = QLabel()  # label (actif)
        self.LbInfo12 = QLabel()  # label (actif)
        
        ### For filtering and approval
        self.LbFilterHeader = QLabel('3. Filter to remove noise')  # label (passif)
        
        self.LbFilterMed = QLabel('3.1 Median filter : ')  # label (passif)
        self.EdFilterMed1 = QLineEdit('0')  # edit
        self.LbFilterMed1unit = QLabel('pixels ')  # label (passif)
        
        self.LbFilterGau = QLabel('3.2 Gaussian filter: ')  # label (passif)
        self.EdFilterGau1 = QLineEdit('3')  # edit
        self.LbFilterGau1unit = QLabel('pixels ')  # label (passif)
        
        self.BtUpdateFile1 = QPushButton('UPDATE')
        self.BtUpdateFile1.clicked.connect(self.Update_File1)
        
        ### for using saturation limits in the plot
        self.ckSatDisplay1 = QCheckBox('Define display z-limits')
        self.ckSatDisplay1.clicked.connect(self.DisplaySat1)
        self.LbVmin1 = QLabel('Vmin = ')  # label (passif)
        self.LbVmin1.setAlignment(Qt.AlignRight)
        self.EdVmin1 = QLineEdit('0')  # edit
        self.LbVmax1 = QLabel('Vmax = ')  # label (passif)
        self.LbVmax1.setAlignment(Qt.AlignRight)
        self.EdVmax1 = QLineEdit('5000')  # edit  
        
        ### For putting the background to zero
        self.lbZero1Def = QLabel('4. Put background to zero')
        self.ckZero1DefActivate = QCheckBox('Define background zone')
        self.ckZero1DefActivate.clicked.connect(self.Im1_backg_changed)
        
        rdBtLayoutZero1 = QHBoxLayout()  # layout for the radio button widget
        self.rdBtwidgetZero1 = QWidget(self)  # radio button widget
        self.rdBtwidgetZero1.setLayout(rdBtLayoutZero1)
    
        self.rdbtgroupZero1 = QButtonGroup(self.rdBtwidgetZero1) 
        rdbtOutside=QRadioButton("Outside the rectangle")
        self.rdbtgroupZero1.addButton(rdbtOutside,0) # 0 is the id in the group
        rdbtInside=QRadioButton("Inside the rectangle")
        self.rdbtgroupZero1.addButton(rdbtInside,1)
        rdbtOutside.setChecked(True)   # check one button on creation
        
        rdBtLayoutZero1.addWidget(rdbtOutside)
        rdBtLayoutZero1.addWidget(rdbtInside)
        
        self.LbZeroOff1 = QLabel('Zero offset: ')  # label (actif)
        
        self.BtApplyZero1 = QPushButton('Apply zero shift')
        self.BtApplyZero1.clicked.connect(self.Upd_File1_zeroShift)
        
        self.lbFile1Finished = QLabel('5. Approve end of pre-treatment')
        self.ckFile1Finished = QCheckBox('Pretreatment of file 1 finished!')
        self.ckFile1Finished.stateChanged.connect(self.approval_change)
        
        
        ############  setting the layout of the 1st tab
        grid1 = QGridLayout(self)
        grid1.setSpacing(5) #defines the spacing between widgets
        # horizontally: end of label to edit, and vertically: edit to edit

        grid1.addWidget(self.LbFile1Name, 1, 1, 1, 7)
        grid1.addWidget(self.BtLoadFile1, 1, 0)  # (object, Zeile, Spalte, rowSpan, colSpan)

        grid1.addWidget(self.rdBtwidget1, 2, 0, 1, 4)
        
        grid1.addWidget(self.LbInfo11, 3, 0, 1, 4)
        grid1.addWidget(self.LbInfo12, 4, 0, 1, 4)     

        grid1.addWidget(self.canvasIM1, 5, 0, 15, 4)
        grid1.addWidget(self.toolbarIM1, 21, 0, 1, 4)

        grid1.addWidget(self.LbPiSi1, 0, 0)
        grid1.addWidget(self.EdPiSi1, 0, 1)
        grid1.addWidget(self.LbPiSi1Unit, 0, 2)  
        
        grid1.addWidget(self.LbFilterHeader, 3, 5)
        grid1.addWidget(self.LbPiInfo1, 4, 6, 1, 3)
        grid1.addWidget(self.LbFilterMed, 5, 6)
        grid1.addWidget(self.EdFilterMed1, 5, 7)
        grid1.addWidget(self.LbFilterMed1unit, 5, 8)
        grid1.addWidget(self.LbFilterGau, 6, 6)
        grid1.addWidget(self.EdFilterGau1, 6, 7)
        grid1.addWidget(self.LbFilterGau1unit, 6, 8)
        grid1.addWidget(self.BtUpdateFile1, 7, 5)
        
        # for using saturation limits in the plot
        grid1.addWidget(self.ckSatDisplay1,9,5)
        grid1.addWidget(self.LbVmin1,10,5)  # label (passif)
        grid1.addWidget(self.EdVmin1,10,6)  # edit
        grid1.addWidget(self.LbVmax1,11,5)  # label (passif)
        grid1.addWidget(self.EdVmax1,11,6) # edit
        
        grid1.addWidget(self.lbZero1Def, 13,5)
        grid1.addWidget(self.ckZero1DefActivate, 14, 5)
        grid1.addWidget(self.rdBtwidgetZero1, 14, 6,1,3)
        grid1.addWidget(self.LbZeroOff1, 15, 5,1,2)
        grid1.addWidget(self.BtApplyZero1, 15, 7)
        
        grid1.addWidget(self.lbFile1Finished, 17,5)
        grid1.addWidget(self.ckFile1Finished, 17, 7)
        
        self.tab1.setLayout(grid1)
        # grid.setRowStretch(2, 1)  
        
        ######################### Create 2nd tab
        ############ create the widgets
        ### For loading the image file
        self.LbFile2Caption = QLabel('Name of file 2:')  # label (passif)
        self.LbFile2Name = QLabel('Click "Load File" to start')  # label (actif)
        self.BtLoadFile2 = QPushButton('1. Load file')
        self.BtLoadFile2.clicked.connect(self.Load_File2)

        ### For plotting the image
        # a figure instance to plot the loaded image file
        self.figureIM2 = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvasIM2 = FigureCanvas(self.figureIM2)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbarIM2 = NavigationToolbar(self.canvasIM2, self)
        
        # Connect a function that gets the key that is pressed
        self.canvasIM2.mpl_connect('key_press_event',self.GetKeyIm2)
        # Configure the canvas widget to process keyboard events
        self.canvasIM2.setFocusPolicy(Qt.StrongFocus) # listen to keyboard too!
        # Connect a function that gets the mouse position on every move
        self.canvasIM2.mpl_connect('motion_notify_event',self.GetMouseIm2)
        
        ### For pixel size input
        self.LbPiSi2 = QLabel('2. Linear pixel size:')  # label (passif)
        self.EdPiSi2 = QLineEdit('1.08')  # edit 
        self.LbPiSi2Unit = QLabel('µm')  # label (passif)
        self.LbPiInfo2 = QLabel()  # label (actif)
        
        ### For display choice radiobt
        rdBtLayout = QHBoxLayout()  # layout for the radio button widget
        self.rdBtwidget2 = QWidget(self)  # radio button widget
        self.rdBtwidget2.setLayout(rdBtLayout)
    
        self.rdbtgroup2 = QButtonGroup(self.rdBtwidget2) 
        rdbtAsLoaded=QRadioButton("As loaded")
        rdbtAsLoaded.setChecked(True)   # check one button on creation
        self.rdbtgroup2.addButton(rdbtAsLoaded,0) # 0 is the id in the group
        rdbtFiltered=QRadioButton("Filtered")
        self.rdbtgroup2.addButton(rdbtFiltered,1)
        rdbtFandDwnSampled=QRadioButton("F + downsampled")
        self.rdbtgroup2.addButton(rdbtFandDwnSampled,2)
        
        rdBtLayout.addWidget(rdbtAsLoaded)
        rdBtLayout.addWidget(rdbtFiltered)
        rdBtLayout.addWidget(rdbtFandDwnSampled)
        self.rdbtgroup2.buttonClicked[int].connect(self.rdbt2Tog)
        
        ### for info labels above image
        self.LbInfo21 = QLabel()  # label (actif)
        self.LbInfo22 = QLabel()  # label (actif)
        
        ### For filtering and approval
        self.LbFilterHeader = QLabel('3. Filter to remove noise')  # label (passif)
        
        self.LbFilterMed = QLabel('3.1 Median filter: ')  # label (passif)
        self.EdFilterMed2 = QLineEdit('0')  # edit
        self.LbFilterMed2unit = QLabel('pixels ')  # label (passif)
        
        self.LbFilterGau = QLabel('3.2 Gaussian filter: ')  # label (passif)
        self.EdFilterGau2 = QLineEdit('3')  # edit
        self.LbFilterGau2unit = QLabel('pixels ')  # label (passif)
        
        self.BtUpdateFile2 = QPushButton('UPDATE')
        self.BtUpdateFile2.clicked.connect(self.Update_File2)
                
        ### for using saturation limits in the plot
        self.ckSatDisplay2 = QCheckBox('Define display z-limits')
        self.ckSatDisplay2.clicked.connect(self.DisplaySat2)
        self.LbVmin2 = QLabel('Vmin = ')  # label (passif)
        self.LbVmin2.setAlignment(Qt.AlignRight)
        self.EdVmin2 = QLineEdit('0')  # edit
        self.LbVmax2 = QLabel('Vmax = ')  # label (passif)
        self.LbVmax2.setAlignment(Qt.AlignRight)
        self.EdVmax2 = QLineEdit('5000')  # edit  

        ### For putting the background to zero
        self.lbZero2Def = QLabel('4. Put background to zero')
        self.ckZero2DefActivate = QCheckBox('Define background zone')
        self.ckZero2DefActivate.clicked.connect(self.Im2_backg_changed)
        
        rdBtLayoutZero2 = QHBoxLayout()  # layout for the radio button widget
        self.rdBtwidgetZero2 = QWidget(self)  # radio button widget
        self.rdBtwidgetZero2.setLayout(rdBtLayoutZero2)
    
        self.rdbtgroupZero2 = QButtonGroup(self.rdBtwidgetZero2) 
        rdbtOutside=QRadioButton("Outside the rectangle")
        self.rdbtgroupZero2.addButton(rdbtOutside,0) # 0 is the id in the group
        rdbtInside=QRadioButton("Inside the rectangle")
        self.rdbtgroupZero2.addButton(rdbtInside,1)
        rdbtOutside.setChecked(True)   # check one button on creation
        
        rdBtLayoutZero2.addWidget(rdbtOutside)
        rdBtLayoutZero2.addWidget(rdbtInside)
        
        self.LbZeroOff2 = QLabel('Zero offset: ')  # label (actif)
        
        self.BtApplyZero2 = QPushButton('Apply zero shift')
        self.BtApplyZero2.clicked.connect(self.Upd_File2_zeroShift)
        
        self.lbFile2Finished = QLabel('5. Approve end of pre-treatment')
        self.ckFile2Finished = QCheckBox('Pretreatment of file 2 finished!')
        self.ckFile2Finished.stateChanged.connect(self.approval_change)
        
        ############  setting the layout of the 2nd tab
        grid2 = QGridLayout(self)
        grid2.setSpacing(5) #defines the spacing between widgets
        # horizontally: end of label to edit, and vertically: edit to edit
        
        grid2.addWidget(self.LbFile2Name, 1, 1, 1, 7)
        grid2.addWidget(self.BtLoadFile2, 1, 0)  # (object, Zeile, Spalte, rowSpan, colSpan)

        grid2.addWidget(self.rdBtwidget2,  2, 0, 1, 4)
        
        grid2.addWidget(self.LbInfo21, 3, 0, 1, 4)
        grid2.addWidget(self.LbInfo22, 4, 0, 1, 4)
        
        grid2.addWidget(self.canvasIM2, 5, 0, 15, 4)
        grid2.addWidget(self.toolbarIM2, 21, 0, 1, 4)

        grid2.addWidget(self.LbPiSi2, 0, 0)
        grid2.addWidget(self.EdPiSi2, 0, 1)
        grid2.addWidget(self.LbPiSi2Unit, 0, 2)
        
        grid2.addWidget(self.LbFilterHeader, 3, 5)
        grid2.addWidget(self.LbPiInfo2, 4, 6, 1, 3)
        grid2.addWidget(self.LbFilterMed, 5, 6)
        grid2.addWidget(self.EdFilterMed2, 5, 7)
        grid2.addWidget(self.LbFilterMed2unit, 5, 8)
        grid2.addWidget(self.LbFilterGau, 6, 6)
        grid2.addWidget(self.EdFilterGau2, 6, 7)
        grid2.addWidget(self.LbFilterGau2unit, 6, 8)
        grid2.addWidget(self.BtUpdateFile2, 7, 5)
        
        # for using saturation limits in the plot
        grid2.addWidget(self.ckSatDisplay2,9,5)
        grid2.addWidget(self.LbVmin2,10,5)  # label (passif)
        grid2.addWidget(self.EdVmin2,10,6)  # edit
        grid2.addWidget(self.LbVmax2,11,5)  # label (passif)
        grid2.addWidget(self.EdVmax2,11,6) # edit
        
        grid2.addWidget(self.lbZero2Def, 13,5)
        grid2.addWidget(self.ckZero2DefActivate, 14, 5)
        grid2.addWidget(self.rdBtwidgetZero2, 14, 6,1,3)
        grid2.addWidget(self.LbZeroOff2, 15, 5,1,2)
        grid2.addWidget(self.BtApplyZero2, 15, 7)
        
        grid2.addWidget(self.lbFile2Finished, 17, 5)
        grid2.addWidget(self.ckFile2Finished, 17, 7)

        self.tab2.setLayout(grid2)
        # grid.setRowStretch(2, 1)  
              
        ######################### Create 3rd tab
        ############ create the widgets
        
        ### For display choice radiobt
        rdBtLayout = QHBoxLayout()  # layout for the radio button widget
        self.rdBtwidget3 = QWidget(self)  # radio button widget
        self.rdBtwidget3.setLayout(rdBtLayout)
    
        self.rdbtgroup3 = QButtonGroup(self.rdBtwidget3) 
        rdbtRef=QRadioButton("Reference image")
        self.rdbtgroup3.addButton(rdbtRef,0) # 0 is the id in the group
        rdbtFlo=QRadioButton("Floating image")
        self.rdbtgroup3.addButton(rdbtFlo,1)
        rdbtDiffFlo_m_Ref=QRadioButton("Difference: Float-Ref")
        self.rdbtgroup3.addButton(rdbtDiffFlo_m_Ref,2)
        rdbtRef.setChecked(True)   # check one button on creation
        
        rdBtLayout.addWidget(rdbtRef)
        rdBtLayout.addWidget(rdbtFlo)
        rdBtLayout.addWidget(rdbtDiffFlo_m_Ref)
        self.rdbtgroup3.buttonClicked[int].connect(self.rdbt3Tog)
        
        ### For plotting the images
        # a label to give information on the dispalyed file
        self.LbDiffFileInfo = QLabel('File info: ')  # label (actif)
        # a figure instance to plot the difference image
        self.figureIMdi = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvasIMdi = FigureCanvas(self.figureIMdi)
        
        # Connect a function that gets the key that is pressed
        self.canvasIMdi.mpl_connect('key_press_event',self.GetKey)
        # Configure the canvas widget to process keyboard events
        self.canvasIMdi.setFocusPolicy(Qt.StrongFocus) # listen to keyboard too!
        
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbarIMdi = NavigationToolbar(self.canvasIMdi, self)
        
        ### For input of transformation parameters
        self.LbTransformHeader = QLabel('4. Initial transformation parameters of float image:')  # label (passif)
        
        self.LbZHead = QLabel('4.1 Vertical scaling: ')  # label (passif)
        self.LbZOffs = QLabel('Offset: ')  # label (passif)
        self.EdZOffs = QLineEdit('0')  # edit
        self.LbZOffsUnit = QLabel('grey levels after normalization')  # label (passif)
        self.LbZFact = QLabel('Factor: ')  # label (passif)
        self.EdZFact = QLineEdit('1')  # edit
        self.LbZFactUnit = QLabel('  (GLnew = (GL+Offs)*Fact)')  # label (passif)

        self.LbLatHead = QLabel('4.2 Lateral transformation: ')  # label (passif)        
        self.ckLatXFlip = QCheckBox('Flip left/right')
        
        self.LbLatRot = QLabel('Rotate between: ')  # label (passif)
        self.EdLatRot = QLineEdit('-140')  # edit
        self.LbLatRot2 = QLabel('and')  # label (passif)        
        self.EdLatRotMax = QLineEdit('5')  # edit
        self.LbLatRotUnit = QLabel('° around center ')  # label (passif)
        
        self.LbLatXShi = QLabel('Shift hor. between: ')  # label (passif)
        self.EdLatXShi = QLineEdit('-30')  # edit
        self.LbLatXShi2 = QLabel('and')  # label (passif)
        self.EdLatXShiMax = QLineEdit('-6')  # edit
        self.LbLatXShiUnit = QLabel('pixels ')  # label (passif)
        
        self.LbLatYShi = QLabel('shift ver. between: ')  # label (passif)
        self.EdLatYShi = QLineEdit('45')  # edit
        self.LbLatYShi2 = QLabel('and')  # label (passif)
        self.EdLatYShiMax = QLineEdit('6')  # edit
        self.LbLatYShiUnit = QLabel('pixels ')  # label (passif)
        
        self.BtUpdateTransfo = QPushButton('UPDATE to Min.')
        self.BtUpdateTransfo.clicked.connect(self.Update_Transform)
        
        ### For cropping
        self.ckCropIt = QCheckBox('Crop margins in pixels')
        self.ckCropIt.clicked.connect(self.Crop_changed)
        self.EdCropUp = QLineEdit('50')  # edit
        self.EdCropDwn = QLineEdit('50')  # edit
        self.EdCropL = QLineEdit('50')  # edit
        self.EdCropR = QLineEdit('50')  # edit
        
        ### For masking
        self.ckMaskActivateIt = QCheckBox('Use mask')
        self.ckMaskActivateIt.clicked.connect(self.Mask_changed)
        
        rdBtLayoutMsk = QHBoxLayout()  # layout for the radio button widget
        self.rdBtwidgetMsk = QWidget(self)  # radio button widget
        self.rdBtwidgetMsk.setLayout(rdBtLayoutMsk)
    
        self.rdbtgroupMsk = QButtonGroup(self.rdBtwidgetMsk) 
        rdbtAdd=QRadioButton("Add pixels")
        self.rdbtgroupMsk.addButton(rdbtAdd,0) # 0 is the id in the group
        rdbtRemove=QRadioButton("Remove pixels")
        self.rdbtgroupMsk.addButton(rdbtRemove,1)
        rdbtAdd.setChecked(True)   # check one button on creation
        
        rdBtLayoutMsk.addWidget(rdbtAdd)
        rdBtLayoutMsk.addWidget(rdbtRemove)
        # self.rdbtgroupMsk.buttonClicked[int].connect(self.rdbtMskTog)
        
        ### For evaluation
        self.LbChi2caption = QLabel('Chi² / pixNum: ')  # label (passif)
        self.LbChi2 = QLabel('1e50')  # label (actif)
        
        ### For fitting
        self.BtFit = QPushButton('Start FIT')
        self.BtFit.clicked.connect(self.Make_fit)
        
        
        ############  setting the layout of the 3rd tab
        grid3 = QGridLayout(self)
        grid3.setSpacing(5) #defines the spacing between widgets
        # horizontally: end of label to edit, and vertically: edit to edit

        # (object, Zeile, Spalte, rowSpan, colSpan)

        grid3.addWidget(self.rdBtwidget3, 0, 1, 1, 4)
        grid3.addWidget(self.LbDiffFileInfo, 1, 0, 1, 6)
        grid3.addWidget(self.canvasIMdi, 2, 0, 12, 6)
        grid3.addWidget(self.toolbarIMdi, 15, 0, 1, 6)

        grid3.addWidget(self.ckCropIt, 0, 6,1,2)
        grid3.addWidget(self.EdCropUp, 0, 8)
        grid3.addWidget(self.EdCropDwn, 2, 8)
        grid3.addWidget(self.EdCropL, 1, 7)
        grid3.addWidget(self.EdCropR, 1, 9)
        
        grid3.addWidget(self.ckMaskActivateIt,3,6)
        grid3.addWidget(self.rdBtwidgetMsk, 3, 7, 1, 3)
       
        grid3.addWidget(self.LbTransformHeader, 4, 6,1,3)
        
        grid3.addWidget(self.LbZHead, 5, 6, 1 ,4)
        grid3.addWidget(self.LbZOffs, 6, 7)
        grid3.addWidget(self.EdZOffs, 6, 8)
        grid3.addWidget(self.LbZOffsUnit, 6, 9,1,3)
        grid3.addWidget(self.LbZFact, 7, 7)
        grid3.addWidget(self.EdZFact, 7, 8)
        grid3.addWidget(self.LbZFactUnit, 7, 9,1,3)
        
        grid3.addWidget(self.LbLatHead, 9, 6, 1 ,3)
        grid3.addWidget(self.ckLatXFlip, 10, 8,1,2)
        grid3.addWidget(self.LbLatRot, 11, 7)
        grid3.addWidget(self.EdLatRot, 11, 8)
        grid3.addWidget(self.LbLatRot2, 11, 9)
        grid3.addWidget(self.EdLatRotMax, 11, 10)
        grid3.addWidget(self.LbLatRotUnit, 11, 11)        
        grid3.addWidget(self.LbLatXShi, 12, 7)
        grid3.addWidget(self.EdLatXShi, 12, 8)
        grid3.addWidget(self.LbLatXShi2, 12, 9)
        grid3.addWidget(self.EdLatXShiMax, 12, 10)
        grid3.addWidget(self.LbLatXShiUnit, 12, 11)        
        grid3.addWidget(self.LbLatYShi, 13, 7)
        grid3.addWidget(self.EdLatYShi, 13, 8)
        grid3.addWidget(self.LbLatYShi2, 13, 9)
        grid3.addWidget(self.EdLatYShiMax, 13, 10)
        grid3.addWidget(self.LbLatYShiUnit, 13, 11)        
        
        grid3.addWidget(self.BtUpdateTransfo, 15, 8)
        grid3.addWidget(self.LbChi2caption, 14, 7)
        grid3.addWidget(self.LbChi2, 14, 8)
        grid3.addWidget(self.BtFit, 15,9,1,2)

        self.tab3.setLayout(grid3)
        # grid.setRowStretch(2, 1)
        
        ######################### Create 4th tab
        ############ create the widgets
        
        ### For info on the images
        self.LbIMinfo1 = QLabel(
          'Files:                                      Image 1         Image2')
        self.LbIMinfo2 = QLabel(
          'Filenames:                 ')
        self.LbIMinfo3 = QLabel(
          'Shapes after downsampling: ')
        self.LbIMinfo4 = QLabel(
          'Roles:                                     reference       floating')
        # Modify these labels in approval_change
        
        ### For display choice radiobt
        self.LbText = QLabel('Choose file to display:')
        rdBtLayout = QHBoxLayout()  # layout for the radio button widget
        self.rdBtwidgetF = QWidget(self)  # radio button widget
        self.rdBtwidgetF.setLayout(rdBtLayout)
        self.rdbtgroupF = QButtonGroup(self.rdBtwidgetF) 
        rdbtIm1=QRadioButton("Image 1")
        self.rdbtgroupF.addButton(rdbtIm1,0) # 0 is the id in the group
        rdbtIm2=QRadioButton("Image 2")
        self.rdbtgroupF.addButton(rdbtIm2,1)
        rdbtIm1.setChecked(True)   # check one button on creation
        rdBtLayout.addWidget(rdbtIm1)
        rdBtLayout.addWidget(rdbtIm2)
        self.rdbtgroupF.buttonClicked[int].connect(self.rdbtFinalTog)
        
        ### For plotting the cropped images
        # a figure instance to plot on
        self.figureImFinal = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvasImFinal = FigureCanvas(self.figureImFinal)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbarImFinal = NavigationToolbar(self.canvasImFinal, self)
        
        ### For cropping
        self.ckCropItF = QCheckBox('Crop margins of ref. image in pixels')
        self.ckCropItF.clicked.connect(self.CropF_changed)
        self.EdCropFUp = QLineEdit('75')  # edit
        self.EdCropFDwn = QLineEdit('75')  # edit
        self.EdCropFL = QLineEdit('70')  # edit
        self.EdCropFR = QLineEdit('55')  # edit
        
        ### For plotting the pixel cloud
        # a figure instance to plot on
        self.figurePiCloud = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvasPiCloud = FigureCanvas(self.figurePiCloud)    
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbarPiCloud = NavigationToolbar(self.canvasPiCloud, self)
        
        ### For x-axis choice radiobt
        self.LbText2 = QLabel('Choose horizontal axis:') 
        rdBtLayout = QHBoxLayout()  # layout for the radio button widget
        self.rdBtwidgetX = QWidget(self)  # radio button widget
        self.rdBtwidgetX.setLayout(rdBtLayout)
        self.rdbtgroupX = QButtonGroup(self.rdBtwidgetX) 
        rdbtIm1asX = QRadioButton("Image 1 as X")
        self.rdbtgroupX.addButton(rdbtIm1asX,0) # 0 is the id in the group
        rdbtIm2asX = QRadioButton("Image 2 ax X")
        self.rdbtgroupX.addButton(rdbtIm2asX,1)
        rdbtIm1asX.setChecked(True)   # check one button on creation
        rdBtLayout.addWidget(rdbtIm1asX)
        rdBtLayout.addWidget(rdbtIm2asX)
        # self.rdbtgroupX.buttonClicked[int].connect(self.rdbtXTog)
        
        # For Normalisation
        self.ckNorm1 = QCheckBox('Normalize image 1 to: ')
        self.EdNorm1to = QLineEdit('1')  # edit
        self.ckNorm2 = QCheckBox('Normalize image 2 to: ')
        self.EdNorm2to = QLineEdit('1')  # edit
        
        # For axis labels? 
        # ed
        # ed
        
        ### For updating the pixel cloud
        self.BtPiCloUpd = QPushButton('Update pixel cloud')
        self.BtPiCloUpd.clicked.connect(self.Update_PixelCloud)
        
        ### For histogram display (if wanted/needed)
        # Figure
        # def of bin by centerX and widthX
        
        
        ############  setting the layout of the 4th tab
        grid4 = QGridLayout(self)
        grid4.setSpacing(5) #defines the spacing between widgets
        # horizontally: end of label to edit, and vertically: edit to edit

        # (object, Zeile, Spalte, rowSpan, colSpan)

        grid4.addWidget(self.LbIMinfo1, 0, 0, 1, 6)
        grid4.addWidget(self.LbIMinfo2, 1, 0, 1, 6)
        grid4.addWidget(self.LbIMinfo3, 2, 0, 1, 6)
        grid4.addWidget(self.LbIMinfo4, 3, 0, 1, 6)

        grid4.addWidget(self.ckCropItF, 5, 0,1,3)
        grid4.addWidget(self.EdCropFUp, 6, 2)
        grid4.addWidget(self.EdCropFDwn, 8, 2)
        grid4.addWidget(self.EdCropFL, 7, 1)
        grid4.addWidget(self.EdCropFR, 7, 3)
        
        grid4.addWidget(self.LbText, 9, 0, 1, 2)
        grid4.addWidget(self.rdBtwidgetF, 9, 2, 1, 3)
        
        grid4.addWidget(self.canvasImFinal, 10, 0, 12, 6)
        grid4.addWidget(self.toolbarImFinal, 23, 0, 1, 6)
        
        grid4.addWidget(self.LbText2, 0, 7)
        grid4.addWidget(self.rdBtwidgetX, 0, 8, 1, 3)
        
        grid4.addWidget(self.ckNorm1, 2, 7)
        grid4.addWidget(self.EdNorm1to, 2, 8)
        grid4.addWidget(self.ckNorm2, 2, 10)
        grid4.addWidget(self.EdNorm2to, 2, 11)
        # zero is defined during pre-processing
        
        grid4.addWidget(self.canvasPiCloud, 3, 7, 12, 10)
        grid4.addWidget(self.toolbarPiCloud, 16, 7, 1, 6)
        
        grid4.addWidget(self.BtPiCloUpd, 17,9,1,2)

        self.tab4.setLayout(grid4)
        # grid.setRowStretch(2, 1)  
    
        ######################### Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
        global testNum # number of the LIC test (for sanity check)
        global Hval # Total height (nm) of the profile to be extracted from 
        # the info in the filename (for pixelcloud)
        global GLval # size of one grey level step to be calculated from 
        # the info in the filename and the GL extend of the file (for pixelcloud)
        global Fval # Peak fluence of the test to be extracted from 
        # the info in the filename (for pixelcloud)
        testNum = -1000
        Hval = -1000.0
        GLval = -1000.0
        Fval = -1000.0
                

    def rdbt1Tog(self,newChoice):
        global axIM1
        
        if newChoice == 0:
            ImDisp1 = im1 # view only
        elif newChoice == 1:
            ImDisp1 = im1fi # view only
        else:
            ### display the downsampled image
            if flo == '1':
                ImDisp1 = imFloOri # view only
            else:
                ImDisp1 = im1fi # view only      
        
        # Clear the figure from earlier uses
        self.figureIM1.clear()
        # prepare the axis
        axIM1 = self.figureIM1.add_subplot(111)
        axIM1.axis("off")
        cax = axIM1.imshow(ImDisp1, cmap='jet',vmin = Vmi1, vmax = Vma1)
        # common color maps: gray, hot, hsv, inferno, gist_ncar
        self.figureIM1.colorbar(cax, orientation='vertical')
        # self.figureIM.tight_layout()
        XX, YY = np.meshgrid(range(ImDisp1.shape[1]),range(ImDisp1.shape[0]))
        CentroXimFloOri = int(np.round((XX*ImDisp1).sum()/ImDisp1.sum()))
        CentroYimFloOri = int(np.round((YY*ImDisp1).sum()/ImDisp1.sum()))
        axIM1.plot(
                [CentroXimFloOri-20, CentroXimFloOri+20], 
                [CentroYimFloOri, CentroYimFloOri], 
                color='w', linestyle='-', linewidth=2)
        axIM1.plot(
                [CentroXimFloOri, CentroXimFloOri], 
                [CentroYimFloOri-20, CentroYimFloOri+20], 
                color='w', linestyle='-', linewidth=2)
        
        # refresh canvas
        self.canvasIM1.draw()
        # So it seems that globals can be read even without declaration in the 
        # function!!!

            
    def rdbt2Tog(self,newChoice):
        global axIM2
        
        if newChoice == 0:
            ImDisp2 = im2 # view only
        elif newChoice == 1:
            ImDisp2 = im2fi # view only
        else:
            ### display the downsampled image
            if flo == '2':
                ImDisp2 = imFloOri # view only
            else:
                ImDisp2 = im2fi # view only      
        
        # Clear the figure from earlier uses
        self.figureIM2.clear()
        # prepare the axis
        axIM2 = self.figureIM2.add_subplot(111)
        axIM2.axis("off")
        cax = axIM2.imshow(ImDisp2, cmap='jet',vmin = Vmi2, vmax = Vma2)
        # common color maps: gray, hot, hsv, inferno, gist_ncar
        self.figureIM2.colorbar(cax, orientation='vertical')
        # self.figureIM.tight_layout()
        XX, YY = np.meshgrid(range(ImDisp2.shape[1]),range(ImDisp2.shape[0]))
        CentroXimFloOri = int(np.round((XX*ImDisp2).sum()/ImDisp2.sum()))
        CentroYimFloOri = int(np.round((YY*ImDisp2).sum()/ImDisp2.sum()))
        axIM2.plot(
                [CentroXimFloOri-20, CentroXimFloOri+20], 
                [CentroYimFloOri, CentroYimFloOri], 
                color='w', linestyle='-', linewidth=2)
        axIM2.plot(
                [CentroXimFloOri, CentroXimFloOri], 
                [CentroYimFloOri-20, CentroYimFloOri+20], 
                color='w', linestyle='-', linewidth=2)
        
        # refresh canvas
        self.canvasIM2.draw()
        # So it seems that globals can be read even without declaration in the 
        # function!!!

    def Get_info_from_filename(self, fileN):
        global testNum # number of the LIC test (for sanity check)
        global Hval # Total height (nm) of the profile to be extracted from 
        # the info in the filename (for pixelcloud)
        global Fval # Peak fluence (J/cm2) of the test to be extracted from 
        # the info in the filename (for pixelcloud)
        
        # Extract the test number of the measurement (if given in file)
        MorceauX = fileN.upper().split(" depot".upper())
        if len(MorceauX) > 1: 
            # 'depot' was found
            Morceau = MorceauX[1].split() # split by space
            try:
                testNumLoc = int(Morceau[0])
            except:
                print('Deposit number not found')
            else:
                if testNum == -1000:
                    testNum = testNumLoc
                    print('Test number is: {}'.format(testNum))
                elif testNum != testNumLoc:
                    print('You compare test {} and test {}'.format(
                            testNum,testNumLoc))
                    testNum = testNumLoc
                else:
                    print('Test number is: {}'.format(testNum))
        else:
            print('Deposit number not found')
            
        # Extract the Fluence of the measurement (if given in file)
        MorceauX = fileN.split(" F")
        if len(MorceauX) > 1: 
            # 'Fluence info' was found
            Morceau = MorceauX[1].split() # split by space (coupe le reste si pas collé)
            Morceau = Morceau[0].split('.ti') # coupe le '.tif', meme si collé)
            try:
                FvalLoc = float(Morceau[0])
            except:
                print('Fluence value not found')
            else:
                if Fval == -1000:
                    Fval = FvalLoc
                    print('The fluence is: {}'.format(Fval))
                elif Fval != FvalLoc:
                    print('You compare different fluences')
                    testNum = testNumLoc
                else:
                    print('The fluence is: {}'.format(Fval))
        else:
            print('Fluence value not found')
            
        # Extract the Height of the measurement (if given in file)
        MorceauX = fileN.split(" H")
        if len(MorceauX) > 1: 
            # 'Fluence info' was found
            Morceau = MorceauX[1].split() # split by space (coupe le reste si pas collé)
            Morceau = Morceau[0].split('.ti') # coupe le '.tif', meme si collé)
            try:
                HvalLoc = float(Morceau[0])
            except:
                print('Height value not found')
            else:
                if Hval == -1000:
                    Hval = HvalLoc
                    print('The height is: {}'.format(Hval))
                elif Hval != HvalLoc:
                    print('You compare different heights')
                    testNum = testNumLoc
                else:
                    print('The height is: {}'.format(Hval))
        else:
            print('Height value not found')
       
        
    def Load_File1(self):
        global im1
        global refName1 # file name for other tabs
        global GLval # Height step for one GL step (in nm) to be calculated from 
        # Hval and the GLrange in the image (for pixelcloud)
        
        global Vmi1 # define the display limits
        global Vma1
        
        global Im1ulx # for keeping the memory between two calls
        global Im1uly # upper left
        global Im1lrx # lower right
        global Im1lry
        global Im1ZoneDrawUpdate
        
        '''load the image file and show it in the left pane'''
        # choose the image with a dialog
        fname = QFileDialog.getOpenFileName(
                self, 
                'Open file',
                './input/',
                "All files (*.*) ;; image files (*.tif *.tiff *.png)")

        # load the image
        if fname[0]: # a file was chosen
            im1 = plt.imread(fname[0])
        print('File name: ', fname[0])
        
        # display the filename in the label
        self.LbFile1Name.setText(fname[0])
        # publish the filename for use in other functions and tabs
        #refName1 = fname[0]
        refName1 = fname[0].split('/')[-1]  # just the file name not the path
        
        self.Get_info_from_filename(refName1)
         
        if 'profilo'.upper() in refName1.upper():
            # update the GL-step value
            GLval = Hval /(im1.max() - im1.min())
        
        # prepare checking for saturation
        print('The file data type is ', im1.dtype, ' and the shape is ',im1.shape)
        bits = ''.join([c for c in str(im1.dtype) if c in '1234567890.'])
        maxZ = 2**int(bits) - 1 # np.iinfo(im1.dtype).max() ne marche pas
        
        # convert images with more than one level to 1d gray scale images
        if len(im1.shape)>2: # image has more than one layer
            # remove constant layers if there are
            constLayerList = []
            for layer in range(im1.shape[2]):
                if im1[:, :, layer].max()==im1[:, :, layer].min():
                    constLayerList.append(layer)
            im1 = np.delete(im1,constLayerList,2)
            # reduce to one layer if gray image has been saved as rgb with 
            # same entries
            uselessLayerList = []
            for layer in range(im1.shape[2]-1):
                if (im1[:, :, layer]==im1[:, :, layer+1]).all():
                    uselessLayerList.append(layer)
            im1 = np.delete(im1,uselessLayerList,2)
        
            # remove the useless dimension and change to float datatype
            im1 = np.mean(im1, axis=2, dtype=np.float64)
        else:
            im1 = im1.astype(np.float64)
        
        # remove white frame if present
        uf = 0 
        while im1[uf, im1.shape[1]//2] == maxZ:
            uf += 1
        lof = 0 
        while im1[im1.shape[0]-(lof+1), im1.shape[1]//2] == maxZ:
            lof += 1
        lf = 0 
        while im1[im1.shape[0]//2, lf] == maxZ:
            lf += 1
        rf = 0 
        while im1[im1.shape[0]//2, im1.shape[1]-(rf+1)] == maxZ:
            rf += 1
        im1 = im1[uf:im1.shape[0]-(lof+1),lf:im1.shape[1]-(rf+1)]
        
        message = 'Changed image to type ' + str(im1.dtype)+ ' and shape '+ str(im1.shape)
        print(message)
        # display message
        self.LbInfo11.setText(message)

        ## read rdbt
        #print('Idx of checked rdbt: ', self.rdbtgroup1.checkedId() )
        
        ## write rdbt
        #self.rdbtgroup1.button(0).setChecked(True) 

        ### check for saturation but do not normalize (height values etc)
        print('Maximum pixel value of the image: ', im1.max() )
        print('Maximum pixel value of the input dtype: ', maxZ )
        if im1.max() >= maxZ :
            message = 'THIS IMAGE IS SATURATED!'
            print(message)
            # display message
            self.LbInfo12.setText(message)
        else:
            message = 'The image is not saturated!'
            print(message)
            # display message
            self.LbInfo12.setText(message)
        print(' ')
             
        # define the display limits
        Vmi1 = im1.min()
        Vma1 = im1.max()
                
        ### Display the image
        # write rdbt
        self.rdbtgroup1.button(0).setChecked(True) 
        # Call the display function
        self.rdbt1Tog(0)
        
        # Give pixel size info
        PiSi1 = float(self.EdPiSi1.text())
        if PiSi1 > 0:
            message = 'For information: You have {:3.2f} pixels/µm'.format(
                    1/PiSi1)
        else:
            message = 'For information: PIXEL SIZE HAS TO BE POSITIVE !'
        self.LbPiInfo1.setText(message)
                
        # initialize the background zone info
        Im1ulx = -50 # for keeping the memory between two calls
        Im1uly = -50 # upper left
        Im1lrx = -50 # lower right
        Im1lry = -50
        Im1ZoneDrawUpdate = False
        
        
    def Load_File2(self):
        global im2
        global floName2
        global GLval # Height step for one GL step (in nm) to be calculated from 
        # Hval and the GLrange in the image (for pixelcloud)
        
        global Vmi2
        global Vma2
        
        global Im2ulx # for keeping the memory between two calls
        global Im2uly # upper left
        global Im2lrx # lower right
        global Im2lry
        global Im2ZoneDrawUpdate
        
        '''load the image file and show it in the left pane'''
        # choose the image with a dialog
        fname = QFileDialog.getOpenFileName(
                self, 
                'Open file',
                './input/',
                "All files (*.*) ;; image files (*.tif *.tiff *.png)")

        # load the image
        if fname[0]: # a file was chosen
            im2 = plt.imread(fname[0])
        print('File name: ', fname[0])
        
        # display the filename in the label
        self.LbFile2Name.setText(fname[0])
        # floName2 = fname[0]
        floName2 = fname[0].split('/')[-1]  # just the file name not the path
        
        self.Get_info_from_filename(floName2)
         
        if 'profilo'.upper() in floName2.upper():
            # update the GL-step value
            GLval = Hval /(im2.max() - im2.min())
        
        # prepare checking for saturation
        print('The file data type is ', im2.dtype, ' and the shape is ',im2.shape)
        bits = ''.join([c for c in str(im2.dtype) if c in '1234567890.'])
        maxZ = 2**int(bits) - 1 # np.iinfo(im2.dtype).max() ne marche pas
        
        # convert images with more than one level to 1d gray scale images
        if len(im2.shape)>2: # image has more than one layer
            # remove constant layers if there are
            constLayerList = []
            for layer in range(im2.shape[2]):
                if im2[:, :, layer].max()==im2[:, :, layer].min():
                    constLayerList.append(layer)
            im2 = np.delete(im2,constLayerList,2)
            # reduce to one layer if gray image has been saved as rgb with 
            # same entries
            uselessLayerList = []
            for layer in range(im2.shape[2]-1):
                if (im2[:, :, layer]==im2[:, :, layer+1]).all():
                    uselessLayerList.append(layer)
            im2 = np.delete(im2,uselessLayerList,2)
        
            # remove the useless dimension and change to float datatype
            im2 = np.mean(im2, axis=2, dtype=np.float64)
        else:
            im2 = im2.astype(np.float64)
        
        # remove white frame if present
        uf = 0 
        while im2[uf, im2.shape[1]//2] == maxZ:
            uf += 1
        lof = 0 
        while im2[im2.shape[0]-(lof+1), im2.shape[1]//2] == maxZ:
            lof += 1
        lf = 0 
        while im2[im2.shape[0]//2, lf] == maxZ:
            lf += 1
        rf = 0 
        while im2[im2.shape[0]//2, im2.shape[1]-(rf+1)] == maxZ:
            rf += 1
        im2 = im2[uf:im2.shape[0]-(lof+1),lf:im2.shape[1]-(rf+1)]
        
        message = 'Changed image to type ' + str(im2.dtype)+ ' and shape '+ str(im2.shape)
        print(message)
        # display message
        self.LbInfo21.setText(message)

        ## read rdbt
        #print('Idx of checked rdbt: ', self.rdbtgroup2.checkedId() )
        
        ## write rdbt
        #self.rdbtgroup2.button(0).setChecked(True) 

        ### check for saturation but do not normalize (height values etc)
        print('Maximum pixel value of the image: ', im2.max() )
        print('Maximum pixel value of the input dtype: ', maxZ )
        if im2.max() >= maxZ :
            message = 'THIS IMAGE IS SATURATED!'
            print(message)
            # display message
            self.LbInfo22.setText(message)
        else:
            message = 'The image is not saturated!'
            print(message)
            # display message
            self.LbInfo22.setText(message)
        print(' ')
                        
        # define the display limits
        Vmi2 = im2.min()
        Vma2 = im2.max()
                
        ### Display the image
        # write rdbt
        self.rdbtgroup2.button(0).setChecked(True) 
        # Call the dispaly function
        self.rdbt2Tog(0)
        
        # Give pixel size info
        PiSi2 = float(self.EdPiSi2.text())
        if PiSi2 > 0:
            message = 'For information: You have {:3.2f} pixels/µm'.format(
                    1/PiSi2)
        else:
            message = 'For information: PIXEL SIZE HAS TO BE POSITIVE !'
        self.LbPiInfo2.setText(message)

        # initialize the background zone info
        Im2ulx = -50 # for keeping the memory between two calls
        Im2uly = -50 # upper left
        Im2lrx = -50 # lower right
        Im2lry = -50
        Im2ZoneDrawUpdate = False
        
    def Update_File1(self):
        global im1fi
        ### denoise and normalize
        # first use median filter to remove noise pixels
        FilterMed1 = int(self.EdFilterMed1.text())
        if FilterMed1 > 0:
            main.statusBar().showMessage('Processing')
            im1fi = ndi.median_filter( im1, FilterMed1 )
            main.statusBar().showMessage('Ready')
        else:
            im1fi = im1.copy()
            
        # then use Gaussian filter to smoothe edges?
        FilterGau1 = float(self.EdFilterGau1.text())
        if FilterGau1 > 0:
            main.statusBar().showMessage('Processing')
            im1fi = ndi.gaussian_filter( im1fi, FilterGau1 )
            main.statusBar().showMessage('Ready')      
       
        ### Display the image
        # write rdbt
        self.rdbtgroup1.button(1).setChecked(True) 
        # Call the display function
        self.rdbt1Tog(1)
        
    def Update_File2(self):
        global im2fi
        ### denoise and normalize
        # first use median filter to remove noise pixels
        FilterMed2 = int(self.EdFilterMed2.text())
        if FilterMed2 > 0:
            main.statusBar().showMessage('Processing')
            im2fi = ndi.median_filter( im2, FilterMed2 )
            main.statusBar().showMessage('Ready')
        else:
            im2fi = im2.copy()
            
        # then use Gaussian filter to smoothe edges?
        FilterGau2 = float(self.EdFilterGau2.text())
        if FilterGau2 > 0:
            main.statusBar().showMessage('Processing')
            im2fi = ndi.gaussian_filter( im2fi, FilterGau2 )
            main.statusBar().showMessage('Ready')
        
        ### Display the image
        # write rdbt
        self.rdbtgroup2.button(1).setChecked(True) 
        # Call the display function
        self.rdbt2Tog(1)
        
        
    def approval_change(self):
        global imFloOri # original of the floating image, should only be read outside of this fct
        global imRefOri # original of the reference image, should only be read outside of this fct
        global flo # for rdbt2 and rdbt1
        global MaskList
        global ulx # for keeping the memory between two calls
        global uly # upper left
        global lrx # lower right
        global lry
        global refName1
        global floName2
        
        if self.ckFile1Finished.isChecked() and self.ckFile2Finished.isChecked():
            PiSi1 = float(self.EdPiSi1.text())
            PiSi2 = float(self.EdPiSi2.text())
            
            # choose floating and reference image
            # floating image = high resolution image
            if PiSi1 < PiSi2 : # im1 => floating
                imFloOri = im1fi.copy() # small pixel size = high resolution => float
                imRefOri = im2fi.copy()
                fact = PiSi2/PiSi1 # > 1
                flo = '1'
                buffer = refName1
                refName1 = floName2
                floName2 = buffer
                print('reference image = '+refName1)
                print('floating image = '+floName2)
            else:
                imFloOri = im2fi.copy() # small pixel size = high resolution => float
                imRefOri = im1fi.copy()
                fact = PiSi1/PiSi2 # > 1
                flo = '2'
            
            ### adapt pixel size of high resolution image = floating image
            # Dividing the pixelnumber (shape[0]) of the HR image (imFloat)
            # by fact gives the new number of pixels wanted for this image but
            # the result is a floating point number (not an integer). 
            # If nothing special is done the result will be rounded (few pixels)
            # It's better to crop the HR image first in order to come close to
            # integer result of the division. 
            BestFloPixSize = int(np.round(np.floor(imFloOri.shape[0]/fact)*fact)) # calc best pixel number
            print('Best pixel no (dim0) before downsclaing the float image ', BestFloPixSize) # info
            imFloOri = imFloOri[0:BestFloPixSize,:] # crop HR image
            BestFloPixSize = int(np.round(np.floor(imFloOri.shape[1]/fact)*fact)) # calc best pixel number
            print('Best pixel no (dim1)before downsclaing the float image ', BestFloPixSize) # info
            imFloOri = imFloOri[:,0:BestFloPixSize] # crop HR image
            print('changed imFloOri to type' , imFloOri.dtype, ' and shape ',imFloOri.shape) # info
            imFloOri = SkiTra.pyramid_reduce(imFloOri, downscale=fact, order=3) # downscale
            message = 'Changed image to type ' + str(imFloOri.dtype)+ ' and shape '+ str(imFloOri.shape)
            print(message)
            # display message on the good tab
            if flo == '1':
                self.LbInfo11.setText(message)
            else:
                self.LbInfo21.setText(message)
                
            ### display the downsampled image in the corresponding tab
            if flo == '1':
                self.rdbtgroup1.button(2).setChecked(True) 
                self.rdbt1Tog(2)
            else:
                self.rdbtgroup2.button(2).setChecked(True) 
                self.rdbt2Tog(2)
            message = 'imFloOri is of type ' + str(imFloOri.dtype)+ ' and shape '+ str(imFloOri.shape)
            print(message)
            message = 'imRefOri is of type ' + str(imRefOri.dtype)+ ' and shape '+ str(imRefOri.shape)
            print(message)
                                  
            # create the empty list of the masked pixels (tuples)
            MaskList = []
            # initialize the pixel cooridnates for the rectangles
            ulx = -50 # for keeping the memory between two calls
            uly = -50 # upper left
            lrx = -50 # lower right
            lry = -50
            
            # show the type of the Ref and Floating image
            message = ('                             ' 
                       + refName1[-25:-4] + '   ' + floName2[-25:-4])
            self.LbDiffFileInfo.setText(message)
           
            
    def rdbt3Tog(self,newChoice):
        # when calling this function two variables of same shape :
        # imRefCut and imFloCut have to exist
        
        # decide the vertical scale of ref end flo display
        vmini = np.min([imRefCut.min(),imFloCut.min()])
        vmaxi = np.max([imRefCut.max(),imFloCut.max()])
        
        # Clear the figure from earlier uses
        self.figureIMdi.clear()
        # Display the image
        axIMdi = self.figureIMdi.add_subplot(111)
        axIMdi.axis("off")
        if newChoice == 0:
            axIMdi.imshow(imRefCut, cmap='inferno', vmin=vmini, vmax=vmaxi )
            # good color maps: inferno, viridis, plasma, inferno, magma, cividis, 
            # more colorful: gist_rainbow, rainbow, nipy_spectral, gist_ncar
            self.figureIMdi.tight_layout()
            message = 'imRefCut is of type ' + str(
                        imRefCut.dtype)+ ' and shape '+ str(imRefCut.shape)
            print(message)
            message = ('Limits of ndarray: min: {:3.2f}, max:' +
                              '{:3.2f}').format(imRefCut.min(),imRefCut.max()) 
            print(message)
        else:
            # finally display the cases where the float image is needed
            if newChoice == 1:
                ### display the cut imFlo : imFloCut
                axIMdi.imshow(imFloCut, cmap='inferno', vmin=vmini, vmax=vmaxi )
                # common color maps: gray, hot, hsv, inferno, gist_ncar
                self.figureIMdi.tight_layout()
                message = 'imFloCut is of type ' + str(
                        imFloCut.dtype)+ ' and shape '+ str(imFloCut.shape)
                print(message)
                message = ('Limits of ndarray: min: {:3.2f}, max:' +
                              '{:3.2f}').format(imFloCut.min(),imFloCut.max()) 
                print(message)
            else:
                ### display the difference image 
                imDi = imFloCut-imRefCut
                axIMdi.imshow(imDi, cmap='inferno')
                # common color maps: gray, hot, hsv, inferno, gist_ncar
                self.figureIMdi.tight_layout()
        
        if self.ckMaskActivateIt.isChecked():
            btID = self.rdbtgroup3.checkedId() 
            self.showMask(btID)
            
        # refresh canvas
        self.canvasIMdi.draw() 
        return


    def Read_Tra_Params(self):
        ZOffs = float(self.EdZOffs.text())# grey levels after normalization
        ZFact = float(self.EdZFact.text()) 
        if self.ckLatXFlip.isChecked():
            Pfli = 1 # yes if > 0 (implemented like this for fit)
        else:
            Pfli = -1
        Pangle = [float(self.EdLatRot.text()),
                    float(self.EdLatRotMax.text())] # degrees
        PxOffset = [float(self.EdLatXShi.text()),
                      float(self.EdLatXShiMax.text())] # pixels to the right
        PyOffset = [-1 * float(self.EdLatYShi.text()),
                      -1 * float(self.EdLatYShiMax.text())] # pixels up
        # for brute make tuples here
        return ZOffs, ZFact, Pfli, Pangle, PxOffset, PyOffset

               
    def Write_Tra_Params(self,ps):
        # no ranges, only a 1D array
        # ZOffs, ZFact, Pfli, Pangle, PxOffset, PyOffset
        self.EdZOffs.setText('{:2.3e}'.format(ps[0])) # grey levels after normalization
        self.EdZFact.setText('{:2.3e}'.format(ps[1]))
        
        if ps[2] > 0: 
            self.ckLatXFlip.setChecked(True)
        else:
            self.ckLatXFlip.setChecked(False)
        self.EdLatRot.setText('{:2.3e}'.format(ps[3]))  # degrees
        # self.EdLatRotMax.setText('{:2.3e}'.format(Pangle)) # degrees
        self.EdLatXShi.setText('{:2.3e}'.format(ps[4])) # pixels to the right
        self.EdLatYShi.setText('{:2.3e}'.format(-1*ps[5])) # pixels up
        # for brute make tuples here
        return

    def makeImFlo(self):
        global imFlo
        # prepare imFlo having 2 times the size of imRefCut filled with zeros
        imFlo = np.zeros((2*imRefCut.shape[0],2*imRefCut.shape[1]))
        # or             tuple([2*x for x in imRefCut.shape])
        # this DOES NOT WORK:     2*imRefCut.shape        
          
        # shift imFlo to be centered about the maximum of imFloOri 
        # and keep 2 times the size of imRefCut (= imRefOri ici)
        # calc max
        (MaxYimFloOri, MaxXimFloOri) = np.unravel_index(
                                            imFloOri.argmax(), imFloOri.shape)
        # calculate limits of ranges where to put imFloOri (or a part of it)
        # the larger range limit is never used as index, the lower yes
        Xl = imFlo.shape[1]//2 - MaxXimFloOri
        XlU = 0
        if Xl < 0:
            XlU = -Xl
            Xl = 0
        Xr = imFlo.shape[1]//2 + (imFloOri.shape[1] - MaxXimFloOri)
        XrU = 0
        if Xr > imFlo.shape[1]:
            XrU = -(imFlo.shape[1] - Xr)
            Xr = imFlo.shape[1]
        Yu = imFlo.shape[0]//2 - MaxYimFloOri
        YuU = 0
        if Yu < 0:
            YuU = -Yu
            Yu = 0
        Yd = imFlo.shape[0]//2 + (imFloOri.shape[0] - MaxYimFloOri)
        YdU = 0
        if Yd > imFlo.shape[0]:
            YdU = -(imFlo.shape[0] - Yd)
            Yd = imFlo.shape[0]
        imFlo[Yu:Yd,Xl:Xr] = imFloOri[YuU:imFloOri.shape[0]-YdU, \
                                      XlU:imFloOri.shape[1]-XrU].copy()


    def onTabChange(self,TabNum):
        global imRefOri
        global imRefCut
        global imFloOri
        global imFlo
        global imFloCut
        
#        global MaskList
#        global ulx # for keeping the memory between two calls
#        global uly # upper left
#        global lrx # lower right
#        global lry
        
        #global TabNo
        TabNo = TabNum
        # print('TAB {} ACTIVATED'.format(TabNo))
        
        if TabNo == 2:
            ## prepare for fitting tab
            
            # normalize if the fit tab is activated
            imRefOri = imRefOri/imRefOri.max()
            imFloOri = imFloOri/imFloOri.max()
            
            self.crop_Ref() # contains: imRefCut = imRefOri.copy()
           
            self.makeImFlo() # contains imFlo = imFloOri.copy() 
            
            self.crop_Flo_to_Ref() # contains: imFloCut = imFlo.copy()
            
            # show imRefCut (which is a copy of imRefOri)
            self.rdbtgroup3.button(0).setChecked(True) 
            # show change in imRefOri
            self.rdbt3Tog(0)
            
#            # create the empty list of the masked pixels (tuples)
#            MaskList = []
#            # initialize the pixel cooridnates for the rectangles
#            ulx = -50 # for keeping the memory between two calls
#            uly = -50 # upper left
#            lrx = -50 # lower right
#            lry = -50            
            
        elif TabNo == 3:
            ## prepare for measurement tab
             
            ### Make reference image
            self.crop2_Ref() # contains: imRefCut = imRefOri.copy()
            
            ### Make floating image
            ## apply the found best lateral transform before continuing
            # read the parameters from the form
            # ZOffs, ZFact, Pfli, Pangle, PxOffset, PyOffset = self.Read_Tra_Params()
            ps = self.Read_Tra_Params()
            # remove the max values from parameter nested tuple 
            pFix = np.array(ps[0:3])  # copy the first 3 parameters 
            pFix[0] = 0 # Do not change offset here (do this in tabs im1 and im2)
            pFix[1] = 1 # Do not change scaling here (do this later)
            pVar = np.array(ps[3:]) # copy the ranges of params
            pVar = pVar[:,0] # only keep the minima
            paras = np.concatenate([pFix,pVar])
            # call calc_new_float with the list of now skalar parameters
            self.Calc_New_Float(*paras)  # contains: imFlo = imFloOri.copy()        
            self.crop2_Flo_to_Ref() # contains: imFloCut = imFlo.copy()
            
            # show im1Cut 
            self.rdbtgroupF.button(0).setChecked(True) 
            # this may be ref or float !!!
            self.rdbtFinalTog(0)
            
            ### show file info       
            # LbIMinfo1 'Files:            Image 1         Image2'
            # show filenames
            if flo == '1':
                message4 = ('Roles:                                  '+
                           '   floating          reference')
                message2 = ('Filenames:                 ' +
                       floName2 + '   ' + refName1)               
                message3 = ('Shapes after downsampling:    ' 
                       + str(imFloOri.shape) + '      ' + str(imRefOri.shape))
                
                if 'profilo'.upper() in floName2.upper():
                    self.EdNorm1to.setText(str(GLval*imFloCut.max()))
                elif 'laser'.upper() in floName2.upper():
                    self.EdNorm1to.setText(str(Fval))
                    
                if 'profilo'.upper() in refName1.upper():
                    self.EdNorm2to.setText(str(GLval*imRefCut.max()))
                elif 'laser'.upper() in refName1.upper():
                    self.EdNorm2to.setText(str(Fval))
            else :
                message4 = ('Roles:                                   '+
                           '   reference          floating')
                message2 = ('Filenames:                 ' +
                       refName1 + '   ' + floName2)
                message3 = ('Shapes after downsampling:    ' 
                       + str(imRefOri.shape) + '      ' + str(imFloOri.shape)) 
                                
                if 'profilo'.upper() in floName2.upper():
                    self.EdNorm2to.setText(str(GLval*imFloCut.max()))
                elif 'laser'.upper() in floName2.upper():
                    self.EdNorm2to.setText(str(Fval))
                    
                if 'profilo'.upper() in refName1.upper():
                    self.EdNorm1to.setText(str(GLval*imRefCut.max()))
                elif 'laser'.upper() in refName1.upper():
                    self.EdNorm1to.setText(str(Fval))
                    
            self.LbIMinfo4.setText(message4)
            self.LbIMinfo2.setText(message2)      
            self.LbIMinfo3.setText(message3)
            
            
        return


    def rdbtFinalTog(self,newChoice):
        # when calling this function two variables of same shape :
        # imRefCut and imFloCut have to exist
        
        # Clear the figure from earlier uses
        self.figureImFinal.clear()
        # Display the image
        axImFinal = self.figureImFinal.add_subplot(111)
        axImFinal.axis("off")
        if (newChoice == 0 and flo =='1') or (newChoice == 1 and flo =='2'):
            cax = axImFinal.imshow(imFloCut, cmap='inferno')
            # good color maps: inferno, viridis, plasma, inferno, magma, cividis, 
            # more colorful: gist_rainbow, rainbow, nipy_spectral, gist_ncar
            self.figureImFinal.colorbar(cax, orientation='horizontal')
            # self.figureIM.tight_layout()
        else:
            ### display the cut imFlo : imFloCut
            cax = axImFinal.imshow(imRefCut, cmap='inferno')
            # common color maps: gray, hot, hsv, inferno, gist_ncar
            self.figureImFinal.colorbar(cax, orientation='horizontal')
            # self.figureIM.tight_layout()
            
        # refresh canvas
        self.canvasImFinal.draw() 
        return


    def CropF_changed(self):
        ## show changed crop state, cancels action of update_transform and fit
        global imFloCut
        global imRefCut
        MyTableWidget.crop2_Ref(main.tw)
        MyTableWidget.crop2_Flo_to_Ref(main.tw)
        btID = self.rdbtgroupF.checkedId() 
        self.rdbtFinalTog(btID)
        return
       
        
    def Update_PixelCloud(self):
        global histVals
        XChoice = self.rdbtgroupX.checkedId()
        if (XChoice == 0 and flo =='1') or (XChoice == 1 and flo =='2'):
            x = imFloCut.flatten()
            xlb = floName2.split()[0]
            y = imRefCut.flatten()
            ylb = refName1.split()[0]
        else :
            y = imFloCut.flatten()
            ylb = floName2.split()[0]
            x = imRefCut.flatten()
            xlb = refName1.split()[0]
        
        if self.ckNorm1.isChecked():
            if XChoice == 0 :
                x = x / x.max() * float(self.EdNorm1to.text())
            else:
                y = y / y.max() * float(self.EdNorm1to.text())
        if self.ckNorm2.isChecked():
            if XChoice == 0 :
                y = y / y.max() * float(self.EdNorm2to.text())
            else:
                x = x / x.max() * float(self.EdNorm2to.text())
        
        # Clear the figure from earlier uses
        self.figurePiCloud.clear()
        # Display the image
        axPiCloud = self.figurePiCloud.add_subplot(111)
        # axPiCloud.axis("off")
        
        ### real pixel cloud: works
        axPiCloud.plot(x,y,'.',markersize = 0.5)
        axPiCloud.set_xlabel(xlb)
        axPiCloud.set_ylabel(ylb)
        
#        ### display hist2d: works more or less
#        histVals = plt.hist2d(x, y, bins=40) 
#        cax = axPiCloud.imshow(histVals[0], cmap='inferno', vmax = 6)
#        self.figurePiCloud.colorbar(cax, orientation='horizontal')
#        # opens additionnal figure window
#        # plot y-axis in image style (0 on top)
              
        # self.figureIM.tight_layout()
        self.canvasPiCloud.draw() 
        return
    
    
    def Make_fit(self):
        global imFlo # written inside Calc_New_Float
        global imFloCut
        global imRefCut
        ## start processing
        main.statusBar().showMessage('Processing')
        
        # read the parameters from the form
        # ZOffs, ZFact, Pfli, Pangle, PxOffset, PyOffset = self.Read_Tra_Params()
        p0 = self.Read_Tra_Params()
        
        print('Initial params:')
        print(' ZOffs = {:1.3e}, '.format(p0[0]))
        print(' ZFact = {:1.3e}, '.format(p0[1]))
        print(' Pfli = {:1.3e}, '.format(p0[2]))
        print(' PangleMin = {:1.3e}, '.format(p0[3][0]))
        print(' PangleMax = {:1.3e}, '.format(p0[3][1]))
        print(' PxOffsetMin = {:1.3e}, '.format(p0[4][0]))
        print(' PxOffsetMax = {:1.3e}, '.format(p0[4][1]))
        print(' PyOffsetMin = {:1.3e}, '.format(p0[5][0]))
        print(' PyOffsetMax = {:1.3e}, '.format(p0[5][1]))

        # split off the fixed parameters
        pFix = np.array(p0[0:3])  # do not vary the first 3 parameters
        print(' pFix shape : ', pFix.shape) #
        
        # remove the max values from parameter nested tuple
        pVar0 = np.array(p0[3:]) # copy the ranges of params
        print(' pVar0 shape : ', pVar0.shape) # 3,2
        pVar0 = pVar0[:,0] # only keep the minima
        print(' pVar0 shape : ', pVar0.shape) # 3,2
                
        def Merit(ps, pFix):
            global imFlo # written inside Calc_New_Float
            global imFloCut
            global imRefCut
            
            paras = np.concatenate([pFix,ps])
            # print(paras)  # for debugging
            self.Calc_New_Float(*paras) 
            self.crop_Ref()
            self.crop_Flo_to_Ref()
            Ssq, SsqRed = self.cal_chi2()
            return SsqRed
               
        result = opt.minimize(Merit, pVar0, args=(pFix) )
        print(result)
        paras = np.concatenate([pFix,result.x])
        self.Write_Tra_Params(paras)
        
        main.statusBar().showMessage('Ready')
        return
        
    
    def Calc_New_Float(self, ZOffs, ZFact, Pfli, Pangle, PxOffset, PyOffset):
        global imFlo # written 
        ## reset to original float image
        self.makeImFlo() # contains imFlo = imFloOri.copy()
                
        # Z-value modification
        imFlo = (imFlo + ZOffs)*ZFact
        
        # FLIPPING the X values (about the Y axis): Boolean (or pos/neg)         
        if Pfli > 0:
            FlipMa = np.array([ [-1, 0, imFlo.shape[1]],
                                [ 0, 1, 0],
                                [ 0, 0, 1]])
        else:
            FlipMa = np.array([ [1, 0, 1],
                                [0, 1, 0],
                                [0, 0, 1]])
        tf_flipX = SkiTra.EuclideanTransform(matrix=FlipMa)
        
        # Rotation mathematically positive, around center
        cent_y, cent_x = (np.array(imFlo.shape[:2]) -1) / 2 # -1 ??
        tf_rotate = SkiTra.EuclideanTransform(rotation=np.deg2rad(Pangle))
        tf_shiC_inv = SkiTra.EuclideanTransform(translation=[cent_x, cent_y])

        # Translation
        tf_shiC_Mod = SkiTra.EuclideanTransform(
                translation=[-(cent_x+PxOffset), -(cent_y+PyOffset)])
        
        imFlo = SkiTra.warp(imFlo,
                  (((tf_shiC_Mod + tf_rotate) + tf_shiC_inv) +tf_flipX),
                  order=1,
                  clip=False)
        # flip is done first, if called in outermost parantheses
        return 
    
            
    def Update_Transform(self):
        global imFlo # written inside Calc_New_Float
        global imFloCut
        global imRefCut
        ## start processing
        main.statusBar().showMessage('Processing')
        
        # read the parameters from the form
        # ZOffs, ZFact, Pfli, Pangle, PxOffset, PyOffset = self.Read_Tra_Params()
        ps = self.Read_Tra_Params()

        # remove the max values from parameter nested tuple 
        pFix = np.array(ps[0:3])  # copy the first 3 parameters 
        pVar = np.array(ps[3:]) # copy the ranges of params
        pVar = pVar[:,0] # only keep the minima
        paras = np.concatenate([pFix,pVar])

        # call calc_new_float with the list of now skalar parameters
        self.Calc_New_Float(*paras) 
        self.crop_Ref()
        self.crop_Flo_to_Ref()
        # MyTableWidget.crop_Flo_to_Ref(main.tw) # reads imFlo
        
        main.statusBar().showMessage('Ready')

        ## show change either in imFlo or in difference
        btID = self.rdbtgroup3.checkedId() 
        if btID == 0: # if Ref image was shown
            btID = 1 # set to imFlo    
            self.rdbtgroup3.button(btID).setChecked(True)
        self.rdbt3Tog(btID)
        
        ## calculate chi²
        Ssq, SsqRed = self.cal_chi2()
    
    
    def cal_chi2(self):
        diffImSqrd = (imFloCut-imRefCut)**2
        schiSq = np.sum( diffImSqrd )
        piNu = imRefCut.shape[1]*imRefCut.shape[0]
        
        if self.ckMaskActivateIt.isChecked():
            for count in range(len(MaskList)):
                schiSq = (schiSq - 
                           diffImSqrd[MaskList[count][1]][MaskList[count][0]])
            piNu = piNu - len(MaskList)
      
        message = '{:1.3e}'.format(schiSq/piNu)
        self.LbChi2.setText(message)
        print('Chi²/pixNum = ',message)
        return schiSq, schiSq/piNu
        
        
    def crop_Flo_to_Ref(self):
        global imFloCut
        
        # starts with imFlo (transfomed image) generates imFloCut
        imFloCut = imFlo.copy()
            
        # cut to imFloCut to imRefOri dimensions first
        # (around middle) -> imFloCut (then crop like imRef was cropped before)
        yDif = imFloCut.shape[0] - imRefOri.shape[0]  #rows
        xDif = imFloCut.shape[1] - imRefOri.shape[1]  #columns
        if (xDif > 0) and (yDif > 0):  # imFlo is larger than imRefOri
            #cut imFlo around its center
            if xDif % 2 == 0: 
                # xDif even
                imFloCut = imFloCut[:,xDif//2:(imFloCut.shape[1] - xDif//2)]
            else:
                # xDif odd
                imFloCut = imFloCut[:,xDif//2:(imFloCut.shape[1] -(xDif//2 +1))]
            if yDif % 2 == 0: 
                # yDif even
                imFloCut = imFloCut[yDif//2:(imFloCut.shape[0] - yDif//2),:]
            else:
                # yDif odd
                imFloCut = imFloCut[yDif//2:(imFloCut.shape[0] -(yDif//2 +1)),:] 
        # else: pad imFlo with zero frame (but first put backgroud to zero)                
        
        
        # then apply the crop 
        if self.ckCropIt.isChecked():
            CropUp = int(self.EdCropUp.text()) # pixels to the right
            CropDwn = int(self.EdCropDwn.text()) # pixels to the right
            CropL = int(self.EdCropL.text()) # pixels to the right
            CropR = int(self.EdCropR.text()) # pixels to the right
            imFloCut = imFloCut[
                    CropUp : imFloCut.shape[0]-CropDwn, 
                    CropL  : imFloCut.shape[1]-CropR]
        return
    
        
    def crop_Ref(self):
        global imRefCut
        
        # start with copy of approved image
        imRefCut = imRefOri.copy()
        
        if self.ckCropIt.isChecked():
            CropUp = int(self.EdCropUp.text()) # pixels to the right
            CropDwn = int(self.EdCropDwn.text()) # pixels to the right
            CropL = int(self.EdCropL.text()) # pixels to the right
            CropR = int(self.EdCropR.text()) # pixels to the right
            imRefCut = imRefCut[
                    CropUp : imRefCut.shape[0]-CropDwn, 
                    CropL  : imRefCut.shape[1]-CropR]           
        return
            
            
    def Crop_changed(self):       
        ## show changed crop state, cancels action of update_transform and fit
        global imFloCut
        global imRefCut
        MyTableWidget.crop_Ref(main.tw)
        MyTableWidget.makeImFlo(main.tw) # contains imFlo = imFloOri.copy()
        MyTableWidget.crop_Flo_to_Ref(main.tw)
        btID = self.rdbtgroup3.checkedId() 
        self.rdbt3Tog(btID)
        return

    def crop2_Flo_to_Ref(self):
        global imFloCut
        
        # starts with imFlo (transfomed image) generates imFloCut
        imFloCut = imFlo.copy()
            
        # cut to imFloCut to imRefOri dimensions first
        # (around middle) -> imFloCut (then crop like imRef was cropped before)
        yDif = imFloCut.shape[0] - imRefOri.shape[0]  #rows
        xDif = imFloCut.shape[1] - imRefOri.shape[1]  #columns
        if (xDif > 0) and (yDif > 0):  # imFlo is larger than imRefOri
            #cut imFlo around its center
            if xDif % 2 == 0: 
                # xDif even
                imFloCut = imFloCut[:,xDif//2:(imFloCut.shape[1] - xDif//2)]
            else:
                # xDif odd
                imFloCut = imFloCut[:,xDif//2:(imFloCut.shape[1] -(xDif//2 +1))]
            if yDif % 2 == 0: 
                # yDif even
                imFloCut = imFloCut[yDif//2:(imFloCut.shape[0] - yDif//2),:]
            else:
                # yDif odd
                imFloCut = imFloCut[yDif//2:(imFloCut.shape[0] -(yDif//2 +1)),:] 
        # else: pad imFlo with zero frame (but first put backgroud to zero)
        
        # then apply the crop 
        if self.ckCropItF.isChecked():
            CropFUp = int(self.EdCropFUp.text()) # pixels to the right
            CropFDwn = int(self.EdCropFDwn.text()) # pixels to the right
            CropFL = int(self.EdCropFL.text()) # pixels to the right
            CropFR = int(self.EdCropFR.text()) # pixels to the right
            imFloCut = imFloCut[
                    CropFUp : imFloCut.shape[0]-CropFDwn, 
                    CropFL  : imFloCut.shape[1]-CropFR]
        return
    
    def crop2_Ref(self):
        global imRefCut
        
        # start with copy of approved image
        imRefCut = imRefOri.copy()
        
        if self.ckCropItF.isChecked():
            CropFUp = int(self.EdCropFUp.text()) # pixels to the right
            CropFDwn = int(self.EdCropFDwn.text()) # pixels to the right
            CropFL = int(self.EdCropFL.text()) # pixels to the right
            CropFR = int(self.EdCropFR.text()) # pixels to the right
            imRefCut = imRefCut[
                    CropFUp : imRefCut.shape[0]-CropFDwn, 
                    CropFL  : imRefCut.shape[1]-CropFR]           
        return

    def GetMouseIm1(self, event): 
        # Shows the rectangle wich would define the Background zone 
        # if one woul press 'N' now
                     
        ## dans la doc de mpl ils utilisent ca pour eviter des indent sur 
        ## toute la fonction:
        #if self.press is None: return  # genre: si ca, ne fais rien
        #if event.inaxes != self.rect.axes: return
        if (self.ckZero1DefActivate.isChecked()  # background sustraction is activated
                  and event.xdata != None    # the mouse is in the canvas
                  and event.ydata != None    
                  and Im1ZoneDrawUpdate      # the zone drawing should be updated 
                  and (Im1ulx > -1) and (Im1uly > -1) ) :# the rectagle was started
                                     
            ## delete lines on axis (if there were any)
            axIM1.lines = []
            
            ## add the frame
            # use (ulx, uly) and (lrx, lry) 
            if event.xdata >= Im1ulx:
                ulx = Im1ulx
                lrx = int(np.round(event.xdata))
            else:
                ulx = int(np.round(event.xdata))
                lrx = Im1ulx
            if event.ydata >= Im1uly:
                uly = Im1uly
                lry = int(np.round(event.ydata))
            else:
                uly = int(np.round(event.ydata))
                lry = Im1uly           
            
            axIM1.plot([ulx,lrx,lrx,ulx,ulx], 
                        [uly,uly,lry,lry,uly], 
                        color='w', linestyle='-', linewidth=2)
            # ca m'a l'air plus joli, mais c'est seulement légèrement plus rapide
            self.canvasIM1.draw()
            
        
    def GetKeyIm1(self, event):
        # Manipulates the Mask (Pixels not to use for the fit evaluation)
        # h : upper left corner
        # n : lower right corner
        global Im1ulx # for keeping the memory between two calls
        global Im1uly # upper left
        global Im1lrx # lower right
        global Im1lry
        global Im1ZoneDrawUpdate
        # global Im1oldFrame # list of tuples
        
        print('Im1: ', event.key)
        #print('Im1: ', event.ydata)

        if (self.ckZero1DefActivate.isChecked() 
                  and event.xdata != None and event.ydata != None) :
            
            Letter = str(event.key).upper()
            if Letter == 'H':
                # memorize first point
                Im1ulx = int(np.round(event.xdata))
                Im1uly = int(np.round(event.ydata))
                # reset second point
                Im1lrx = -50
                Im1lry = -50
                # Tell other function to draw the rectangle
                Im1ZoneDrawUpdate = True
            elif Letter == 'N':
                # memorize second point
                Im1lrx = int(np.round(event.xdata))
                Im1lry = int(np.round(event.ydata))
                
                if (Im1ulx > -1) and (Im1uly > -1) : # the rectagle gets finished
                    # flip points if necessary
                    if Im1lrx < Im1ulx: # right x should be larger than left x
                        buffer = Im1ulx 
                        Im1ulx = Im1lrx
                        Im1lrx = buffer
                    if Im1lry < Im1uly: # lower y should be larger than upper y
                        buffer = Im1uly 
                        Im1uly = Im1lry
                        Im1lry = buffer
                    # Tell other function to no longer update the rectangle drawing
                    Im1ZoneDrawUpdate = False
            # end letter 'N'
        # end checkbox and mouse inside during key-press
        
    def DisplaySat1(self):
        global Vmi1
        global Vma1
        
        btId = self.rdbtgroup1.checkedId()
        if self.ckSatDisplay1.isChecked():
            Vmi1 = float(self.EdVmin1.text())
            Vma1 = float(self.EdVmax1.text())
        else:
            if btId == 0:
                ImDisp1 = im1 # view only
            elif btId == 1:
                ImDisp1 = im1fi # view only
            else:
                ### display the downsampled image
                if flo == '1':
                    ImDisp1 = imFloOri # view only
                else:
                    ImDisp1 = im1fi # view only  
            Vmi1 = ImDisp1.min()
            Vma1 = ImDisp1.max()
        self.rdbt1Tog(btId)
        return
    
    
    def Im1_backg_changed(self):
        # show the filtered and not downsampled image
        # defining the background zone in the downsampled image makes problems
        if self.ckZero1DefActivate.isChecked():
            self.rdbtgroup1.button(1).setChecked(True) 
            self.rdbt1Tog(1)
        
    def Upd_File1_zeroShift(self):
#        global Im1ulx # for keeping the memory between two calls
#        global Im1uly # upper left
#        global Im1lrx # lower right
#        global Im1lry
        global im1fi
        if not self.ckZero1DefActivate.isChecked():return  # background sustraction is not activated
        
        # Put the display to the filtered image without downsampling
        self.rdbtgroup1.button(1).setChecked(True) 
        # so work with im1fi
        
        inside = self.rdbtgroupZero1.checkedId()  # inside (1) or outside (0)
        
        # calculate offset (mean of enclosed pixels)
        if inside :
            summ = im1fi[Im1uly:Im1lry,Im1ulx:Im1lrx].sum()
            poiNum = np.prod(im1fi[Im1uly:Im1lry,Im1ulx:Im1lrx].shape)
        else: 
            summ = im1fi.sum() - im1fi[Im1uly:Im1lry,Im1ulx:Im1lrx].sum()
            poiNum = np.prod(im1fi.shape) - np.prod(im1fi[Im1uly:Im1lry,Im1ulx:Im1lrx].shape)
        offset = summ / poiNum
        
        im1fi = im1fi - offset
        self.rdbt1Tog(1) # update display

    def GetMouseIm2(self, event): 
        # Shows the rectangle wich would define the Background zone 
        # if one woul press 'N' now
                     
        ## dans la doc de mpl ils utilisent ca pour eviter des indent sur 
        ## toute la fonction:
        #if self.press is None: return  # genre: si ca, ne fais rien
        #if event.inaxes != self.rect.axes: return
        if (self.ckZero2DefActivate.isChecked()  # background sustraction is activated
                  and event.xdata != None    # the mouse is in the canvas
                  and event.ydata != None    
                  and Im2ZoneDrawUpdate      # the zone drawing should be updated 
                  and (Im2ulx > -1) and (Im2uly > -1) ) :# the rectagle was started
                                     
            ## delete lines on axis (if there were any)
            axIM2.lines = []
            
            ## add the frame
            # use (ulx, uly) and (lrx, lry)  
            if event.xdata >= Im2ulx:
                ulx = Im2ulx
                lrx = int(np.round(event.xdata))
            else:
                ulx = int(np.round(event.xdata))
                lrx = Im2ulx
            if event.ydata >= Im2uly:
                uly = Im2uly
                lry = int(np.round(event.ydata))
            else:
                uly = int(np.round(event.ydata))
                lry = Im2uly
            
            axIM2.plot([ulx,lrx,lrx,ulx,ulx], 
                        [uly,uly,lry,lry,uly], 
                        color='w', linestyle='-', linewidth=2)
            # ca m'a l'air plus joli, mais c'est seulement légèrement plus rapide
            self.canvasIM2.draw()
        
        
    def GetKeyIm2(self, event):
        # Manipulates the Mask (Pixels not to use for the fit evaluation)
        # h : upper left corner
        # n : lower right corner
        global Im2ulx # for keeping the memory between two calls
        global Im2uly # upper left
        global Im2lrx # lower right
        global Im2lry
        global Im2ZoneDrawUpdate
        # global Im2oldFrame # list of tuples
        
        print('Im2: ', event.key)
        #print('Im2: ', event.ydata)

        if (self.ckZero2DefActivate.isChecked() 
                  and event.xdata != None and event.ydata != None) :
            
            Letter = str(event.key).upper()
            if Letter == 'H':
                # memorize first point
                Im2ulx = int(np.round(event.xdata))
                Im2uly = int(np.round(event.ydata))
                # reset second point
                Im2lrx = -50
                Im2lry = -50
                # Tell other function to draw the rectangle
                Im2ZoneDrawUpdate = True
            elif Letter == 'N':
                # memorize second point
                Im2lrx = int(np.round(event.xdata))
                Im2lry = int(np.round(event.ydata))
                
                if (Im2ulx > -1) and (Im2uly > -1) : # the rectagle gets finished
                    # flip points if necessary
                    if Im2lrx < Im2ulx: # right x should be larger than left x
                        buffer = Im2ulx 
                        Im2ulx = Im2lrx
                        Im2lrx = buffer
                    if Im2lry < Im2uly: # lower y should be larger than upper y
                        buffer = Im2uly 
                        Im2uly = Im2lry
                        Im2lry = buffer
                    # Tell other function to no longer update the rectangle drawing
                    Im2ZoneDrawUpdate = False
            # end letter 'N'
        # end checkbox and mouse inside during key-press
      
        
    def DisplaySat2(self):
        global Vmi2
        global Vma2
        
        btId = self.rdbtgroup2.checkedId()
        if self.ckSatDisplay2.isChecked():
            Vmi2 = float(self.EdVmin2.text())
            Vma2 = float(self.EdVmax2.text())
        else:
            if btId == 0:
                ImDisp2 = im2 # view only
            elif btId == 1:
                ImDisp2 = im2fi # view only
            else:
                ### display the downsampled image
                if flo == '1':
                    ImDisp2 = imFloOri # view only
                else:
                    ImDisp2 = im2fi # view only  
            Vmi2 = ImDisp2.min()
            Vma2 = ImDisp2.max()
        self.rdbt2Tog(btId)
        return
        
    
    def Im2_backg_changed(self):
        # show the filtered and not downsampled image
        # defining the background zone in the downsampled image makes problems
        if self.ckZero2DefActivate.isChecked():
            self.rdbtgroup2.button(1).setChecked(True) 
            self.rdbt2Tog(1)
        
        
    def Upd_File2_zeroShift(self):
#        global Im2ulx # for keeping the memory between two calls
#        global Im2uly # upper left
#        global Im2lrx # lower right
#        global Im2lry
        global im2fi
        if not self.ckZero2DefActivate.isChecked():return  # background sustraction is not activated
        
        # Put the display to the filtered image without downsampling
        self.rdbtgroup2.button(1).setChecked(True) 
        # so work with im2fi
        
        inside = self.rdbtgroupZero2.checkedId()  # inside (1) or outside (0)
        
        # calculate offset (mean of enclosed pixels)
        if inside :
            summ = im2fi[Im2uly:Im2lry,Im2ulx:Im2lrx].sum()
            poiNum = np.prod(im2fi[Im2uly:Im2lry,Im2ulx:Im2lrx].shape)
        else: 
            summ = im2fi.sum() - im2fi[Im2uly:Im2lry,Im2ulx:Im2lrx].sum()
            poiNum = np.prod(im2fi.shape) - np.prod(im2fi[Im2uly:Im2lry,Im2ulx:Im2lrx].shape)
        offset = summ / poiNum
        
        im2fi = im2fi - offset
        self.rdbt2Tog(1) # update display
        
    def GetKey(self, event):
        # Manipulates the Mask (Pixels not to use for the fit evaluation)
        # h : upper left corner
        # n : lower right corner
        # b : single pixel
        global MaskList
        global ulx # for keeping the memory between two calls
        global uly # upper left
        global lrx # lower right
        global lry
                
        print(event.key)
        #print(event.ydata)

        if (self.ckMaskActivateIt.isChecked() 
                  and event.xdata != None and event.ydata != None) :
            ## read displayed image
            btID = self.rdbtgroup3.checkedId() 
            self.showMask(btID)
            
            Letter = str(event.key).upper()
            newPoints =[]
            if Letter == 'B':
                # attacher si le point n'existe pas encore dans la liste
                newPoints=[( int(np.round(event.xdata)) , 
                                 int(np.round(event.ydata)) )]
            elif Letter == 'H':
                # memorize first point
                ulx = int(np.round(event.xdata))
                uly = int(np.round(event.ydata))
                # reset second point
                lrx = -50
                lry = -50
            elif Letter == 'N':
                # memorize first point
                lrx = int(np.round(event.xdata))
                lry = int(np.round(event.ydata))
                
                if (ulx > -1) and (uly > -1) : # the rectagle gets finished
                    # Add rectangle points to newPoints
                    # should work with inverted points too
                    
                    # flip points if necessary
                    if lrx < ulx: # right x should be larger than left x
                        buffer = ulx 
                        ulx = lrx
                        lrx = buffer
                    if lry < uly: # lower y should be larger than upper y
                        buffer = uly 
                        uly = lry
                        lry = buffer
                    
                    # fill columnwise
                    for xCoo in range(ulx,lrx+1): # from left to right
                        # column loop
                        for yCoo in range(uly,lry+1): # from upper to lower
                            # line loop
                            newPoints.append((xCoo, yCoo))
                    # reset choices
                    lrx = -50
                    lry = -50
                    ulx = -50
                    uly = -50
            # end letter 'N'
            
            # add or remove newPoints to MaskList
            if self.rdbtgroupMsk.checkedId() == 0:
                # add really new points to MaskList
                MaskList = list(set( MaskList + newPoints )) # sorts at the same time
            elif self.rdbtgroupMsk.checkedId() == 1:
                # remove entries of newPoints that existed in MaskList
                MaskList = list(set(MaskList) - set(newPoints)) # sorts at the same time
                
            if Letter == 'B' or Letter == 'N' :
                btID = self.rdbtgroup3.checkedId() 
                self.showMask(btID)
            #print(len(MaskList))   
        # end checkbox and mouse inside during key-press
        
        
    def showMask(self,btID):
        global MaskList
        
        # Make a copy of the displayed image
        if btID == 0:
            MaskedImage = imRefCut.copy()
        elif btID == 1:
            MaskedImage = imFloCut.copy()
        else :
            MaskedImage = (imFloCut-imRefCut).copy()
                
        # calculate the values of the color switch limits and the 
        # replacement values (for the masked pixels to become visible)
        MiniVal = np.min(imRefCut)
        MaxiVal = np.max(imRefCut)
        
        infernoLimits = [0.35,0.82]
        infernoColVals = [0.66,1]
        
        # change the values (colors) of the pixels in the list
        for count in range(len(MaskList)):
            IsVal = imRefCut[MaskList[count][1],MaskList[count][0]]
            if  infernoLimits[0] <  IsVal/(MaxiVal-MiniVal) < infernoLimits[1] : # light color
                putVal = infernoColVals[1]*(MaxiVal-MiniVal)+MiniVal
            else:
                putVal = infernoColVals[0]*(MaxiVal-MiniVal)+MiniVal
            MaskedImage[MaskList[count][1],MaskList[count][0]] = putVal
        
        # display the modified image 
        # Clear the figure from earlier uses
        self.figureIMdi.clear()
        # Display the image
        axIMdi = self.figureIMdi.add_subplot(111)
        axIMdi.axis("off")
        cax = axIMdi.imshow(MaskedImage, cmap='inferno',vmin=MiniVal, vmax=MaxiVal)
        # common color maps: gray, hot, hsv, inferno, gist_ncar
        self.figureIMdi.colorbar(cax, orientation='horizontal')
        # refresh canvas
        self.canvasIMdi.draw() 


    def Mask_changed(self):
        global MaskList
        global ulx # for keeping the memory between two calls
        global uly # upper left
        global lrx # lower right
        global lry
        
        if self.ckMaskActivateIt.isChecked():
            btID = self.rdbtgroup3.checkedId() 
            self.showMask(btID)
        else:
            ulx = -50 # for keeping the memory between two calls
            uly = -50 # upper left
            lrx = -50 # lower right
            lry = -50
            btID = self.rdbtgroup3.checkedId() 
            self.rdbt3Tog(btID)
        
####################################################
if __name__ == '__main__':
    # app = QApplication(sys.argv) # std : create QApplication
    app = QApplication.instance() # checks if QApplication already exists
    if not app: # create QApplication if it doesnt exist
        app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)

    main = mainWindow()
    # print(dir(main)) # for debugging
    main.show()

    # sys.exit(app.exec_()) # std : exits python when the app finishes
    app.exec_() #do not exit Ipython when the app finishes

"""

fig, axs = plt.subplots(3, 1, figsize=(5, 15), sharex=True, sharey=True,
                        tight_layout=True)

# We can increase the number of bins on each axis
axs[0].hist2d(x, y, bins=40)



# read rdbt
print('Idx of checked rdbt: ', self.rdbtgroup.checkedId() )
        
# write rdbt
self.rdbtgroup.button(2).setChecked(True) 

For text legibility, gray-scale contrast is more important than color contrast. 
Use either white or black text to achieve maximum gray-scale contrast for 
whatever the background color happens to be. Using black or white text will 
also avoid confusion on whether the foreground or the background color is 
the color code the user should be attending to.
To decide dynamically whether to use black or white text, 
calculate the gray-scale brightness of the background RGB for a “typical” 
monitor using the following formula:
Y = 0.2126 * (R/255)^2.2  +  0.7151 * (G/255)^2.2  +  0.0721 * (B/255)^2.2
If Y is less than or equal to 0.18, use white text. 
If it’s greater than 0.18, use black text.

chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

centroid position:
    cx = sum(posx * poids) / sum(poids)

position of max in multiD arrau a:
    unravel_index(a.argmax(), a.shape)

"""
