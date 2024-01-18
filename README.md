# SlicerColoc-Z-Stats (ver. 1.0 dev): A Z-Stack signal colocalization extension tool for 3D Slicer
## Overview
SlicerColoc-Z-Stats is a 3D Slicer extension designed for measuring proteins' colocalization based on multi-channel confocal z-stack images.

Users can: Customize the threshold range for each channel of the loaded confocal z-stack by using adjustable sliders (changes can be reflected via the volume rendering in real-time); Select a region of interest (ROI) through an ROI box; Obtain a Venn diagram displaying the volume percentages of the thresholded channels within the ROI; Obtain the results of several related colocalization coefficients; Get a 2D histogram showing voxel intensity relationships of each channel pair, and get a spreadsheet that stores all the analysis results.

The license for this extension is [MIT](https://github.com/benoukraflab/SlicerColoc-Z-Stats/blob/main/LICENSE)

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Screenshots.png" width="800px">

## Installation
* Since the 2D histograms produced by our extension are created by the Bokeh package, to be able to export PNG images, Bokeh needs to use a browser to render the PNGs. For this to work, a driver is required to be installed before installing our extension in the 3D Slicer. Take installing the *ChromeDriver* as an example: Download and unzip the *ChromeDriver* corresponding to your Chrome version from this [link](https://chromedriver.chromium.org/downloads), and make sure it's in your PATH. For more information on how to install the driver, check out this [link](https://docs.bokeh.org/en/2.4.2/docs/user_guide/export.html#). 
* The 3D Slicer stable version is needed to use this extension: [Stable Release](https://download.slicer.org/). For more information on how to install 3D Slicer, check out this [link](https://slicer.readthedocs.io/en/latest/user_guide/getting_started.html).
  * On Windows, open “Extensions Manager” via the menu: View / Extensions Manager.
  * Go to the “Install extensions” tab
  * Go to the “Quantification” category
  * Click the “Install” button of “ColocZStats” to install it.
  * Wait until the “Restart” button in the lower-right corner becomes clickable, then click “Restart”.
  * For more information on how to install an extension via the “Extensions Manager”, check out this [link](https://slicer.readthedocs.io/en/latest/user_guide/extensions_manager.html#install-extensions). Note that the URL for the *Slicer Extensions Catalog* listed in the link above is outdated, the latest URL is: [https://extensions.slicer.org/catalog/All/32438/win](https://extensions.slicer.org/catalog/All/32438/win).

## Tutorial
* Start 3D Slicer
* Go to the "ColocZStats" extension.
* Load a multi-channel z-stack TIFF image: Click the 'Data' button and click the 'Choose File(s) to Add' button to load the image. When it is loaded into ColocZStats, each channel will be automatically split as a separate volume node, and each will be assigned a distinct color for rendering.
* Select the channels for analysis and adjust the sliders under any channel to any necessary position to assign custom threshold ranges.
* Click on the eye icon of 'Display ROI' to create an ROI box for the current stack in the 3D View. Please note that the initial ROI box may not fit perfectly with the entire stack. However, you can still drag the ROI box to any position you need. If you want to select the entire stack for calculation, drag the ROI box to a position containing the entire stack.
* Click the 'Re-center ROI' button to reposition the image region within the ROI box to the scene's center.
* Click the 'Compute Colocalization' button and wait a few seconds to obtain a Venn diagram, a 2D histogram for each channel pair, and a spreadsheet that saves all the results of the related colocalization metrics. All the analysis will only based on the thresholded channels within the ROI. When there are too many voxels in the ROI box, it may take longer for Bokeh to render 2D histograms. The 2D histograms, Venn diagram, and the result spreadsheet will be saved in the 3D Slicer's default scene location by default. (The default scene location can be found under the 'Edit/Application Settings' option within 3D Slicer. It can also be read/written from Python as *slicer.app.defaultScenePath*. It can also be changed, but note that the default scene location should be a folder with read and write permissions).
* Click the 'SAVE' button to save the scene, the annotation, and the status of the GUI to an 'mrml' file for reloading.
* To ensure compatibility, the input file should be a TIFF-formatted 3D multi-channel confocal z-stack that retains its original intensities, and each channel should be in grayscale. Additionally, all channels should have identical image order, dimensions, and magnification.
* [Download links to sample image](https://drive.google.com/file/d/1IYlggsikgtQR7jXE83sSS2ZtMCuswsA0/view?usp=sharing)

## Coefficients
* **Pearson's colocalization coefficient**:
Pearson's linear correlation coefficient can be used to measure the overlap of the voxels. It is defined as follows:
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Pearson%20Coefficient.png" width="600px">

Pearson's coefficient ranges from -1 to 1. Ch1 and Ch2 represent a specified channel pair.
Similar to the way the Colocalization Analyzer in Huygens software computes Pearson's coefficient [1]. In principle, Pearson's coefficient is unaffected by thresholds. However, thresholds are taken into account to handle specified threshold settings consistently across all coefficients computed by the ColocZStats. The difference between the Colocalization Analyzer of Huygens and ColocZStats is that when ColocZStats calculates Pearson's coefficient, for each specified channel, not only its lower threshold but also its upper threshold will be included in the calculation. For example, if you specify lower and upper threshold values for a specified channel, voxel intensities greater than the upper threshold value will be set to zero and based on that, the lower threshold value will be subtracted from all the remaining voxel intensities. In case negative voxel values occur, these will be set to zero. This means that setting user-specified threshold values can change the resulting Pearson's coefficient. Therefore, Pearson's coefficient generated by ColocZStats is always based on the thresholded image data within the ROI box.


* **Global Intersection coefficient**:

Similar to the way the Colocalization Analyzer in Huygens software computes the global intersection coefficient [1]. For any specified channel, a voxel in the ROI box can be considered to have some interesting signal once its value is within a certain threshold intensity range. In such a case, its value will be accounted for as 1, independent of its actual intensity; otherwise, it will be accounted for as 0. The difference between the Colocalization Analyzer of Huygens and ColocZStats is that when ColocZStats calculates the global intersection coefficient, each specified channel's upper threshold will be included in the calculation.
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Intersection-weight.png" width="600px">
In the case of any two channels being selected, the global intersection coefficient is:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Intersection%20for%20two.png" width="600px">

The intersection contribution of a given voxel can be defined as the product of the two channels.

The numerator: The total volume of intersecting voxels. 

The denominator: the total volume of both channels together, which is calculated as the total volume of the first selected channel plus the total volume of the second selected channel minus the total volume of intersecting voxels (to avoid accounting for it twice).
The global intersection coefficient can also be split into two separate coefficients (To report what portion of the first and second channels are intersecting):

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i1%20for%20two.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i2%20for%20two.png" width="600px">

Based on the above method of obtaining the intersection coefficients between two channels, the functionality of obtaining the intersection coefficients of three channels has been added to ColocZStats.
In the case of any three channels are selected:
The global intersection coefficient is:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/intersection%20for%20three.png" width="900px">

The intersection contribution of a given voxel can be defined as the product of the three channels.

The numerator: the total volume of intersecting voxels. 

The denominator: the total volume of the three selected channels together.

When any three channels are selected, the global intersection coefficient can also be split into three separate coefficients (To report what portion of the three channels are intersecting):

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i1%20for%20three.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i2%20for%20three.png" width="600px">

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/i3%20for%20three.png" width="600px">


## Panels and their use
* **Volume**: The volume currently being rendered and manipulated.
  
* **Display ROI**: Show/hide the ROI box for the current volume. 

* **Re-center ROI**: Reposition the image region selected by the ROI box to the center of the scene:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Recenter.gif" width="600px">

* **Rename Volume**: Rename the current volume. Note that to save the scene without duplicate volume nodes and to avoid errors after loading the scene, please give each volume an individual name.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Rename-Volume.gif" width="600px">


* **Delete Volume**: Delete the current volume.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Delete-Volume.gif" width="600px">


* **Channels**: For adjusting the thresholds and the visibility for all individual channels of the stack.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Channels%20panel.gif" width="600px">

* **Rename Channel**: A button for renaming each channel. Each channel name displayed on the GUI corresponds to the channel name displayed in the Venn diagram and the results spreadsheet. Note that to save the scene without duplicate volume nodes and to avoid errors after loading the scene, please give each channel an individual name.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Rename%20Channel.gif" width="600px">

* **Annotation**: A text field for users to add an annotation for each loaded stack. All the annotations can be saved while saving the scene and be reloaded while reloading the scene.
<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Add%20Annotations.gif" width="600px">


* **Compute Colocalization**: Compute the above colocalization metrics for the thresholded channels within the current ROI box, draw a Venn diagram showing the volume percentages, draw 2D histograms for each channel pair, and generate a result spreadsheet that contains the names of all selected channels, all corresponding threshold ranges, all the colocalization metrics, and the information of the ROI box (Center, Orientation, Size), etc.

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Colocalization-Computation.gif" width="600px">

**Venn diagram example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Venn-Example.png" width="600px">

**2D histogram example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Scatterplot-example.png" width="600px">

**Result Spreadsheet example**:

<img src="https://github.com/ChenXiang96/SlicerColoc-Z-Stats/blob/main/Images/Spreadsheet-Example.gif" width="600px">

## Authors/Contributors:
* **Xiang Chen** - [Xiang Chen](https://github.com/ChenXiang96).
* **Oscar Meruvia-Pastor** - [Oscar Meruvia-Pastor](https://github.com/omerpas/).
* **Touati Benoukraf** - [Touati Benoukraf](https://github.com/benoukraflab).

## Limitations
* For compatibility, each multi-channel Z-stack is allowed to contain up to 15 channels.
* A maximum of 3 channels can be selected simultaneously for the computation.



## References
[1] ColocalizationTheory [Internet]. [cited 2022 Dec 21],. Available from: https://svi.nl/ColocalizationTheory


