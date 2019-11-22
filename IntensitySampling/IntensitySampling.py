import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# IntensitySampling
#

class IntensitySampling(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "IntensitySampling" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Sequences"]
    self.parent.dependencies = []
    self.parent.contributors = ["Junichi Tokuda (BWH)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# IntensitySamplingWidget
#

class IntensitySamplingWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    ####################
    # For debugging
    #
    # Reload and Test area
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)
    
    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "CurveMaker Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)
    #
    ####################

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Input sequence node selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vktMRMLSequenceNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Select a sequence node that contains a serial image." )
    parametersFormLayout.addRow("Input Image Sequence: ", self.inputSelector)

    #
    # Input Label node selector
    #
    self.inputLabelSelector = slicer.qMRMLNodeComboBox()
    self.inputLabelSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.inputLabelSelector.selectNodeUponCreation = True
    self.inputLabelSelector.addEnabled = False
    self.inputLabelSelector.removeEnabled = False
    self.inputLabelSelector.noneEnabled = False
    self.inputLabelSelector.showHidden = False
    self.inputLabelSelector.showChildNodeTypes = False
    self.inputLabelSelector.setMRMLScene( slicer.mrmlScene )
    self.inputLabelSelector.setToolTip( "Select a sequence node that contains a serial image." )
    parametersFormLayout.addRow("Input Label: ", self.inputLabelSelector)

    
    ##
    ## output file Selector
    ##
    outputFileLayout = qt.QHBoxLayout()
    
    self.outputFileEdit = qt.QLineEdit()
    self.outputFileEdit.text = ''
    self.outputFileEdit.readOnly = True
    self.outputFileEdit.frame = True
    self.outputFileEdit.styleSheet = "QLineEdit { background:transparent; }"
    self.outputFileEdit.cursor = qt.QCursor(qt.Qt.IBeamCursor)

    self.outputFileBrowserButton = qt.QPushButton()
    self.outputFileBrowserButton.setText("...")

    self.outputFileDialog = qt.QFileDialog()
    
    outputFileLayout.addWidget(self.outputFileEdit)
    outputFileLayout.addWidget(self.outputFileBrowserButton)
    parametersFormLayout.addRow("Output File (CSV): ", outputFileLayout)

    #self.outputSelector = slicer.qMRMLNodeComboBox()
    #self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    #self.outputSelector.selectNodeUponCreation = True
    #self.outputSelector.addEnabled = True
    #self.outputSelector.removeEnabled = True
    #self.outputSelector.noneEnabled = True
    #self.outputSelector.showHidden = False
    #self.outputSelector.showChildNodeTypes = False
    #self.outputSelector.setMRMLScene( slicer.mrmlScene )
    #self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    #parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    ##
    ## check box to trigger taking screen shots for later use in tutorials
    ##
    #self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    #self.enableScreenshotsFlagCheckBox.checked = 0
    #self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    #parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputFileBrowserButton.connect('clicked(bool)', self.onInputFileBrowser)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    #self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()
    pass

  def onApplyButton(self):
    logic = IntensitySamplingLogic()
    #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    #logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)


  def onInputFileSelector(self):
    outputFilePath = self.outputFileDialog.getExistingDirectory()

    if self.savingSeperateChannelCheckBox.checked == True:
      self.importDirString = self.fileDialog.getExistingDirectory()
      if len(self.importDirString) > self.maximumFileNameLen:
        self.inputFileBrowserButton.setText(".." + self.importDirString[-self.maximumFileNameLen:])
    else:
      self.fileString = self.fileDialog.getOpenFileName()
      if len(self.fileString)>self.maximumFileNameLen:
        self.inputFileBrowserButton.setText(".." + self.fileString[-self.maximumFileNameLen:])
    
    
#
# IntensitySamplingLogic
#

class IntensitySamplingLogic(ScriptedLoadableModuleLogic):

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    logging.info('Processing completed')

    return True


class IntensitySamplingTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    #self.test_IntensitySampling1()
    
  #def test_IntensitySampling1(self):
  #  """ Ideally you should have several levels of tests.  At the lowest level
  #  tests should exercise the functionality of the logic with different inputs
  #  (both valid and invalid).  At higher levels your tests should emulate the
  #  way the user would interact with your code and confirm that it still works
  #  the way you intended.
  #  One of the most important features of the tests is that it should alert other
  #  developers when their changes will have an impact on the behavior of your
  #  module.  For example, if a developer removes a feature that you depend on,
  #  your test should break so they know that the feature is needed.
  #  """
  #
  #  self.delayDisplay("Starting the test")
  #  #
  #  # first, get some data
  #  #
  #  import SampleData
  #  SampleData.downloadFromURL(
  #    nodeNames='FA',
  #    fileNames='FA.nrrd',
  #    uris='http://slicer.kitware.com/midas3/download?items=5767',
  #    checksums='SHA256:12d17fba4f2e1f1a843f0757366f28c3f3e1a8bb38836f0de2a32bb1cd476560')
  #  self.delayDisplay('Finished with download and loading')
  #
  #  volumeNode = slicer.util.getNode(pattern="FA")
  #  logic = IntensitySamplingLogic()
  #  self.assertIsNotNone( logic.hasImageData(volumeNode) )
  #  self.delayDisplay('Test passed!')
