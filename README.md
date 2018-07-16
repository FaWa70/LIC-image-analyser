# LIC-image-analyser
Superpose and analyse images from different measurments of the same object

V31:
* Added the button for export of the pixelCloud to an excel file and implemented a simple version 
(no info on mask, crop, transform parameters, etc.)
* Removed the useless maximum values for the transformation parameters.
(needed to adapt update_transform, makefit and onTabChange) 
* It's no longer necessary to go back to tab 2 or 1 (for unchecking and rechecking approval) before going from 3 to 4. (But if one goes back the inversion error is still there)
* Double crop error in tab3 has been solved by modifying makeimFlo (starts now with 2*imRefOri not imRefCut any longer)
--------------------
problems in V30:
* After fit going back to im2 uncheck+recheck finished ckbox inverts the ref and float image
(do it 2 times to get the right plots in tab4)
* Double crop error in tab3 (floating image)

--------------------
V30 can normalize the data an dputw axes labels in the pixel cloud on tab4
But there is still the double crop error in tab3
