import os
import unittest
import logging
import vtk, qt, ctk, slicer
import SegmentStatistics
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

try:
    import matplotlib
except ModuleNotFoundError:
    slicer.util.pip_install("matplotlib")
    import matplotlib

try:
    import decimal
except ModuleNotFoundError:
    slicer.util.pip_install("decimal")
    import decimal
from decimal import Decimal

try:
    import pandas as pd
except ModuleNotFoundError:
    slicer.util.pip_install("pandas")
    import pandas as pd

try:
    import xlsxwriter
except ModuleNotFoundError:
    slicer.util.pip_install("xlsxwriter")
    import xlsxwriter

import sys

if not hasattr(sys, 'argv'):
    sys.argv = ['']

try:
    import tifffile
except ModuleNotFoundError:
    slicer.util.pip_install("tifffile")
    import tifffile

try:
    import matplotlib_venn
except ModuleNotFoundError:
    slicer.util.pip_install("matplotlib_venn")
    import matplotlib_venn

from matplotlib_venn import venn2_unweighted
from matplotlib_venn import venn3_unweighted

matplotlib.use("Agg")
from pylab import *
import matplotlib.pyplot as plt

#
# ColocZStats
#

class ColocZStats(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "ColocZStats"
        self.parent.categories = [
            "Quantification"]
        self.parent.dependencies = []
        self.parent.contributors = [
            "Xiang Chen (Memorial University of Newfoundland), Oscar Meruvia-Pastor (Memorial University of Newfoundland), Touati Benoukraf (Memorial University of Newfoundland)"]

        self.parent.helpText = """
  For user guides, go to <a href="https://github.com/ChenXiang96/SlicerColoc-Z-Stats">the GitHub page</a>
"""
        self.parent.acknowledgementText = """
  This extension was originally developed by Xiang Chen, Memorial University of Newfoundland(MUN). Thanks to Dr.Oscar Meruvia-Pastor(MUN) and Dr.Touati Benoukraf(MUN) for their careful guidance during the development process.
"""

    def testFunc():
        print("test func")


#
# ColocZStatsWidget
#

class ColocZStatsWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False
        self._updatingParameterNodeFromGUI = False
        self._importingScene = False
        self.volumeDict = {}
        self.uiGroupDict = {}
        self.annotationDict = {}
        self.ROINodeDict = {}
        self.ROICheckedDict = {}
        self.InputCheckedDict = {}
        self.currentIndex = -1
        self.imageWidget = None
        self.channelsWidget = qt.QWidget()
        self.channelsLayout = qt.QVBoxLayout()
        self.channelsWidget.setLayout(self.channelsLayout)

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/ColocZStats.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = ColocZStatsLogic()

        # Connections
        # Connect observers to scene events
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartImportEvent, self.onSceneStartImport)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndImportEvent, self.onSceneEndImport)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
        self.ui.InputVolumeComboBox.defaultText = "Select a Volume"
        self.ui.InputVolumeComboBox.connect('currentIndexChanged(int)', self.onInputVolumeChange)
        self.ui.InputCheckBox.connect('clicked(bool)', self.onInputCheckBoxClicked)
        self.ui.ROICheckBox.connect('clicked(bool)', self.onROICheckBoxClicked)
        self.ui.RecenterButton.connect('clicked(bool)', self.onRecenterButtonClicked)
        self.ui.RenameButton.connect('clicked(bool)', self.onRenameButtonClicked)
        self.ui.DeleteButton.connect('clicked(bool)', self.onDeleteButtonClicked)
        self.ui.ComputeButton.connect('clicked(bool)', self.onComputeButtonClicked)
        self.ui.AnnotationText.connect('updateMRMLFromWidgetFinished()', self.onAnnotationTextSaved)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

        # Populate input volume list with existing scalar volume nodes
        volumeNodes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
        for node in volumeNodes:
            self.logic.createVolumesForChannels(node, self)

        self.updateParameterNodeFromGUI()

    def onInputVolumeChange(self, index):
        """
        Called when input volume's combobox changes.
        """
        # Update current index
        oldIndex = self.currentIndex
        self.currentIndex = index
        comboBox = self.ui.InputVolumeComboBox

        # Disabled old input volume widgets
        if oldIndex != -1:
            oldFilename = comboBox.itemData(oldIndex)
            if oldFilename:
                oldGroupBox = self.uiGroupDict[oldFilename]
                oldGroupBox.hide()
                if oldFilename in self.ROINodeDict:
                    self.ROINodeDict[oldFilename].GetDisplayNode().SetVisibility(False)

        # Enable new input volume widgets
        filename = comboBox.itemData(index)
        if filename:
            groupBox = self.uiGroupDict[filename]
            groupBox.show()

            if filename in self.ROINodeDict:
                self.ROINodeDict[filename].GetDisplayNode().SetVisibility(self.ROICheckedDict[filename])

        if filename in self.annotationDict:
            annotationTextNode = self.annotationDict[filename]
            if annotationTextNode:
                self.ui.AnnotationText.setMRMLTextNode(annotationTextNode)

        if filename in self.InputCheckedDict:
            self.ui.InputCheckBox.checked = self.InputCheckedDict[filename]

        if filename in self.ROINodeDict:
            self.ui.ROICheckBox.setChecked(self.ROICheckedDict[filename])
        else:
            self.ui.ROICheckBox.setChecked(False)

        self.updateParameterNodeFromGUI()

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def onNodeAdded(self, caller, event, calldata):
        node = calldata
        if isinstance(node, slicer.vtkMRMLVolumeNode):
            qt.QTimer.singleShot(100, lambda: self.logic.createVolumesForChannels(node, self))

    def onInputCheckBoxClicked(self, checked):
        """
        Called when the checkbox before the input volume is clicked.
        To control the visibility of the volume in the scene.
        """
        if self._updatingGUIFromParameterNode:
            return
        comboBox = self.ui.InputVolumeComboBox
        filename = comboBox.itemData(comboBox.currentIndex)
        channelVolumeList = self.volumeDict.get(filename)
        if not channelVolumeList:
            return

        volRenLogic = slicer.modules.volumerendering.logic()
        self.InputCheckedDict[filename] = checked

        group = self.uiGroupDict[filename]
        checkBoxes = group.findChildren(qt.QCheckBox)
        for index in range(len(channelVolumeList)):
            channelVolumeNode = channelVolumeList[index]
            if channelVolumeNode:
                displayNode = volRenLogic.GetFirstVolumeRenderingDisplayNode(channelVolumeNode)
                displayNode.SetVisibility(checked and checkBoxes[index].checked)

        self.updateParameterNodeFromGUI()

    def onROICheckBoxClicked(self, checked):
        """
        Called when the checkbox before the ROI is clicked.
        To control the visibility of the ROI bounding box.
        """
        if self._updatingGUIFromParameterNode:
            return
        comboBox = self.ui.InputVolumeComboBox
        filename = comboBox.itemData(comboBox.currentIndex)
        channelVolumeList = self.volumeDict.get(filename)
        if not channelVolumeList:
            return

        createROINode = not (filename in self.ROINodeDict)
        if createROINode:
            ROINode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")
            ROINode.SetName(comboBox.currentText + " ROI")
            roiDisplayNode = ROINode.GetDisplayNode()
            roiDisplayNode.SetColor(1.0, 1.0, 1.0)
            roiDisplayNode.SetSelectedColor(1.0, 1.0, 1.0)
            roiDisplayNode.SetOpacity(0.0)
            self.ROINodeDict[filename] = ROINode
            self.ROICheckedDict[filename] = checked

        volRenLogic = slicer.modules.volumerendering.logic()
        roiNodeID = self.ROINodeDict[filename].GetID()

        # Fit ROI bounding box to volume and enable the cropping effect.
        for channelVolumeNode in channelVolumeList:
            if channelVolumeNode:
                displayNode = volRenLogic.GetFirstVolumeRenderingDisplayNode(channelVolumeNode)
                displayNode.SetAndObserveROINodeID(roiNodeID)
                if createROINode:
                    # volRenLogic.FitROIToVolume(displayNode)
                    cropVolumeParameters = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLCropVolumeParametersNode")
                    cropVolumeParameters.SetInputVolumeNodeID(channelVolumeNode.GetID())
                    cropVolumeParameters.SetROINodeID(roiNodeID)
                    slicer.modules.cropvolume.logic().SnapROIToVoxelGrid(cropVolumeParameters)
                    slicer.modules.cropvolume.logic().FitROIToInputVolume(cropVolumeParameters)
                    slicer.mrmlScene.RemoveNode(cropVolumeParameters)
                displayNode.SetCroppingEnabled(checked)
        self.ROINodeDict[filename].GetDisplayNode().SetVisibility(checked)
        self.ROICheckedDict[filename] = checked

        self.updateParameterNodeFromGUI()

    def onRecenterButtonClicked(self):
        """
        Called when the 'Re-center ROI' button is clicked.
        To reposition the image region selected by the ROI bounding box to the center of the scene.
        """
        comboBox = self.ui.InputVolumeComboBox
        filename = comboBox.itemData(comboBox.currentIndex)
        roiNode = None
        if filename in self.ROINodeDict:
            roiNode = self.ROINodeDict[filename]
        layoutManager = slicer.app.layoutManager()
        threeDWidget = layoutManager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        if roiNode:
            xyz = [0, 0, 0]
            roiNode.GetXYZ(xyz)
            threeDView.cameraNode().SetFocalPoint(xyz)
        else:
            threeDView.resetFocalPoint()

    def onRenameButtonClicked(self):
        """
        Called when the 'Rename Volume' button is clicked.
        To rename the current volume.
        """
        comboBox = self.ui.InputVolumeComboBox
        filename = comboBox.itemData(comboBox.currentIndex)
        channelVolumeList = self.volumeDict.get(filename)
        if not channelVolumeList:
            return
        text = qt.QInputDialog.getText(self.layout.parentWidget(), "Rename Volume", "New name:", qt.QLineEdit.Normal, comboBox.currentText)
        if text:
            newName = str(text)
            comboBox.setItemText(comboBox.currentIndex, newName)
            groupBox = self.uiGroupDict[filename]
            checkBoxes = groupBox.findChildren(qt.QCheckBox)
            for index in range(len(channelVolumeList)):
                if channelVolumeList[index]:
                    name = newName + "_" + checkBoxes[index].text
                    channelVolumeList[index].SetName(name)
            self.updateParameterNodeFromGUI()
            roiNode = None
            if filename in self.ROINodeDict:
                roiNode = self.ROINodeDict[filename]
            if roiNode:
                roiNode.SetName(newName + " ROI")
            else:
                return



    def onDeleteButtonClicked(self):
        """
        Called when the 'Delete Volume' button is clicked.
        To delete the current volume from the scene.
        """
        comboBox = self.ui.InputVolumeComboBox
        filename = comboBox.itemData(comboBox.currentIndex)
        channelVolumeList = self.volumeDict.get(filename)
        if not channelVolumeList:
            return

        for channelVolumeNode in channelVolumeList:
            if channelVolumeNode:
                slicer.mrmlScene.RemoveNode(channelVolumeNode)

        # Delete all sliders from the UI that control the threshold of all channels.
        self.volumeDict.pop(filename, None)
        groupBox = self.uiGroupDict[filename]
        groupBox.hide()
        self.uiGroupDict.pop(filename, None)
        groupBox.setParent(None)
        comboBox.removeItem(comboBox.currentIndex)

        # Delete all ROI bounding box as well.
        if filename in self.ROINodeDict:
            ROINode = None
            ROINode = self.ROINodeDict.pop(filename)
            if ROINode:
                slicer.mrmlScene.RemoveNode(ROINode)
        if filename in self.ROICheckedDict:
            self.ROICheckedDict.pop(filename)
        self.ui.ROICheckBox.setChecked(False)

    def onComputeButtonClicked(self):
        """
        Called when the 'Compute Colocalization' button is clicked.
        To compute the volume's colocalization percentage within the current ROI.
        """
        self.logic.computeStats(self)

    def onAnnotationTextSaved(self):
        """
        To save the annotation text.
        """
        if not self._updatingGUIFromParameterNode:
            self.updateParameterNodeFromGUI()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        self.updateParameterNodeFromGUI()
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        self.updateParameterNodeFromGUI()
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def onSceneStartImport(self, caller, event):
        self._importingScene = True

    def onSceneEndImport(self, caller, event):
        self._importingScene = False
        nodes = slicer.util.getNodesByClass("vtkMRMLScriptedModuleNode")
        for node in nodes:
            if node.GetName() == "ColocZStats":
                self.setParameterNode(node)
                break

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode or self._updatingParameterNodeFromGUI or self._importingScene:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        countStr = self._parameterNode.GetParameter("Count")
        if countStr == None or countStr == "":
            self._updatingGUIFromParameterNode = False
            return

        # Image Count
        imageCount = int(countStr)
        # Current Selected Index
        currentText = self._parameterNode.GetParameter("CurrentText")

        comboBox = self.ui.InputVolumeComboBox
        # Load data for each image
        for index in range(imageCount):
            indexStr = str(index)

            # Item Text
            itemText = self._parameterNode.GetParameter("ItemText" + indexStr)

            # Filepath
            filepath = self._parameterNode.GetParameter("Filepath" + indexStr)

            # Input Check Box
            InputVisibility = (self._parameterNode.GetParameter("InputVisibility" + indexStr) == "true")
            self.InputCheckedDict[filepath] = InputVisibility

            # ROI Check Box
            ROINode = self._parameterNode.GetNodeReference("ROINode" + indexStr)
            if ROINode:
                self.ROINodeDict[filepath] = ROINode
            ROICheckStatus = (self._parameterNode.GetParameter("ROI" + indexStr) == "true")
            self.ROICheckedDict[filepath] = ROICheckStatus

            # Annotation
            annotationText = self._parameterNode.GetParameter("Annotation" + indexStr)
            if not annotationText:
                annotationText = ""

            # Channel count
            channelCount = int(self._parameterNode.GetParameter("Channel Count" + indexStr))

            # Create layout
            layout = qt.QVBoxLayout()

            # Reference for all channels' volume.
            channelVolumes = list()
            for channelIndex in range(channelCount):
                volumeParameterName = "Volume" + str(index) + "_" + str(channelIndex)
                channelVolume = self._parameterNode.GetNodeReference(volumeParameterName)
                channelVolumes.append(channelVolume)

            if filepath not in self.uiGroupDict:
                for channelIndex in range(len(channelVolumes)):

                    # Update the state of channels' Visibility, LowerThreshold, UpperThreshold.
                    visibilityParameterName = "Visibility" + str(index) + "_" + str(channelIndex)
                    visibility = (self._parameterNode.GetParameter(visibilityParameterName) == "true")
                    channelLabelName = "ChannelLabel" + str(index) + "_" + str(channelIndex)
                    channelLabel = str(self._parameterNode.GetParameter(channelLabelName))
                    lowerThresholdParameterName = "LowerThreshold" + str(index) + "_" + str(channelIndex)
                    lowerThreshold = int(float(self._parameterNode.GetParameter(lowerThresholdParameterName)))
                    upperThresholdParameterName = "UpperThreshold" + str(index) + "_" + str(channelIndex)
                    upperThreshold = int(float(self._parameterNode.GetParameter(upperThresholdParameterName)))

                    # Create widgets for channel volume node
                    subHorizontallayout = qt.QHBoxLayout()
                    name = channelLabel
                    checkBox = qt.QCheckBox(name)
                    checkBox.objectName = name + "_checkbox"
                    checkBox.setChecked(visibility)
                    self.connectCheckBoxChangeSlot(checkBox, channelVolumes[channelIndex])
                    subHorizontallayout.addWidget(checkBox)
                    renameChannelbutton = qt.QPushButton("Rename Channel")
                    renameChannelbutton.objectName = name + "_renameButton"
                    self.connectRenameChannelButtonChangeSlot(renameChannelbutton, channelVolumes[channelIndex], subHorizontallayout, checkBox)
                    subHorizontallayout.addWidget(renameChannelbutton)
                    thresholdSlider = slicer.qMRMLVolumeThresholdWidget()
                    thresholdSlider.objectName = name + "_threshold"
                    thresholdSlider.setMRMLVolumeNode(channelVolumes[channelIndex])
                    thresholdSlider.lowerThreshold = max(lowerThreshold, 1)
                    thresholdSlider.upperThreshold = upperThreshold
                    self.connectThresholdChangeSlot(thresholdSlider, channelVolumes[channelIndex])
                    layout.addItem(subHorizontallayout)
                    layout.addWidget(thresholdSlider)



                # Add a groupBox for thresholding widgets.
                self.volumeDict[filepath] = channelVolumes
                groupBox = qt.QGroupBox("")
                self.uiGroupDict[filepath] = groupBox
                layout.addStretch()
                groupBox.setLayout(layout)
                self.channelsLayout.addWidget(groupBox)
                self.ui.scrollArea.setWidget(self.channelsWidget)
                comboBox.addItem(itemText, filepath)

                # Create text node for the annotation.
                annotationTextNode = self._parameterNode.GetNodeReference("AnnotationNode" + indexStr)
                annotationTextNode.SetText(annotationText)
                self.annotationDict[filepath] = annotationTextNode
            else:
                groupBox = self.uiGroupDict[filepath]
                checkBoxes = groupBox.findChildren(qt.QCheckBox)
                thresholdSliders = groupBox.findChildren(slicer.qMRMLVolumeThresholdWidget)


                for channelIndex in range(len(channelVolumes)):
                    # Update the state of channels' Visibility, LowerThreshold, UpperThreshold.
                    visibilityParameterName = "Visibility" + str(index) + "_" + str(channelIndex)
                    visibility = (self._parameterNode.GetParameter(visibilityParameterName) == "true")
                    channelLabelName = "ChannelLabel" + str(index) + "_" + str(channelIndex)
                    channelLabel = str(self._parameterNode.GetParameter(channelLabelName))
                    checkBox = checkBoxes[channelIndex]
                    checkBox.setChecked(visibility)
                    checkBox.setText(channelLabel)
                    lowerThresholdParameterName = "LowerThreshold" + str(index) + "_" + str(channelIndex)
                    lowerThreshold = int(float(self._parameterNode.GetParameter(lowerThresholdParameterName)))
                    upperThresholdParameterName = "UpperThreshold" + str(index) + "_" + str(channelIndex)
                    upperThreshold = int(float(self._parameterNode.GetParameter(upperThresholdParameterName)))
                    thresholdSlider = thresholdSliders[channelIndex]
                    thresholdSlider.lowerThreshold = max(lowerThreshold, 1)
                    thresholdSlider.upperThreshold = upperThreshold
                annotationTextNode = self.annotationDict[filepath]
                annotationTextNode.SetText(annotationText)
            currentFile = comboBox.itemData(comboBox.currentIndex)
            if currentFile == filepath:
                groupBox.show()
                self.currentIndex = comboBox.currentIndex
            else:
                groupBox.hide()

        currentIndex = comboBox.findText(currentText)
        comboBox.setCurrentIndex(currentIndex)
        filename = comboBox.itemData(currentIndex)
        if filename:
            if filename in self.InputCheckedDict:
                self.ui.InputCheckBox.checked = self.InputCheckedDict[filename]
            if filename in self.ROINodeDict:
                self.ROINodeDict[filename].GetDisplayNode().SetVisibility(self.ROICheckedDict[filename])
                self.ui.ROICheckBox.setChecked(self.ROICheckedDict[filename])
            if filename in self.annotationDict:
                annotationTextNode = self.annotationDict[filename]
                if annotationTextNode:
                    self.ui.AnnotationText.setMRMLTextNode(annotationTextNode)

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode or self._updatingParameterNodeFromGUI or self._importingScene:
            return

        self._updatingParameterNodeFromGUI = True
        comboBox = self.ui.InputVolumeComboBox
        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        # Image Count
        imageCount = len(self.volumeDict)
        self._parameterNode.SetParameter("Count", str(imageCount))
        if imageCount == 0:
            self._parameterNode.EndModify(wasModified)
            self._updatingParameterNodeFromGUI = False
            return

        self.ui.AnnotationText.saveEdits()

        # The Item Text of current selected volume.
        self._parameterNode.SetParameter("CurrentText", comboBox.currentText)

        # Save data for each image
        for index in range(imageCount):
            indexStr = str(index)

            # Item Text
            self._parameterNode.SetParameter("ItemText" + indexStr, comboBox.itemText(index))

            # Filepath
            filepath = comboBox.itemData(index)
            self._parameterNode.SetParameter("Filepath" + indexStr, filepath)

            # Input Check Box
            if filepath in self.InputCheckedDict:
                self._parameterNode.SetParameter("InputVisibility" + indexStr,
                                                 "true" if self.InputCheckedDict[filepath] else "false")
            # ROI Check Box
            if filepath in self.ROICheckedDict:
                self._parameterNode.SetParameter("ROI" + indexStr, "true" if self.ROICheckedDict[filepath] else "false")
            if filepath in self.ROINodeDict:
                self._parameterNode.SetNodeReferenceID("ROINode" + indexStr, self.ROINodeDict[filepath].GetID())

            # Annotation
            annotationTextNode = self.annotationDict[filepath]
            self._parameterNode.SetNodeReferenceID("AnnotationNode" + indexStr, annotationTextNode.GetID())
            annotationText = annotationTextNode.GetText()
            if not annotationText:
                annotationText = ""
            self._parameterNode.SetParameter("Annotation" + indexStr, annotationText)

            # Channel count
            channelVolumeList = self.volumeDict.get(filepath)
            channelCount = len(channelVolumeList)
            self._parameterNode.SetParameter("Channel Count" + indexStr, str(channelCount))

            # Reference for all channels' volume.
            for channelIndex in range(channelCount):
                volumeParameterName = "Volume" + indexStr + "_" + str(channelIndex)
                volumeID = channelVolumeList[channelIndex].GetID()
                self._parameterNode.SetNodeReferenceID(volumeParameterName, volumeID)

            # The widgets of visibility and threshold sliders for all channels.
            group = self.uiGroupDict[filepath]
            checkBoxes = group.findChildren(qt.QCheckBox)
            thresholdSliders = group.findChildren(slicer.qMRMLVolumeThresholdWidget)

            for channelIndex in range(len(channelVolumeList)):
                channelIndexStr = str(channelIndex)
                checkBox = checkBoxes[channelIndex]
                thresholdSlider = thresholdSliders[channelIndex]
                channelLabelName = "ChannelLabel" + indexStr + "_" + channelIndexStr
                channelLabel = checkBox.text
                self._parameterNode.SetParameter(channelLabelName, channelLabel)
                visibilityParameterName = "Visibility" + indexStr + "_" + channelIndexStr
                visibility = "true" if checkBox.checked else "false"
                self._parameterNode.SetParameter(visibilityParameterName, visibility)
                lowerThresholdParameterName = "LowerThreshold" + indexStr + "_" + channelIndexStr
                self._parameterNode.SetParameter(lowerThresholdParameterName, str(thresholdSlider.lowerThreshold))
                upperThresholdParameterName = "UpperThreshold" + indexStr + "_" + channelIndexStr
                self._parameterNode.SetParameter(upperThresholdParameterName, str(thresholdSlider.upperThreshold))

        self._parameterNode.EndModify(wasModified)
        self._updatingParameterNodeFromGUI = False

    # The slot for threshold checkBox and sliders.
    def connectCheckBoxChangeSlot(self, checkBox, volume):
        checkBox.connect('clicked(bool)', lambda checked: self.logic.setVolumeVisibility(volume, checked, self))

    def connectThresholdChangeSlot(self, thresholdSlider, volume):
        thresholdSlider.connect('thresholdValuesChanged(double, double)',
                                lambda lower, upper: self.logic.updateThresholdOnVolume(volume, lower, upper, self, thresholdSlider))

    def connectRenameChannelButtonChangeSlot(self, renameChannelbutton, volume, subHorizontallayout, checkBox):
        renameChannelbutton.connect('clicked(bool)', lambda checked: self.logic.onRenameChannelButtonClicked(volume, subHorizontallayout, checkBox, self))



