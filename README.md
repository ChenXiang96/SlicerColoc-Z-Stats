# SlicerColoc-Z-Stats (ver. 1.0 dev): A Z-Stack signal colocalization extension tool for 3D Slicer
## Overview
SlicerColoc-Z-Stats is a 3D Slicer extension for computing 3D proteins' colocalization (spatial overlap between different channels) of Z-stack images.

Users can adjust the volume rendering of the Z-stack image via customizable thresholds, select the region of interest (ROI) by the bounding box and generate a Venn diagram and a spreadsheet， which displays/saves the colocalization metrics.

The license for this extension is [MIT](https://github.com/benoukraflab/SlicerColoc-Z-Stats/blob/main/LICENSE)

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Screenshots.png" width="800px">

## Installation
* The 3D Slicer stable version 5.0.3 is needed to use this module: [version Version 5.0.3](https://download.slicer.org/). Or it can be downloaded from this [link](https://slicer-packages.kitware.com/#collection/5f4474d0e1d8c75dfc70547e/folder/62cc513eaa08d161a31c1372)
  * Open “Extensions Manager” using menu: View / Extensions manager. On macOS, Extensions manager requires the [application to be installed](https://slicer.readthedocs.io/en/latest/user_guide/getting_started.html#mac).
  * Go to “Install extensions” tab
  * Go to “Quantification” category
  * Click “Install” button of “ColocZStats” to install it.
  * Wait until “Restart” button in the lower-right corner becomes enabled, then click “Restart”.
  * For more information on how to install extension via the “Extensions Manager”, see this [link](https://slicer.readthedocs.io/en/latest/user_guide/extensions_manager.html#install-extensions).

## Tutorial
* Start 3D Slicer
* Switch the scene view to '3D only'
* Load a TIFF image: Click the 'Data' button or the 'Add Data' button under the 'File' tab, and click the 'Choose File(s) to Add' button to load the image.
* Switch to "ColocZStats" module. The TIFF file will appear as grayscale image until it is selected as 'Volume' in the ColozZstats module.
* Click on the eye icon in front of 'Display ROI' to show the ROI bounding box of the current image in the 3D View.
* Adjust the ROI bounding box to any position.
* Click the 'Re-center ROI' button to reposition the image region within the ROI bounding box to the scene's center.
* Adjust the slider under each channel to any position. The threshold of each channel can be changed synchronously with the sliding of the slider, which can be observed in the 3D view.
* Click the 'Compute Colocalization' button and wait seconds to get a Venn diagram and a spreadsheet, which displays the image's colocalization metrics within the current ROI. The Venn diagram and the spreadsheet are saved in the default scene location of slicer version 5.0.3. (The default scene location can be found under the 'Edit/Application Settings' option within 3D Slicer. It can also be read/written from Python as *slicer.app.defaultScenePath*. It can also be changed, but note that the default scene location should be a folder with read and write permissions).
* Click the 'SAVE' button to save the scene and the information of the UI to a 'mrml' file for reloading.
* [Download links to sample image](https://drive.google.com/file/d/1IYlggsikgtQR7jXE83sSS2ZtMCuswsA0/view?usp=sharing)

## Coefficients
* **Pearson's colocalization coefficient**:
Pearson's linear correlation coefficient can be used to measure the overlap of the pixels. It is defined as follows:
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Pearson's%20Coefficient.png" width="600px">

* **Intersection coefficient**:
A voxel in the ROI box can be considered to have some interesting signal once its value is between a certain threshold intensity range. In such a case its value could be accounted for as 1, independent of its actual intensity, and otherwise it could be accounted for as 0, and similarly for the other selected channels.
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Intersection%20weight.png" width="600px">
For the case of any two selected channels:
The intersection contribution of a given voxel can be defined as the product of the two channels.
The intersection coefficient is:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Intersection%20for%20two%20channels.png" width="600px">

The numerator: the total number of intersecting voxels between the two channels. 

The denominator: the total number of voxels of both channels together, which is calculated as the total voxels’ number of the first selected channel plus the total voxels’ number of the second selected channel minus voxels’ number of the intersection (to avoid accounting for it twice).

The intersection coefficient can also be split into two separate coefficients (To report what portion of the first and second channels are intersecting):

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i1%20%20for%20two%20selected%20channels.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i2%20%20for%20%20two%20selected%20channels.png" width="600px">

For the case of any three selected channels:
The intersection contribution of a given voxel can be defined as the product of the three channels.
The intersection coefficient is:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Intersection%20for%20three%20channels.png" width="900px">

The numerator: the total number of intersecting voxels among three channels. 

The denominator: the total voxels’ number of the three selected channels together.
When any three channels are selected, the intersection coefficient can also be split into three separate coefficients (To report what portion of the three channels are intersecting):

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i1%20%20for%20%20three%20selected%20channels.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i2%20%20for%20%20three%20selected%20channels.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i3%20%20for%20%20three%20selected%20channels.png" width="600px">


## Panels and their use
* **Volume**: Select the current volume to render and operate. 
* **Display ROI**: Show/hide the ROI bounding box of the current volume. Note that after the image is loaded, the ROI box created by clicking the "Display ROI" button for the first time does not actually totaly fit with the entire image, but the ROI box can still be customized and dragged to any location. If you want to select the entire image for calculation, please make sure to drag the ROI box to any position that can completely contain the entire image.

* **Re-center ROI**: Reposition the image region selected by the ROI bounding box to the center of the scene:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Re-center%20ROI.gif" width="600px">

* **Rename Volume**: Rename the current volume. Note that in order to save the scene without duplicate volume nodes and to avoid errors (includes calculation errors) after loading the scene, please give each volume an individual name.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Rename%20Volume.gif" width="600px">


* **Delete Volume**: Delete the current volume.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Delete%20Volume.gif" width="600px">


* **Channels**: A list of sliders for adjusting the thresholds for all individual channels of the image.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Channels.gif" width="600px">

* **Rename Channel**: A button to the right of each channel label to rename each channel. Each channel name displayed on the GUI corresponds to the channel name on the Venn diagram and the spreadsheet generated by clicking the 'Compute Colocalization' button. Note that in order to save the scene without duplicate volume nodes and to avoid errors (includes calculation errors) after loading the scene, please give each channel an individual name.


<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Rename%20Channel%20button.gif" width="600px">

* **Annotation**: A text field for users to add annotations.
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Annotations.gif" width="600px">


* **Compute Colocalization**: Compute the image's colocalization metrics within the current ROI box, draw a Venn diagram to show the voxel percentage, Intensity Scatterplots corresponding to the selected channels, and generate a spreadsheet that contains the names of all selected channels, all corresponding threshold ranges, the colocalization metrics, and the information of the ROI box (Center, Orientation, Size).

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Compute%20Colocalization.gif" width="600px">

**Venn diagram example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Venn%20diagram%20example.png" width="600px">

**Intensity scatterplot example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Scatter%20Plot%20example.png" width="600px">

**Spreadsheet example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Spreadsheet%20example.gif" width="600px">

## Authors/Contributors:
* **Xiang Chen** - [Xiang Chen](https://github.com/ChenXiang96).
* **Oscar Meruvia-Pastor** - [Oscar Meruvia-Pastor](https://github.com/omerpas/).
* **Touati Benoukraf** - [Touati Benoukraf](https://github.com/benoukraflab).

## Limitations
* Currently, this module only supports Z-stack images in Tagged image file format (.tif, .tiff).
* A maximum of 3 channels can be selected simultaneously for the computation of the colocalization percentage.




