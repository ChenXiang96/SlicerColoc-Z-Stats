# SlicerColoc-Z-Stats (ver. 1.0 dev): A Z-Stack signal colocalization extension tool for 3D Slicer
## Overview
SlicerColoc-Z-Stats is a 3D Slicer extension for computing proteins' colocalization (spatial overlap between different channels) of Z-stack images.

Users can adjust the volume rendering of the Z-stack image via customizable thresholds, select the region of interest (ROI) by the bounding box and generate a Venn diagram, 2D histograms and a spreadsheet, which displays/saves the colocalization metrics.

The license for this extension is [MIT](https://github.com/benoukraflab/SlicerColoc-Z-Stats/blob/main/LICENSE)

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Screenshots.png" width="800px">

## Installation
* Since the 2D histograms produced by our extension are created by the Bokeh package, in order to be able to export PNG images, Bokeh needs to use a browser to render the PNG. In order for this to work, a driver is required to be installed before installing our extension in the 3D Slicer. Take installing the *ChromeDriver* as an example: Download and unzip the *ChromeDriver* corresponding to your Chrome version from this [link](https://chromedriver.chromium.org/downloads), and make sure it's in your PATH. For more information on how to install the driver, check out this [link](https://docs.bokeh.org/en/2.4.2/docs/user_guide/export.html#). 
* The 3D Slicer stable version is needed to use this extension: [Stable Release](https://download.slicer.org/). For more information on how to install 3D Slicer, check out this [link](https://slicer.readthedocs.io/en/latest/user_guide/getting_started.html).
  * On Windows, open “Extensions Manager” using menu: View / Extensions manager.
  * Go to “Install extensions” tab
  * Go to “Quantification” category
  * Click “Install” button of “ColocZStats” to install it.
  * Wait until “Restart” button in the lower-right corner becomes enabled, then click “Restart”.
  * For more information on how to install extension via the “Extensions Manager”, check out this [link](https://slicer.readthedocs.io/en/latest/user_guide/extensions_manager.html#install-extensions). Note that the URL for the *Slicer Extensions Catalog* listed in the link above is outdated, the latest URL is: [https://extensions.slicer.org/catalog/All/32438/win](https://extensions.slicer.org/catalog/All/32438/win).

## Tutorial
* Start 3D Slicer
* Go to "ColocZStats" extension.
* Load a Z-stack TIFF image: Click the 'Data' button or the 'Add Data' button under the 'File' tab, and click the 'Choose File(s) to Add' button to load the image. When a Z-stack image is loaded into ColocZStats, each of its channels is automatically split into separate volume nodes, and each volume node is assigned a distinct color for rendering. This allows you to view and manipulate each channel independently. 
* Click on the eye icon in front of 'Display ROI' to create and show the ROI box of the current image in the 3D View. Please note that after the image is loaded, the initial ROI box created by clicking the button may not fit perfectly with the entire image. However, you can still customize and drag the ROI box to any position you need. If you want to select the entire image for calculation, make sure to drag the ROI box to a position that completely contains the entire image.
* Adjust the ROI box to any position.
* Click the 'Re-center ROI' button to reposition the image region within the ROI box to the scene's center.
* Adjust the slider under each channel to any position. The threshold of each channel can be changed synchronously with the sliding of the slider, which can be observed in the 3D view.
* To obtain 2D histograms, a Venn diagram, and a spreadsheet displaying/saving the image's colocalization metrics within the current ROI, click the 'Compute Colocalization' button and wait a few seconds. Please note that when there are too many voxels in the ROI box, it may take 2-3 minutes for Bokeh to render the 2D histogram. The 2D histograms, Venn diagram and the spreadsheet are saved in the default scene location of 3D slicer. (The default scene location can be found under the 'Edit/Application Settings' option within 3D Slicer. It can also be read/written from Python as *slicer.app.defaultScenePath*. It can also be changed, but note that the default scene location should be a folder with read and write permissions).
* Click the 'SAVE' button to save the scene, the annotations, and the status of the UI to a 'mrml' file for reloading.
* [Download links to sample image](https://drive.google.com/file/d/1IYlggsikgtQR7jXE83sSS2ZtMCuswsA0/view?usp=sharing)

## Coefficients
* **Pearson's colocalization coefficient**:
Pearson's linear correlation coefficient can be used to measure the overlap of the voxels. It is defined as follows:
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Pearson%20Coefficient.png" width="600px">
The pearson's coefficient ranges from -1 to 1. Ch1 and Ch2 represent the selected channels, respectively. 
Similar to the way the Colocalization Analyzer in Huygens software computes Pearson's coefficient [1]. In principle, Pearson's coefficient is unaffected by thresholds. However, thresholds are taken into account to handle specified threshold settings consistently across all coefficients computed by the ColocZStats. The difference between the Colocalization Analyzer of Huygens and ColocZStats is that when ColocZStats calculates Pearson's coefficient, each specified channel's lower threshold and upper threshold will be included in the calculation. For example,  if you specify lower and upper threshold values for a specified channel, voxel intensities greater than the upper threshold value will be set to zero and based on that, the lower threshold value will be subtracted from all the remaining voxel intensities. In case negative voxel values occur, these will be set to zero. This means that setting user-specified threshold values can change the resulting Pearson's coefficient. Therefore, Pearson's coefficient generated by ColocZStats is always based on the thresholded image data within the ROI box.


* **Intersection coefficient**:
Similar to the way the Colocalization Analyzer in Huygens software computes the Intersection coefficient [1]. A voxel in the ROI box can be considered to have some interesting signal once its value is between a certain threshold intensity range. In such a case its value could be accounted for as 1, independent of its actual intensity, and otherwise it could be accounted for as 0, and similarly for the other selected channels. The difference between the Colocalization Analyzer of Huygens and ColocZStats is that when ColocZStats calculates the Intersection coefficient, each specified channel's lower threshold and upper threshold will be included in the calculation.
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Intersection-weight.png" width="600px">
For the case of any two selected channels:
The intersection contribution of a given voxel can be defined as the product of the two channels.
The intersection coefficient is:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Intersection%20for%20two.png" width="600px">

The numerator: the total number of intersecting voxels between the two channels. 

The denominator: the total number of voxels of both channels together, which is calculated as the total voxels’ number of the first selected channel plus the total voxels’ number of the second selected channel minus voxels’ number of the intersection (to avoid accounting for it twice).

The intersection coefficient can also be split into two separate coefficients (To report what portion of the first and second channels are intersecting):

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i1%20for%20two.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i2%20for%20two.png" width="600px">

Based on the above method of obtaining the intersection coefficient between two channels, the functionality of obtaining the intersection coefficient of three channels has been added to ColocZStats.
For the case of any three selected channels:
The intersection contribution of a given voxel can be defined as the product of the three channels.
The intersection coefficient is:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/intersection%20for%20three.png" width="900px">

The numerator: the total number of intersecting voxels among three channels. 

The denominator: the total voxels’ number of the three selected channels together.
When any three channels are selected, the intersection coefficient can also be split into three separate coefficients (To report what portion of the three channels are intersecting):

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i1%20for%20three.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i2%20for%20three.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i3%20for%20three.png" width="600px">


## Panels and their use
* **Volume**: Select the current volume which contains multiple channels to render and operate. 
* **Display ROI**: Show/hide the ROI bounding box of the current volume. 

* **Re-center ROI**: Reposition the image region selected by the ROI bounding box to the center of the scene:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Recenter.gif" width="600px">

* **Rename Volume**: Rename the current volume. Note that in order to save the scene without duplicate volume nodes and to avoid errors (includes calculation errors) after loading the scene, please give each volume an individual name.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Rename-Volume.gif" width="600px">


* **Delete Volume**: Delete the current volume.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Delete-Volume.gif" width="600px">


* **Channels**: A list of sliders for adjusting the thresholds for all individual channels of the image.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Channels%20panel.gif" width="600px">

* **Rename Channel**: A button to the right of each channel label to rename each channel. Each channel name displayed on the GUI corresponds to the channel name on the Venn diagram and the spreadsheet generated by clicking the 'Compute Colocalization' button. Note that in order to save the scene without duplicate volume nodes and to avoid errors (includes calculation errors) after loading the scene, please give each channel an individual name.


<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Rename%20Channel.gif" width="600px">

* **Annotation**: A text field for users to add annotations for each volume node. The annotations can be saved while saving the scene and be reloaded while reloading the scene.
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Add%20Annotations.gif" width="600px">


* **Compute Colocalization**: Compute the image's colocalization metrics within the current ROI box, draw a Venn diagram to show the voxel percentage, draw 2D histograms corresponding to the selected channels, and generate a spreadsheet that contains the names of all selected channels, all corresponding threshold ranges, the colocalization metrics, and the information of the ROI box (Center, Orientation, Size).

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Colocalization-Computation.gif" width="600px">

**Venn diagram example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Venn-Example.png" width="600px">

**2D histogram example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Scatterplot-example.png" width="600px">

**Spreadsheet example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Spreadsheet-Example.gif" width="600px">

## Authors/Contributors:
* **Xiang Chen** - [Xiang Chen](https://github.com/ChenXiang96).
* **Oscar Meruvia-Pastor** - [Oscar Meruvia-Pastor](https://github.com/omerpas/).
* **Touati Benoukraf** - [Touati Benoukraf](https://github.com/benoukraflab).

## Limitations
* Currently, this extension only supports multi-channel Z-stack images in Tagged image file format (.tif, .tiff).
* Load multi-channel Z-stack images of up to 15 channels.
* A maximum of 3 channels can be selected simultaneously for the computation.



## References
[1] ColocalizationTheory [Internet]. [cited 2022 Dec 21],. Available from: https://svi.nl/ColocalizationTheory


