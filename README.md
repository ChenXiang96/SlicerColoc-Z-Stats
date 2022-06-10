# Module-for-3D-Slicer
## Overview
This is a 3D slicer module for computing the percentage of colocalization(Spatial overlap between different channels) of Z-stack images.

Users can threshold the volume rendering of the input Z-stack image in the render window, select the region of interest(ROI) by the bounding box, and get a Venn diagram that shows the critical metric of colocalization's percentage.

## Installation
* The current 3D Slicer stable version is needed to use this module: [version 4.11.20210226](https://download.slicer.org/).
* This is a Python scripted module. Download the source code from [here](https://github.com/ChenXiang96/Module-for-3D-Slicer).
* Extract downloaded package (for example, to C:\Users\Public).
* Run 3D Slicer, search for the 'Extension Wizard' extension in the 'Modules' search box at the top and open it. Then click the 'Select Extension' button located under the 'Extension Tools' collapsible button.
* Select the path of this module to import it to Slicer(for example, C:\Users\Public\Module-for-3D-Slicer-main\MyTestModule).

## Panels and their use
* **Volume**: Select the current volume to render and opreate. 
* **Display ROI**: Show/hide the ROI bounding box of the current volume.
* **Re-center ROI**: Reposition the image region selected by the ROI bounding box to the center of the scene:

<img src="https://github.com/ChenXiang96/Module-for-3D-Slicer/blob/main/README-images/Re-center%20ROI.gif" width="600px">

* **Rename Volume**: Rename the current volume.

<img src="https://github.com/ChenXiang96/Module-for-3D-Slicer/blob/main/README-images/Rename%20Volume.gif" width="600px">


* **Delete Volume**: Delete the current volume.

<img src="https://github.com/ChenXiang96/Module-for-3D-Slicer/blob/main/README-images/Delete%20Volume.gif" width="600px">


* **Channels**: A list of sliders for adjusting the thresholds for all individual channels of the image.

<img src="https://github.com/ChenXiang96/Module-for-3D-Slicer/blob/main/README-images/Channels.gif" width="600px">


* **Annotation**: A text field for users to add annotations.

<img src="https://github.com/ChenXiang96/Module-for-3D-Slicer/blob/main/README-images/Annotations.gif" width="600px">


* **Compute Colocalization**: Compute the image's colocalization percentage within the current ROI, and draw a Venn diagram to show the percentage.

<img src="https://github.com/ChenXiang96/Module-for-3D-Slicer/blob/main/README-images/Compute%20Colocalization.gif" width="600px">


## Authors/Contributors:
* **Xiang Chen** - [Xiang Chen](https://github.com/ChenXiang96).

## Limitations
* Currently, this module only supports Z-stack images in Tagged image file format (.tif, .tiff).
* A maximum of 3 channels can be selected simultaneously for the computation of the colocalization percentage.




