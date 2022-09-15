# SlicerColoc-Z-Stats (ver. 1.0 dev): A Z-Stack signal colocalization extension tool for 3D Slicer
## Overview
SlicerColoc-Z-Stats is a 3D Slicer extension for computing 3D proteins' colocalization (spatial overlap between different channels) of Z-stack images.

Users can set the volume rendering of the Z-stack input image via customizable thresholds within 3D viewports, select the region of interest (ROI) by the bounding box and generate a Venn diagram that displays colocalization metrics.

The license for this extension is [MIT](https://github.com/benoukraflab/SlicerColoc-Z-Stats/blob/main/LICENSE)

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Screenshots.png" width="800px">

## Installation
* The 3D Slicer stable version 5.0.3 is needed to use this module: [version Version 5.0.3](https://download.slicer.org/). Or it can be downloaded from this [link](https://slicer-packages.kitware.com/#collection/5f4474d0e1d8c75dfc70547e/folder/62cc513eaa08d161a31c1372)
* Method 1:
  * Open “Extensions Manager” using menu: View / Extensions manager. On macOS, Extensions manager requires the [application to be installed](https://slicer.readthedocs.io/en/latest/user_guide/getting_started.html#mac).
  * Go to “Install extensions” tab
  * Go to “Quantification” category
  * Click “Install” button of “ColocZStats” to install it.
  * Wait until “Restart” button in the lower-right corner becomes enabled, then click “Restart”.
  * For more information on how to install extension via the “Extensions Manager”, see this [link](https://slicer.readthedocs.io/en/latest/user_guide/extensions_manager.html#install-extensions).
* Method 2:
  * This is a Python scripted module. Download the source code from [here](https://github.com/ChenXiang96/SlicerColoc-Z-Stats).
  * Extract downloaded package (for example, to C:\Users\Public).
  * Run 3D Slicer, search for the 'Extension Wizard' extension in the 'Modules' search box at the top and open it. Then click the 'Select Extension' button located under the 'Extension Tools' collapsible button.
  * Select the path of this module to import it to Slicer(for example, C:\Users\Public\SlicerColoc-Z-Stats-main).

## Tutorial
* Start 3D Slicer
* Switch the scene view to '3D only'
* Load a TIFF image: Click the 'Data' button or the 'Add Data' button under the 'File' tab, and click the 'Choose File(s) to Add' button to load the image.
* Switch to "ColocZStats" module. The TIFF file will appear as grayscale image until it is selected as 'Volume' in the ColozZstats module.
* Click on the eye icon in front of 'Display ROI' to show the ROI bounding box of the current image in the 3D View.
* Adjust the ROI bounding box to any position.
* Click the 'Re-center ROI' button to reposition the image region within the ROI bounding box to the scene's center.
* Adjust the slider under each channel to any position. The threshold of each channel can be changed synchronously with the sliding of the slider, which can be observed in the 3D view.
* Click the 'Compute Colocalization' button and wait about a minute to get a Venn diagram which displays the image's colocalization percentage within the current ROI. The Venn diagram will be saved under the installation folder of version 5.0.3.(for example, C:\Users\Public\AppData\Local\NA-MIC\Slicer 5.0.3).
* Click the 'SAVE' button to save the scene and the information of the UI/Annotation to a 'mrml' file for reloading.
* [Download links to sample image](https://drive.google.com/file/d/1IYlggsikgtQR7jXE83sSS2ZtMCuswsA0/view?usp=sharing)

## Panels and their use
* **Volume**: Select the current volume to render and operate. 
* **Display ROI**: Show/hide the ROI bounding box of the current volume.
* **Re-center ROI**: Reposition the image region selected by the ROI bounding box to the center of the scene:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Re-center%20ROI.gif" width="600px">

* **Rename Volume**: Rename the current volume.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Rename%20Volume.gif" width="600px">


* **Delete Volume**: Delete the current volume.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Delete%20Volume.gif" width="600px">


* **Channels**: A list of sliders for adjusting the thresholds for all individual channels of the image.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Channels.gif" width="600px">


* **Annotation**: A text field for users to add annotations.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Annotations.gif" width="600px">


* **Compute Colocalization**: Compute the image's colocalization percentage within the current ROI, and draw a Venn diagram to show the percentage.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Compute%20Colocalization.gif" width="600px">


## Authors/Contributors:
* **Xiang Chen** - [Xiang Chen](https://github.com/ChenXiang96).
* **Oscar Meruvia-Pastor** - [Oscar Meruvia-Pastor](https://github.com/omerpas/).
* **Touati Benoukraf** - [Touati Benoukraf](https://github.com/benoukraflab).

## Limitations
* Currently, this module only supports Z-stack images in Tagged image file format (.tif, .tiff).
* A maximum of 3 channels can be selected simultaneously for the computation of the colocalization percentage.