#
# ColocZStatsLogic
#

class ColocZStatsLogic(ScriptedLoadableModuleLogic):
    """All the actual computation done by this module.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the threshold slider for each channel triggered.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def updateThresholdOnVolume(self, volNode, lower, upper, widget, thresholdSlider):
        if lower < 1:
            lower = 1
            thresholdSlider.lowerThreshold = 1
        displayNode = volNode.GetDisplayNode()
        displayNode.SetThreshold(lower, upper)
        displayNode.SetApplyThreshold(True)
        widget.updateParameterNodeFromGUI()

    def createVolumesForChannels(self, node, widget):
        """
        Create a volume for each channel to control.
        """
        if not (node and node.IsA("vtkMRMLScalarVolumeNode")):
            return

        volumeStorageNode = node.GetStorageNode()
        if volumeStorageNode:
            filename = volumeStorageNode.GetFileName()
        else:
            return

        if (not filename) or widget.volumeDict.get(filename):
            return
        if not (filename.endswith(".tif") or filename.endswith(".tiff")):
            if filename.endswith(".nrrd"):
                return
            text = "TIFF format Image required."
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText(text)
            msg.setStandardButtons(qt.QMessageBox.Ok)
            msg.exec_()
            return

        redNode = slicer.util.getNode('Red')
        greenNode = slicer.util.getNode('Green')
        blueNode = slicer.util.getNode('Blue')
        yellowNode = slicer.util.getNode('Yellow')
        cyanNode = slicer.util.getNode('Cyan')
        magentaNode = slicer.util.getNode('Magenta')
        greyNode = slicer.util.getNode('Grey')

        warm1Node = slicer.util.getNode('Warm1')
        warm2Node = slicer.util.getNode('Warm2')
        warm3Node = slicer.util.getNode('Warm3')
        cool1Node = slicer.util.getNode('Cool1')
        cool2Node = slicer.util.getNode('Cool2')
        cool3Node = slicer.util.getNode('Cool3')
        warmShade1Node = slicer.util.getNode('WarmShade1')
        warmShade2Node = slicer.util.getNode('WarmShade2')
        warmShade3Node = slicer.util.getNode('WarmShade3')
        colorIds = [redNode.GetID(), greenNode.GetID(), blueNode.GetID(), yellowNode.GetID(), cyanNode.GetID(),
                    magentaNode.GetID(), warm1Node.GetID(), warm2Node.GetID(), warm3Node.GetID(), cool1Node.GetID(),
                    cool2Node.GetID(), cool3Node.GetID(), warmShade1Node.GetID(), warmShade2Node.GetID(),
                    warmShade3Node.GetID()]

        import numpy as np
        print("Loaded image: " + filename)
        tif = tifffile.TiffFile(filename)
        nodeName = node.GetName()
        layout = qt.QVBoxLayout()
        channelVolumeList = list()

        # Find channel dimension to determine how many channels are in the input image.
        channelDim = -1
        ZDim = -1
        axes = tif.series[0].axes
        image = tif.asarray()
        for index in range(0, len(axes)):
            if axes[index] == 'Z':
                ZDim = index
                break

        for index in range(0, len(axes)):
            if axes[index] == 'C':
                channelDim = index
                break
        if ZDim == -1:
            text = "Z-stacked image required."
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText(text)
            msg.setStandardButtons(qt.QMessageBox.Ok)
            msg.exec_()
            slicer.mrmlScene.RemoveNode(node)
            return

        elif ZDim != -1:
            if channelDim != -1:
                image = np.moveaxis(image, channelDim, 0)
                channelNum = image.shape[0]
                if channelNum > 15:
                    text = "Does not support image with channels more than 15."
                    msg = qt.QMessageBox()
                    msg.setIcon(qt.QMessageBox.Warning)
                    msg.setText(text)
                    msg.setStandardButtons(qt.QMessageBox.Ok)
                    msg.exec_()
                    slicer.mrmlScene.RemoveNode(node)
                    return

                dimNum = len(image.shape)
                if dimNum == 4:
                    for component in range(channelNum):
                        componentImage = image[component, :, :, :]
                        name = nodeName + "_" + "Channel " + str(component + 1)
                        channelLabelName = name.split("_")[-1]
                        channelVolume = self.createVolumeForChannel(componentImage, colorIds[component], layout, name, widget,channelLabelName)
                        channelVolumeList.append(channelVolume)
                else:
                    text = "Image data dimension are incompatible. Expected 4. Got " + str(dimNum)
                    msg = qt.QMessageBox()
                    msg.setIcon(qt.QMessageBox.Warning)
                    msg.setText(text)
                    msg.setStandardButtons(qt.QMessageBox.Ok)
                    msg.exec_()
                    slicer.mrmlScene.RemoveNode(node)

            else:
                channelLabelName = node.GetName()
                self.initializeVolume(node, greyNode.GetID(), layout, widget, channelLabelName)
                channelVolumeList.append(node)

        # Update threshold sliders for all channels.
        widget.volumeDict[filename] = channelVolumeList
        widget.InputCheckedDict[filename] = True
        widget.ui.InputCheckBox.checked = True
        groupBox = qt.QGroupBox("")
        widget.uiGroupDict[filename] = groupBox
        layout.addStretch()
        groupBox.setLayout(layout)
        widget.channelsLayout.addWidget(groupBox)
        widget.ui.scrollArea.setWidget(widget.channelsWidget)

        # Update text node for the annotation.
        annotationTextNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTextNode")
        widget.annotationDict[filename] = annotationTextNode

        # Update the comboBox.
        comboBox = widget.ui.InputVolumeComboBox
        comboBox.addItem(node.GetName(), filename)
        currentFile = comboBox.itemData(comboBox.currentIndex)
        if currentFile == filename:
            groupBox.show()
            self.currentIndex = comboBox.currentIndex
        else:
            groupBox.hide()
        if currentFile == filename:
            widget.ui.AnnotationText.setMRMLTextNode(annotationTextNode)

        if not node in channelVolumeList:
            slicer.mrmlScene.RemoveNode(node)

        widget.updateParameterNodeFromGUI()

    def createVolumeForChannel(self, componentImage, colorId, layout, name, widget, channelLabelName):
        """
        Create a volume for each channel to control.
        """
        scalarVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        scalarVolumeNode.SetName(name)
        slicer.util.updateVolumeFromArray(scalarVolumeNode, componentImage)
        self.initializeVolume(scalarVolumeNode, colorId, layout, widget,channelLabelName)
        return scalarVolumeNode

    def initializeVolume(self, scalarVolumeNode, colorId, layout, widget, channelLabelName):
        scalarVolumeNode.CreateDefaultDisplayNodes()
        scalarVolumeNode.GetScalarVolumeDisplayNode().SetAndObserveColorNodeID(colorId)
        volRenLogic = slicer.modules.volumerendering.logic()
        displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(scalarVolumeNode)
        displayNode.SetName(scalarVolumeNode.GetName() + "_Rendering")
        displayNode.SetFollowVolumeDisplayNode(True)
        displayNode.SetVisibility(True)

        # Create widgets for channel volume node
        name = scalarVolumeNode.GetName()
        subHorizontallayout = qt.QHBoxLayout()
        checkBox = qt.QCheckBox(channelLabelName)
        checkBox.objectName = name + "_checkbox"
        checkBox.setChecked(True)
        checkBox.connect('clicked(bool)', lambda checked: self.setVolumeVisibility(scalarVolumeNode, checked, widget))
        subHorizontallayout.addWidget(checkBox)
        renameChannelbutton = qt.QPushButton("Rename Channel")
        renameChannelbutton.objectName = name + "_renameButton"
        renameChannelbutton.connect('clicked(bool)', lambda checked: self.onRenameChannelButtonClicked(scalarVolumeNode,subHorizontallayout,checkBox,widget))
        subHorizontallayout.addWidget(renameChannelbutton)

        threshold = slicer.qMRMLVolumeThresholdWidget()
        threshold.objectName = name + "_threshold"
        threshold.setMRMLVolumeNode(scalarVolumeNode)
        threshold.lowerThreshold = max(1, threshold.lowerThreshold)
        threshold.connect('thresholdValuesChanged(double, double)', lambda lower, upper: self.updateThresholdOnVolume(scalarVolumeNode, lower, upper, widget,threshold))
        layout.addItem(subHorizontallayout)
        layout.addWidget(threshold)

    def onRenameChannelButtonClicked(self, volumeNode,subHorizontallayout, checkBox, widget):
        """
        Called when the 'Rename Channel' button is clicked.
        """
        # Get the current combo box text.
        comboBox = widget.ui.InputVolumeComboBox
        imageName = comboBox.currentText

        text = qt.QInputDialog.getText(subHorizontallayout.parentWidget(), "Rename Channel", "New name:", qt.QLineEdit.Normal,checkBox.text)
        if text:
            newChannelLabelName = str(text)
            newChannelVolumeName = imageName + "_" + newChannelLabelName
            volumeNode.SetName(newChannelVolumeName)
            checkBox.setText(newChannelLabelName)

        widget.updateParameterNodeFromGUI()


    def setVolumeVisibility(self, volumeNode, checked, widget):
        """
        Called when the checkbox of each threshold slider is clicked.
        """
        volRenLogic = slicer.modules.volumerendering.logic()
        displayNode = volRenLogic.GetFirstVolumeRenderingDisplayNode(volumeNode)
        displayNode.SetVisibility(checked and widget.ui.InputCheckBox.checked)
        widget.updateParameterNodeFromGUI()

    def computeStats(self, widget):
        """
        To compute the volume's colocalization percentage within the current ROI.
        """
        comboBox = widget.ui.InputVolumeComboBox
        filename = comboBox.itemData(comboBox.currentIndex)
        channelVolumeList = widget.volumeDict.get(filename)
        if not channelVolumeList:
            return

        roiNode = None
        if filename in widget.ROINodeDict:
            roiNode = widget.ROINodeDict[filename]
        if roiNode:
            # Get the information of ROI
            coords, roiSize, orientationMatrix = self.infoForROI(roiNode)
        else:
            return
        selectedVolumes, thresholds, selectedColors,selectedChannelLabels = self.getSelectedVolumes(channelVolumeList, widget.uiGroupDict[filename])

        # Get all checked channels.
        selectedVolumeCount = len(selectedVolumes)
        if selectedVolumeCount < 2:
            text = "Multi-channel required."
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText(text)
            msg.setStandardButtons(qt.QMessageBox.Ok)
            msg.exec_()
            return

        if selectedVolumeCount > 3:
            text = "Up to 3 channels can be selected simultaneously for calculation."
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText(text)
            msg.setStandardButtons(qt.QMessageBox.Ok)
            msg.exec_()
            return

        # Compute each volume's stats
        self.computeStatsForVolumes(selectedVolumes, roiNode, thresholds, comboBox.currentText, widget, selectedColors,selectedChannelLabels,coords, roiSize, orientationMatrix)


    def getSelectedVolumes(self, channelVolumeList, group):
        """
        Determine which channels are selected, what their thresholds are, and what specific colors they correspond to.
        """
        colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#00ffff', '#ff00ff', '#eb711a', '#baeb1a', '#1aeb86',
                  '#1ab7eb', '#7f1aeb', '#d620a0', '#851d1d', '#9ba33e', '#3e9641']
        selectedVolumes = list()
        selectedColors = list()
        thresholds = list()
        selectedChannelLabels = list()

        checkBoxes = group.findChildren(qt.QCheckBox)
        thresholdSliders = group.findChildren(slicer.qMRMLVolumeThresholdWidget)

        for index in range(len(channelVolumeList)):
            checkBox = checkBoxes[index]
            thresholdSlider = thresholdSliders[index]
            if checkBox.checked:
                selectedChannelLabels.append(checkBox.text)
                selectedVolumes.append(channelVolumeList[index])
                thresholds.append(thresholdSlider.lowerThreshold)
                thresholds.append(thresholdSlider.upperThreshold)
                selectedColors.append(colors[index])
        return selectedVolumes, thresholds, selectedColors,selectedChannelLabels


    def infoForROI(self, roiNode):
        """
        Get the information of ROI.
        """
        # The center of the markups representation. Ex. center of ROI or plane markups.
        # similar as GetCenter()
        for fidIndex in range(roiNode.GetNumberOfControlPoints()):
            coords = [0, 0, 0]
            roiNode.GetNthControlPointPosition(fidIndex, coords)

        # 3x3 orientation matrix of the ROI representation.
        orientationMatrix = list(roiNode.GetNthControlPointOrientationMatrix(0))

        # The size/axis-aligned edge lengths of the ROI.
        roiSize = list(roiNode.GetSize())

        return coords, roiSize, orientationMatrix


    def computeStatsForVolumes(self, volumes, roiNode, thresholds, imageName, widget, colors, ChannelLabels, coords, roiSize, orientationMatrix):
        """
        To compute the volume's colocalization percentage within the current ROI.
        """

        # Save the ROI node into into a markups json file.
        roiNode.AddDefaultStorageNode()
        jsonFileName = slicer.app.defaultScenePath + "/" + imageName + " ROI.mrk.json"
        slicer.util.saveNode(roiNode, jsonFileName)

        # Get cropped and thresholded volume data in numpy array
        cropVolLogic = slicer.modules.cropvolume.logic()
        cropExtent = [0] * 6
        cropVolLogic.GetVoxelBasedCropOutputExtent(roiNode, volumes[0], cropExtent)
        for cropExtentIndex in range(len(cropExtent)):
            if cropExtent[cropExtentIndex] < 0:
                cropExtent[cropExtentIndex] = 0
        workVolumes = list()
        singleChannelVolumes = list()
        lowerThresholdList = list()
        upperThresholdList = list()

        volumeMM3 = 0
        for index in range(len(volumes)):
            volume = volumes[index]
            arrayData = slicer.util.arrayFromVolume(volume)  # Get numpy array data from volume
            volumeMM3 = (arrayData > 0).sum()

            # Crop volume data. Note that numpy array index order is kji, not ijk.
            if roiNode:
                arrayData = arrayData[cropExtent[4]: cropExtent[5], cropExtent[2]: cropExtent[3],
                            cropExtent[0]: cropExtent[1]]
            volumeMM3 = (arrayData > 0).sum()

            # Threshold volume data
            lowerThreshold = thresholds[index * 2]
            upperThreshold = thresholds[index * 2 + 1]
            lowerThresholdList.append(lowerThreshold)
            upperThresholdList.append(upperThreshold)
            newarrayData = np.logical_and(arrayData>=lowerThreshold, arrayData<=upperThreshold)
            newvolumeMM3 = (newarrayData > 0).sum()
            workVolumes.append(newarrayData)
            volumeCM3 = Decimal(str(newvolumeMM3)) * Decimal('0.001')
            singleChannelVolumes.append(volumeCM3)

        # No intersection if there is only one channel
        if len(volumes) == 1:
            return

        # Computes two channels intersection if there are only two channels
        if len(workVolumes) == 2:
            volumeMM3 = np.logical_and(workVolumes[0] > 0, workVolumes[1] > 0).sum()
            volumeCM3 = Decimal(str(volumeMM3)) * Decimal('0.001')
            selectedChannelLabel1 = ChannelLabels[0]
            selectedChannelLabel2 = ChannelLabels[1]

            if imageName in selectedChannelLabel1:
                ChannelLabel1_in_csv  = selectedChannelLabel1
            else:
                ChannelLabel1_in_csv = imageName + "_" + selectedChannelLabel1

            if imageName in selectedChannelLabel2:
                ChannelLabel2_in_csv  = selectedChannelLabel2
            else:
                ChannelLabel2_in_csv = imageName + "_" + selectedChannelLabel2

            self.drawVennForTwoChannels(widget, singleChannelVolumes, volumeCM3, lowerThresholdList, upperThresholdList, colors, selectedChannelLabel1, selectedChannelLabel2, ChannelLabel1_in_csv, ChannelLabel2_in_csv, imageName, coords, roiSize, orientationMatrix, jsonFileName)
            return

        twoChannelsIntersectionVolumes = list()
        for index in range(3):
            secondIndex = index + 1
            if secondIndex == 3:
                secondIndex = 0
            volumeMM3 = np.logical_and(workVolumes[index] > 0, workVolumes[secondIndex] > 0).sum()
            volumeCM3 = Decimal(str(volumeMM3)) * Decimal('0.001')
            twoChannelsIntersectionVolumes.append(volumeCM3)

        volumeMM3 = np.logical_and(np.logical_and(workVolumes[0] > 0, workVolumes[1] > 0), workVolumes[2] > 0).sum()
        volumeCM3 = Decimal(str(volumeMM3)) * Decimal('0.001')
        selectedChannelLabel1 = ChannelLabels[0]
        selectedChannelLabel2 = ChannelLabels[1]
        selectedChannelLabel3 = ChannelLabels[2]

        if imageName in selectedChannelLabel1:
            ChannelLabel1_in_csv = selectedChannelLabel1
        else:
            ChannelLabel1_in_csv = imageName + "_" + selectedChannelLabel1

        if imageName in selectedChannelLabel2:
            ChannelLabel2_in_csv = selectedChannelLabel2
        else:
            ChannelLabel2_in_csv = imageName + "_" + selectedChannelLabel2

        if imageName in selectedChannelLabel2:
            ChannelLabel3_in_csv = selectedChannelLabel3
        else:
            ChannelLabel3_in_csv = imageName + "_" + selectedChannelLabel3

        self.drawVennForThreeChannels(widget, singleChannelVolumes, twoChannelsIntersectionVolumes, volumeCM3,lowerThresholdList,upperThresholdList, colors, selectedChannelLabel1, selectedChannelLabel2, selectedChannelLabel3, ChannelLabel1_in_csv, ChannelLabel2_in_csv, ChannelLabel3_in_csv, imageName, coords, roiSize, orientationMatrix, jsonFileName)

    def drawVennForTwoChannels(self, widget, singleChannelVolumes, intersectionVolume,lowerThresholdList, upperThresholdList, colors, selectedChannelLabel1, selectedChannelLabel2, ChannelLabel1_in_csv, ChannelLabel2_in_csv, imageName, coords, roiSize, orientationMatrix, jsonFileName):
        """
        Draw a Venn diagram showing the colocalization percentage when only two channels are selected.
        """
        p1 = 0
        p2 = 0
        p3 = 0
        totalVolumeOfTwoChannels = singleChannelVolumes[0] + singleChannelVolumes[1] - intersectionVolume

        if float(totalVolumeOfTwoChannels) > 0:
            result1 = format(float(((singleChannelVolumes[0] - intersectionVolume) / totalVolumeOfTwoChannels) * Decimal('100.0000')), '.4f')
            result2 = format(float(((singleChannelVolumes[1] - intersectionVolume) / totalVolumeOfTwoChannels) * Decimal('100.0000')), '.4f')
            result3 = format(float((intersectionVolume / totalVolumeOfTwoChannels) * Decimal('100.0000')), '.4f')
            result_list = [Decimal(result1), Decimal(result2), Decimal(result3)]
            if result_list.count(max(result_list)) == 2 and max(result_list) == Decimal('50.0000'):
                p1 = result1
                p2 = result2
                p3 = result3
            else:
                result_sum = Decimal('0.0000')
                for i in result_list:
                    if i != max(result_list):
                        result_sum += i
                result_list[result_list.index(max(result_list))] = Decimal('100.0000') - result_sum

                # Get the specific percentage value corresponding to each part of the Venn diagram.
                p1 = format(float(result_list[0]), '.4f')
                p2 = format(float(result_list[1]), '.4f')
                p3 = format(float(result_list[2]), '.4f')
            sum1 = format(float((result_list[0] + result_list[2])), '.4f')
            sum2 = format(float((result_list[1] + result_list[2])), '.4f')

            print("The threshold range of " + ChannelLabel1_in_csv + " is: " + str(lowerThresholdList[0]) + "-" + str(upperThresholdList[0]))
            print("The threshold range of " + ChannelLabel2_in_csv + " is: " + str(lowerThresholdList[1]) + "-" + str(upperThresholdList[1]))
            print("The percentage of " + ChannelLabel1_in_csv + " is: " + sum1 + "%")
            print("The percentage of " + ChannelLabel2_in_csv + " is: " + sum2 + "%")
            print("The percentage of intersection between " + ChannelLabel1_in_csv + " and " + ChannelLabel2_in_csv + " is:" + p3 + "%")
            print("Calculation completed.")
            print("------------------------------")
        else:
            print("Total volume is 0.")

        # Display and save the Venn diagram.
        my_dpi = 100
        plt.figure(figsize=(800 / my_dpi, 600 / my_dpi), dpi=my_dpi)
        venn2_unweighted(subsets=[p1, p2, p3], set_labels=[selectedChannelLabel1, selectedChannelLabel2],
                         set_colors=(colors[0], colors[1]),
                         alpha=0.6)
        plt.title("Volume Percentage(%)\n" + imageName, fontsize=18)
        vennImagename = imageName + ' Venn diagram.jpg'
        vennImagefileLocation = slicer.app.defaultScenePath + "/" + vennImagename
        plt.savefig(vennImagefileLocation)
        pm = qt.QPixmap(vennImagefileLocation)
        if not widget.imageWidget:
            widget.imageWidget = qt.QLabel()
        widget.imageWidget.setPixmap(pm)
        widget.imageWidget.setScaledContents(True)
        widget.imageWidget.show()

        # Create a spreadsheet to save the colocalization and ROI information.
        coords_str = "[" + str(-coords[0]) + ", " + str(-coords[1]) + ", " + str(coords[2]) + "]"
        orientation_str = "[" + str(-orientationMatrix[0]) + ", " + str(-orientationMatrix[1]) + ", " + str(-orientationMatrix[2]) + ", " + str(-orientationMatrix[3]) + ", " + str(-orientationMatrix[4]) + ", " + str(-orientationMatrix[5]) + ", " + str(orientationMatrix[6]) + ", " + str(orientationMatrix[7]) + ", " + str(orientationMatrix[8]) + "]"
        roiSize_str = "[" + str(roiSize[0]) + ", " + str(roiSize[1]) + ", " + str(roiSize[2]) + "]"

        volume_colocalization_column_1 = [ChannelLabel1_in_csv + " (includes all intersections)", ChannelLabel2_in_csv+ " (includes all intersections)", ChannelLabel1_in_csv + " ∩ " + ChannelLabel2_in_csv]
        volume_colocalization_column_2 = [str(Decimal(sum1)) + "%", str(Decimal(sum2)) + "%", str(Decimal(p3)) + "%"]
        volume_colocalization_column_3 = [str(lowerThresholdList[0]), str(lowerThresholdList[1])]
        volume_colocalization_column_4 = [str(upperThresholdList[0]), str(upperThresholdList[1])]
        cell_colocalization = {'Colocalization Statistics': volume_colocalization_column_1, 'Volume overlaps': volume_colocalization_column_2, 'Threshold range (min)': volume_colocalization_column_3, 'Threshold range (max)': volume_colocalization_column_4}

        ROI_Information_column_1 = ["Coordinate System: ", "Center: ", "Orientation: ", "Size: ", "ROI JSON File location: "]
        ROI_Information_column_2 = ["LPS", coords_str, orientation_str, roiSize_str, jsonFileName]
        ROI_Information = {"ROI Information": ROI_Information_column_1, "Values": ROI_Information_column_2}

        df1 = pd.DataFrame.from_dict(cell_colocalization, orient='index')
        df1 = df1.transpose()
        df2 = pd.DataFrame.from_dict(ROI_Information, orient='index')
        df2 = df2.transpose()

        excel_out_path = slicer.app.defaultScenePath + "/" + imageName + " Statistics.xlsx"
        writer = pd.ExcelWriter(excel_out_path , engine='xlsxwriter')
        df1.to_excel(writer, sheet_name = 'Colocalization', index=False)
        df2.to_excel(writer, sheet_name = 'ROI Information', header=False, index=False)
        writer.save()

    def drawVennForThreeChannels(self, widget, singleChannelVolumes, twoChannelsIntersectionVolumes, intersection_1_2_3,
                                 lowerThresholdList, upperThresholdList, colors, selectedChannelLabel1, selectedChannelLabel2, selectedChannelLabel3,  ChannelLabel1_in_csv, ChannelLabel2_in_csv, ChannelLabel3_in_csv, imageName, coords, roiSize, orientationMatrix, jsonFileName):
        """
        Draw a Venn diagram showing the colocalization percentage when three channels are selected.
        """
        totalVolumeOfTwoChannels = singleChannelVolumes[0] + singleChannelVolumes[1] - twoChannelsIntersectionVolumes[0]
        totalVolumeOfThreeChannels = totalVolumeOfTwoChannels + singleChannelVolumes[2] - twoChannelsIntersectionVolumes[2] - (twoChannelsIntersectionVolumes[1] - intersection_1_2_3)

        p1 = 0
        p2 = 0
        p3 = 0
        p4 = 0
        p5 = 0
        p6 = 0
        p7 = 0

        if float(totalVolumeOfThreeChannels) > 0:
            result1 = format(float((((singleChannelVolumes[0] - twoChannelsIntersectionVolumes[0]) - (twoChannelsIntersectionVolumes[2] - intersection_1_2_3)) / totalVolumeOfThreeChannels) * Decimal('100.0000')), '.4f')
            result2 = format(float((((singleChannelVolumes[1] - twoChannelsIntersectionVolumes[0]) - (twoChannelsIntersectionVolumes[1] - intersection_1_2_3)) / totalVolumeOfThreeChannels) * Decimal('100.0000')), '.4f')
            result3 = format(float(((twoChannelsIntersectionVolumes[0] - intersection_1_2_3) / totalVolumeOfThreeChannels) * Decimal('100.0000')), '.4f')
            result4 = format(float((((singleChannelVolumes[2] - twoChannelsIntersectionVolumes[1]) - (twoChannelsIntersectionVolumes[2] - intersection_1_2_3)) / totalVolumeOfThreeChannels) * Decimal('100.0000')) , '.4f')
            result5 = format(float(((twoChannelsIntersectionVolumes[2] -intersection_1_2_3) / totalVolumeOfThreeChannels) * Decimal('100.0000')), '.4f')
            result6 = format(float(((twoChannelsIntersectionVolumes[1] - intersection_1_2_3) / totalVolumeOfThreeChannels) * Decimal('100.0000')), '.4f')
            result7 = format(float((intersection_1_2_3 / totalVolumeOfThreeChannels) * Decimal('100.0000')), '.4f')
            result_list = [Decimal(result1), Decimal(result2), Decimal(result3), Decimal(result4), Decimal(result5), Decimal(result6), Decimal(result7)]

            if result_list.count(max(result_list)) == 3 and max(result_list) == Decimal('33.3333'):
                p1 = result1
                p2 = result2
                p3 = result3
                p4 = result4
                p5 = result5
                p6 = result6
                p7 = result7
            else:
                result_sum = Decimal('0.0000')
                for i in result_list:
                    if i != max(result_list):
                        result_sum += i
                result_list[result_list.index(max(result_list))] = Decimal('100.0000') - result_sum

                # Get the specific percentage value corresponding to each part of the Venn diagram.
                p1 = format(float(result_list[0]), '.4f')
                p2 = format(float(result_list[1]), '.4f')
                p3 = format(float(result_list[2]), '.4f')
                p4 = format(float(result_list[3]), '.4f')
                p5 = format(float(result_list[4]), '.4f')
                p6 = format(float(result_list[5]), '.4f')
                p7 = format(float(result_list[6]), '.4f')

            sum1_2 = format(float((result_list[2] + result_list[6])), '.4f')
            sum1_3 = format(float((result_list[4] + result_list[6])), '.4f')
            sum2_3 = format(float((result_list[5] + result_list[6])), '.4f')
            sum1 = format(float((result_list[0] + result_list[4] + result_list[2] + result_list[6])), '.4f')
            sum2 = format(float((result_list[1] + result_list[5] + result_list[2] + result_list[6])), '.4f')
            sum3 = format(float((result_list[3] + result_list[4] + result_list[5] + result_list[6])), '.4f')

            print("The threshold range of " + ChannelLabel1_in_csv + " is: " + str(lowerThresholdList[0]) + "-" + str(upperThresholdList[0]))
            print("The threshold range of " + ChannelLabel2_in_csv + " is: " + str(lowerThresholdList[1]) + "-" + str(upperThresholdList[1]))
            print("The threshold range of " + ChannelLabel3_in_csv + " is: " + str(lowerThresholdList[2]) + "-" + str(upperThresholdList[2]))
            print("The percentage of " + ChannelLabel1_in_csv + " is:" + sum1 + "%")
            print("The percentage of " + ChannelLabel2_in_csv + " is:" + sum2 + "%")
            print("The percentage of " + ChannelLabel3_in_csv + " is:" + sum3 + "%")
            print("The percentage of intersection between " + ChannelLabel1_in_csv + " and " + ChannelLabel2_in_csv + " is:" + sum1_2 + "%")
            print("The percentage of intersection between " + ChannelLabel1_in_csv + " and " + ChannelLabel3_in_csv + " is:" + sum1_3 + "%")
            print("The percentage of intersection between " + ChannelLabel2_in_csv + " and " + ChannelLabel3_in_csv + " is:" + sum2_3 + "%")
            print("The percentage of the intersection of the three channels is: " + p7 + "%")
            print("Calculation completed.")
            print("------------------------------")
        else:
            print("Total volume is 0.")

        # Create a Venn diagram.
        my_dpi = 100
        plt.figure(figsize=(800 / my_dpi, 600 / my_dpi), dpi=my_dpi)
        venn3_unweighted(subsets=[p1, p2, p3, p4, p5, p6, p7],
                         set_labels=[selectedChannelLabel1, selectedChannelLabel2, selectedChannelLabel3],
                         set_colors=(colors[0], colors[1], colors[2]), alpha=0.6)
        plt.title("Volume Percentage(%)\n" + imageName, fontsize=18)
        vennImagename = imageName + ' Venn diagram.jpg'
        vennImagefileLocation = slicer.app.defaultScenePath + "/" + vennImagename
        plt.savefig(vennImagefileLocation)
        pm = qt.QPixmap(vennImagefileLocation)
        if not widget.imageWidget:
            widget.imageWidget = qt.QLabel()
        widget.imageWidget.setPixmap(pm)
        widget.imageWidget.setScaledContents(True)
        widget.imageWidget.show()

        # Create a spreadsheet to save the colocalization and ROI information.
        coords_str = "[" + str(-coords[0]) + ", " + str(-coords[1]) + ", " + str(coords[2]) + "]"
        orientation_str = "[" + str(-orientationMatrix[0]) + ", " + str(-orientationMatrix[1]) + ", " + str(-orientationMatrix[2]) + ", " + str(-orientationMatrix[3])  + ", " + str(-orientationMatrix[4]) + ", " + str(-orientationMatrix[5]) + ", " + str(orientationMatrix[6]) + ", " + str(orientationMatrix[7]) + ", " + str(orientationMatrix[8]) + "]"
        roiSize_str = "[" + str(roiSize[0]) + ", " + str(roiSize[1]) + ", " + str(roiSize[2]) + "]"

        volume_colocalization_column_1 = [ChannelLabel1_in_csv + " (includes all intersections)", ChannelLabel2_in_csv+ " (includes all intersections)",ChannelLabel3_in_csv+ " (includes all intersections)", ChannelLabel1_in_csv + " ∩ " + ChannelLabel2_in_csv, ChannelLabel1_in_csv + " ∩ " + ChannelLabel3_in_csv, ChannelLabel2_in_csv + " ∩ " + ChannelLabel3_in_csv, ChannelLabel1_in_csv + " ∩ " + ChannelLabel2_in_csv + " ∩ " + ChannelLabel3_in_csv]
        volume_colocalization_column_2 = [str(Decimal(sum1)) + "%", str(Decimal(sum2)) + "%" , str(Decimal(sum3)) + "%" , str(Decimal(sum1_2)) + "%",str(Decimal(sum1_3)) + "%",str(Decimal(sum2_3)) + "%", str(Decimal(p7)) + "%"]
        volume_colocalization_column_3 = [str(lowerThresholdList[0]), str(lowerThresholdList[1]), str(lowerThresholdList[2])]
        volume_colocalization_column_4 = [str(upperThresholdList[0]), str(upperThresholdList[1]), str(upperThresholdList[2])]
        cell_colocalization = {'Colocalization Statistics': volume_colocalization_column_1, 'Volume overlaps': volume_colocalization_column_2, 'Threshold range (min)': volume_colocalization_column_3, 'Threshold range (max)': volume_colocalization_column_4}

        ROI_Information_column_1 = ["Coordinate System: ", "Center: ", "Orientation: ", "Size: ", "ROI JSON File location: "]
        ROI_Information_column_2 = ["LPS", coords_str, orientation_str, roiSize_str, jsonFileName]
        ROI_Information = {"ROI Information": ROI_Information_column_1, "Values": ROI_Information_column_2}

        df1 = pd.DataFrame.from_dict(cell_colocalization, orient = 'index')
        df1 = df1.transpose()
        df2 = pd.DataFrame.from_dict(ROI_Information, orient = 'index')
        df2 = df2.transpose()
        excel_out_path = slicer.app.defaultScenePath + "/" + imageName + " Statistics.xlsx"
        writer = pd.ExcelWriter(excel_out_path, engine='xlsxwriter')
        df1.to_excel(writer, sheet_name = 'Colocalization', index=False)
        df2.to_excel(writer, sheet_name = 'ROI Information',header=False, index=False)
        writer.save()


#
# ColocZStatsTest
#
class ColocZStatsTest(ScriptedLoadableModuleTest):
    """
    The test case.
    """

    def runTest(self):
        self.test_ColocZStats()

    def test_ColocZStats(self):
        self.delayDisplay("Starting the test")
        self.delayDisplay('Test passed!')
