import sys
import os
import re
from os.path import basename, dirname, isfile
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import piexif
import photoOrg_MainWindow

class MainWindow(QtWidgets.QMainWindow, photoOrg_MainWindow.Ui_MainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.installEventFilter(self)
        self.actionOpen_Files.triggered.connect(self.ChooseFiles)
        self.actionExit.triggered.connect(self.ExitApp)
        self.actionSortPhotoListAlphabetically.triggered.connect(self.SortPhotoListAlphabetically)
        self.actionSortPhotoListByOriginalDate.triggered.connect(self.SortPhotoListByOriginalDate)
        self.btnChangeDate.clicked.connect(self.WriteExifDate)
        self.btnChangeDate.setEnabled(False)
        self.btnChangeExif.clicked.connect(self.WriteExifData)
        self.btnChangeExif.setEnabled(False)
        self.btnDelete.clicked.connect(self.DeleteFiles)
        self.btnDelete.setEnabled(False)
        self.btnOpen.clicked.connect(self.ChooseFiles)
        self.btnRename.clicked.connect(self.RenameFiles)
        self.btnRename.setEnabled(True)
        self.btnRotate.clicked.connect(self.RotateImages)
        self.btnRotate.setEnabled(True)
        self.cboDateEdit.addItems(["Edit all parts",  "Edit year", "Edit month", "Edit day"])
        self.cboDateFiles.addItems(["Selected only",  "All files"])
        self.cboDateFiles.currentIndexChanged.connect(self.ComboDateFilesChanged)
        self.cboDateOptions.addItems(["No date",  "YMDhms",  "YMD_hms",  "Y-M-D_hms",  "Y-M-D_h-m-s",  "Custom"])
        self.cboDateOptions.currentIndexChanged.connect(self.ComboboxDateOptionsChanged)
        self.cboExifFiles.addItems(["Selected only",  "All files"])
        self.cboExifFiles.currentIndexChanged.connect(self.ComboExifFilesChanged)
        self.cboFilenameBase.addItems(["Use existing file name",  "Specify base name"])
        self.cboFilenameBase.currentIndexChanged.connect(self.ComboboxFilenameBaseChanged)
        self.cboMirror.addItems(["No mirroring", "Horizontal",  "Vertical"])
        self.cboNumberPosition.addItems(["Number at start",  "Number at end"])
        self.cboNumberPosition.currentIndexChanged.connect(self.DisplayNewFilename)
        self.cboNumbers.addItems(["From 1",  "From 1, pad zeros" ,"Specify start" ,"Specify start, pad zeros" ,  "No number"])
        self.cboNumbers.currentIndexChanged.connect(self.ComboboxNumbersChanged)
        self.cboRenameFiles.addItems(["Selected only",  "All files"])
        self.cboRenameFiles.currentIndexChanged.connect(self.ComboRenameFilesChanged)
        self.cboRotate.addItems(["No rotation", "90 clockwise",  "180 clockwise",  "270 clockwise"])
        self.cboRotateFiles.addItems(["Selected only",  "All files"])
        self.cboRotateFiles.currentIndexChanged.connect(self.ComboRotateFilesChanged)
        self.cboRenameFiles.currentIndexChanged.connect(self.ComboRenameFilesChanged)
        self.cboSuffix.addItems(["Use existing suffix", "Upper case",  "Lower case", "Custom"])
        self.cboSuffix.currentIndexChanged.connect(self.ComboboxSuffixChanged)
        self.cboThumbnail.addItems(["Write if absent", "Write all (500x281)"])
        self.cboTimeEdit.addItems(["Edit all parts",  "Edit hour", "Edit minute", "Edit second"])
        self.cboTimeShift.addItems(["Add",  "Subtract"])
        self.chkOriginalDate.stateChanged.connect(self.CheckOriginalDateChanged)
        self.chkOriginalTime.stateChanged.connect(self.CheckOriginalTimeChanged)
        self.chkShiftDate.stateChanged.connect(self.CheckShiftDateChanged)
        self.chkDelete.stateChanged.connect(self.CheckDeleteChanged)
        self.chkDeleteXMP.stateChanged.connect(self.CheckDeleteChanged)
        self.db =photoDb(self)
        self.lblCustomSuffix.hide()
        self.lblDatePattern.hide()
        self.lblFilename.hide()
        self.lblProgressBar.hide()
        self.lblStartValue.hide()
        self.lstPhotos.clicked.connect(self.ListPhotosClicked)
        self.lstPhotos.installEventFilter(self)
        self.lstPhotos.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.lstPhotos.setIconSize(QtCore.QSize(100,100))
        self.lstPhotos.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.progressBar.hide()
        self.setStyleSheet(self.thisMainWindowStylesheet)
        self.timeOriginalDate.dateChanged.connect(self.TimeOriginalDateChanged)
        self.timeOriginalDate.installEventFilter(self)
        self.timeOriginalDate.setDate(QtCore.QDate.currentDate())
        self.txtDatePattern.hide()
        self.txtDatePattern.installEventFilter(self)
        self.txtFilename.hide()
        self.txtFilename.installEventFilter(self)
        self.txtShiftSecond.installEventFilter(self)
        self.txtStartNumber.hide()
        self.txtStartNumber.installEventFilter(self)
        self.txtSuffix.hide()
        self.txtSuffix.installEventFilter(self)
        #cycle through all checkboxes, radiobuttons and comboboxes and set their click events
        for c in self.tabExifData.children():
            if "txt" in c.objectName(): c.installEventFilter(self)
            if "chk" in c.objectName(): c.clicked.connect(self.ExifCheckboxClicked)
        for c in self.tabDate.children():
            if "txt" in c.objectName(): c.installEventFilter(self)

    #set global variables, including stylesheet information for both the app and its dialogs.
    #we need three stylesheets for different window parts because the main window, file open box, and other msg boxes
    #each need slightly different styles. The key difference is the color and behavior of active/selected buttons.
    thisPath = ""
    thisStylesheetBase = """
                QListWidget:item:selected {
                    background: rgb(56,114,189)
                }
                QListWidget:item:!active {
                    color: silver
                }
                QLabel {
                    border: none
                }
                QTabWidget::pane {
                    border: 1px solid silver
                }
                QTabWidget::tab-bar:top {
                    top: 1px
                }
                QTabWidget::tab-bar:bottom {
                    bottom: 1px
                }
                QTabWidget::tab-bar:left {
                    right: 1px
                }
                QTabWidget::tab-bar:right {
                    left: 1px
                }
                QTabBar::tab {
                    border: 1px solid silver;
                    min-width: 7ex;
                    padding: 3px
                }
                QTabBar::tab:selected {
                    background: rgb(80,80,80);
                    color: white
                }
                QLineEdit {
                    border: 1px solid silver;
                    color:  rgb(56,114,189)
                }
                QHeaderView::section {
                    background-color: rgb(50,50,50);
                    color: silver;
                    padding-left: 4px;
                    border: none
                }
                QComboBox {
                    border-radius: 0px;
                    padding: 1px 18px 1px 3px;
                    min-width: 3em;
                    color:  rgb(56,114,189)
                } """
    thisMainWindowStylesheetAdditions = """
                QWidget {
                    border: none;
                    background: black;
                    color: silver
                }
                QCheckBox:indicator:unchecked {
                    background-color: white;
                }
                QCheckBox:indicator:checked {
                    background-color: blue;
                }
                QProgressBar {
                    border: none;
                    border-radius: 0px;
                    text-align: center;
                    color: black;
                    background-color: silver
                }
                QProgressBar:chunk{
                    border: none;
                    border-radius: 0px;
                    text-align: center;
                    color: rgb(56,114,189);
                    background-color: rgb(56,114,189)
                }
                QPushButton {
                    background-color: rgb(80,80,80);
                    border-radius: 0px;
                    padding: 5px;
                    min-width: 5em;
                    outline: none
                }
                QComboBox {
                    border: none;
                    border-radius: 0px;
                    padding: 1px 18px 1px 3px;
                    min-width: 6em;
                    color: silver
                }
                QScrollBar:vertical {
                    background: rgb(56,114,189);
                    width: 10px;
                    margin: 0px 0px 0px 0px;
                }"""
    thisDialogStylesheetAdditions = """
                QWidget {
                    border: none;
                    background: rgb(50,50,50);
                    color: silver
                }
                QScrollBar:vertical {
                    background: rgb(80,80,80);
                    width: 10px;
                    margin: 0px 0px 0px 0px;
                    border: none
                }
                QScrollBar:horizontal {
                    background: rgb(80,80,80);
                    width: 10px;
                    margin: 0px 0px 0px 0px;
                    border: none
                }"""
    thisPushButtonsWhiteTextStylesheet = """
                    QPushButton:!focus {
                    color: white;
                    background-color: rgb(80,80,80);
                    border-radius: 0px;
                    padding: 5px;
                    min-width: 5em
                }
                QPushButton:focus {
                    color: white;
                    background-color: rgb(80,80,80);
                    border-radius: 0px;
                    padding: 5px;
                    min-width: 5em;
                    outline: none
                }"""
    thisPushButtonsUnfocusedGrayTextStylesheet = """
                    QPushButton:!focus {
                    color: rgb(120,120,120);
                    background-color: rgb(80,80,80);
                    border-radius: 0px;
                    padding: 5px;
                    min-width: 5em
                }
                QPushButton:focus {
                    color: white;
                    background-color: rgb(80,80,80);
                    border-radius: 0px;
                    padding: 5px;
                    min-width: 5em;
                    outline: none
                }"""
    #concatenate stylesheet strings for their appropriate use. The different dialog boxes need different color values for
    #selected and unselected buttons.
    thisDialogStylesheet = thisDialogStylesheetAdditions + thisStylesheetBase + thisPushButtonsUnfocusedGrayTextStylesheet
    thisMainWindowStylesheet = thisMainWindowStylesheetAdditions + thisStylesheetBase + thisPushButtonsWhiteTextStylesheet
    thisFileDialogStylesheet = thisDialogStylesheetAdditions + thisStylesheetBase + thisPushButtonsWhiteTextStylesheet


    def keyPressEvent(self, e):
        # open file dalog routine if user presses Crtl-O
        if e.key() == QtCore.Qt.Key_O and e.modifiers() & QtCore.Qt.ControlModifier:
            self.ChooseFiles()

        # open file dalog routine if user presses Crtl-O
        if e.key() == QtCore.Qt.Key_F11:
            self.ToggleFullScreen()
            

    def CheckIfRenamingWouldOverwriteFiles(self):
        #get selected rows from lstPhotos, as long as it has rows to select
        #loop through selected rows and return true of file with newName already exists
        #allow the renaming of file to proceed if it would only overwrite itself
        #if new filename appears twice in the list of new filenames, return true
        #return false if no overwriting would occur
        if self.lstPhotos.count() > 0:
            selRows = self.GetAffectedRows("chosen")
            newNames = []
            for r in selRows:
                n = self.GetNewFilename(r)
                newNames.append(n)
                if isfile(n) and basename(n) != str(self.lstPhotos.item(r).text()):
                    return True
            for n in newNames:
                if newNames.count(n) > 1:
                    return True
        return False

    def ComboDateFilesChanged(self):
        self.cboRenameFiles.setCurrentIndex(self.cboDateFiles.currentIndex())
        self.cboExifFiles.setCurrentIndex(self.cboDateFiles.currentIndex())
        self.DisplayNewFilename()
        self.DisplayEXIFData()

    def ComboExifFilesChanged(self):
        self.cboRenameFiles.setCurrentIndex(self.cboExifFiles.currentIndex())
        self.cboDateFiles.setCurrentIndex(self.cboExifFiles.currentIndex())
        self.cboRotateFiles.setCurrentIndex(self.cboExifFiles.currentIndex())
        self.DisplayNewFilename()
        self.DisplayEXIFData()

    def ComboRenameFilesChanged(self):
        self.cboExifFiles.setCurrentIndex(self.cboRenameFiles.currentIndex())
        self.cboDateFiles.setCurrentIndex(self.cboRenameFiles.currentIndex())
        self.cboRotateFiles.setCurrentIndex(self.cboRenameFiles.currentIndex())
        self.DisplayNewFilename()
        self.DisplayEXIFData()

    def ComboRotateFilesChanged(self):
        self.cboRenameFiles.setCurrentIndex(self.cboExifFiles.currentIndex())
        self.cboExifFiles.setCurrentIndex(self.cboRotateFiles.currentIndex())
        self.cboDateFiles.setCurrentIndex(self.cboRotateFiles.currentIndex())
        self.DisplayNewFilename()
        self.DisplayEXIFData()
        
    def ComboboxFilenameBaseChanged(self):
        if self.cboFilenameBase.currentText() == "Specify base name":
            self.txtFilename.show()
            self.lblFilename.show()
        else:
            self.txtFilename.hide()
            self.lblFilename.hide()
        self.DisplayNewFilename()

    def ComboboxNumbersChanged(self):
        if "Specify start" in self.cboNumbers.currentText():
            self.txtStartNumber.show()
            self.lblStartValue.show()
        else:
            self.txtStartNumber.hide()
            self.lblStartValue.hide()
        self.DisplayNewFilename()

    def ComboboxDateOptionsChanged(self):
        if self.cboDateOptions.currentText() == "Custom":
            self.txtDatePattern.show()
            self.lblDatePattern.show()
        else:
            self.txtDatePattern.hide()
            self.lblDatePattern.hide()
        self.DisplayNewFilename()

    def ComboboxSuffixChanged(self):
        if "Custom" in self.cboSuffix.currentText():
            self.txtSuffix.show()
            self.lblCustomSuffix.show()
        else:
            self.txtSuffix.hide()
            self.lblCustomSuffix.hide()
        self.DisplayNewFilename()
        
    def ConvertPixmapToJpeg(self, pm,  fmt='JPG'):
        #routine to get thumbnail jpeg from the lstPhotos icons
        #this saves time compared to reading the thumbnails from scratch from the files on disk
        #piexif requires thumbnail to be in bytearray format (raw JPEG data)
        #check if bytearray is below 50K so the resulting EXIF data will be less than 64K spec limit
        #if bytearray is too large, trim the height and width by 10 pixels and recheck size until under 50K
        array = QtCore.QByteArray()
        firstPass = True
        while len(array) > 50000 or firstPass is True:
            if firstPass is False: pm = pm.scaled(pm.height()-10, pm.width()-10, QtCore.Qt.KeepAspectRatio)
            array = QtCore.QByteArray()
            buffer = QtCore.QBuffer(array)
            buffer.open(QtCore.QIODevice.WriteOnly)
            pm.save(buffer, fmt)
            buffer.close()
            firstPass = False
        return array.data()#return the thumbnail in raw JPEG bytearray format

    def DateCheckboxClicked(self):
        #this routine enables the Change Exif button if an any checkbox  on tabEIFData is clicked on
        #start by setting flag to false.  It will be set to true only if a checkbox is found to be checked
        #loop thorugh all objects on the tab, and check if a checkbox is set to true
        self.btnChangeDate.setEnabled(False)
        for c in self.tabDate.children():
            if "chk" in c.objectName():
                if c.isChecked(): self.btnChangeDate.setEnabled(True)

    def DeleteFiles(self):
        if self.lstPhotos.count() > 0:

            itemCount = self.GetAffectedRowsCount("delete")
            
            if itemCount > 0:
                self.setCursor(QtCore.Qt.WaitCursor)
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Question)
                if self.chkDelete.isChecked() is True:
                    msgText = str(itemCount) + ' files will permanently deleted.\n\n"'
                if self.chkDeleteXMP.isChecked() is True:
                    msgText = msgText + str(itemCount) + ' XMP files will permanently deleted.\n\n"'
                msgText = msgText + "Continue?"
                msg.setText(msgText)
                msg.setWindowTitle("Delete Files")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msg = self.FormatMessageBox(msg)
                result = msg.exec_()

                if result == QtWidgets.QMessageBox.Ok:

                    if self.chkDeleteXMP.isChecked() is True:
                        selRows = self.GetAffectedRows("delete")
                        selRows = sorted(selRows, key=int, reverse=True)
                        for r in selRows:
                            p = self.db.getPhoto(r)
                            if isfile(p["filename"] + ".xmp") is True:
                                os.remove(p["filename"] + ".xmp")                        
                    
                    if self.chkDelete.isChecked() is True:
                        selRows = self.GetAffectedRows("delete")
                        selRows = sorted(selRows, key=int, reverse=True)
                        for r in selRows:
                            p = self.db.getPhoto(r)
                            if isfile(p["filename"]) is True:
                                os.remove(p["filename"])
                            self.lstPhotos.takeItem(r)
                            self.db.deleteRow(r)
                            
                self.setCursor(QtCore.Qt.ArrowCursor)

    def DisplayBigPhoto(self):
        #routine to display the currently selected photo in lstPhotos as the big image
        #first, hide the previously displayed image
        #if a photo is selected, convert it to QPixmap format so we can display it in the QLabel object
        #get a list of all selected photos, choose the one closest to the top, and assign its image to big display
        #display the QLabel object with the newly assigned image
        #get a list of all selected photos, choose the one closest to the top, and assign its image to big display
        if self.GetAffectedRowsCount("selected") > 0:
            pm = QtGui.QPixmap()
            selItems = self.lstPhotos.selectedItems()
            pm = selItems[0].icon().pixmap(selItems[0].icon().availableSizes()[0])
            lblBigPhotoHeight = self.lblBigPhoto.frameGeometry().height()
            lblBigPhotoWidth = self.lblBigPhoto.frameGeometry().width()
            
            if pm.height() > pm.width():
                pm = pm.scaledToHeight(lblBigPhotoHeight)
            else:
                pm = pm.scaledToWidth(lblBigPhotoWidth)
            
            self.lblBigPhoto.setPixmap(pm)
            self.lblBigPhoto.show()

    def DisplayEXIFData(self):
        #set text in display to default: Null.  Use "N" for displays that are too small for the whole word.
        #include the < characters to clarify for the user that this is truly a null value
        #also, later routines will check for the presence of the < character and will not write to EXIF
        #if the < character is present
        self.txtCameraMake.setText("<Null>")
        self.txtCameraModel.setText("<Null>")
        self.txtImageDescription.setText("<Null>")
        self.txtUserComment.setText("<Null>")
        self.txtLensMake.setText("<Null>")
        self.txtLensModel.setText("<Null>")        
        self.txtArtist.setText("<Null>")        
        self.txtCopyright.setText("<Null>")        
        self.txtYear.setText("<Null>")
        self.txtMonth.setText("<N>")
        self.txtDay.setText("<N>")
        self.txtHour.setText("<Null>")
        self.txtMinute.setText("<N>")
        self.txtSecond.setText("<N>")
        #make sure there is data to work with...
        if self.GetAffectedRowsCount("chosen") > 0:
            #as a safety precaution, reset all checkboxes so the user won't accidentally insert data.
            #the user will have to check the checkbox manually before future EXIF data would be inserted into files
            self.chkCameraMake.setChecked(False)
            self.chkCameraModel.setChecked(False)
            self.chkImageDescription.setChecked(False)
            self.chkUserComment.setChecked(False)
            self.chkLensMake.setChecked(False)
            self.chkLensModel.setChecked(False)
            self.chkArtist.setChecked(False)
            self.chkCopyright.setChecked(False)
            self.chkOriginalDate.setChecked(False)
            self.chkOriginalTime.setChecked(False)
            self.chkShiftDate.setChecked(False)
            self.chkEmbedThumbnail.setChecked(False)
            self.btnChangeExif.setEnabled(False)
            self.btnChangeDate.setEnabled(False)
            #reset all our variables to get started
            #variables starting with "exif" will collect data that is common to all selected files
            #variables starting with "blank" are flags to be triggered if one or more files have blank data
            #variables starting with "varying" are flags to be triggered if data in selected files differ
            exifMake = exifModel = exifImageDescription = exifLensMake = exifLensModel = exifUserComment = exifArtist = exifCopyright = ""
            exifYear = exifMonth = exifDay = exifHour = exifMinute = exifSecond = ""
            blankMakeExists = blankModelExists = blankImageDescriptionExists = blankDateExists = blankLensMakeExists = blankLensModelExists = blankUserCommentExists = blankArtistExists = blankCopyrightExists = False
            varyingMakes = varyingModels = varyingImageDescriptions = varyingLensMakes = varyingLensModels = varyingUserComments = varyingArtists = varyingCopyrights = False
            varyingExifYears = varyingExifMonths = varyingExifDays = varyingExifHours = varyingExifMinutes = varyingExifSeconds = False
            #set flag to tell loop below whether we are processing the first file in selection
            isFirstEntry = True
            #create selRows list to hold indexes of selected items
            selRows = self.GetAffectedRows("chosen")
            #variables starting with "this" hold data unique to each looped file in selection
            for r in selRows:
                thisExifMake = thisExifModel = thisExifImageDescription = thisExifDate = thisExifLensMake = thisExifLensModel = thisExifUserComment = thisExifArtist = thisExifCopyright = ""
                thisExifYear = thisExifMonth = thisExifDay = thisExifHour = thisExifMinute = thisExifSecond = ""
                #fname is the full file name for the selected list item to be processed.
                #the filename takes its path from the displayed lblPath. It takes the filename from the text in lstPhotos
#                fname = self.thisPath + self.lstPhotos.item(thisItem).text()
                #try to get EXIF data from the selected image. Only JPEG and TIFF files will return data.
                #skil the variable assignments if EXIF is not retrieved.
                #if EXIF data is gotten, try to assign each variable. Some photos won't have all the variables.
                p = self.db.getPhoto(r)
                if "exif" in p:
                    exif_dict = p["exif"]
                    try:
                        thisExifMake = exif_dict["0th"][piexif.ImageIFD.Make].decode("utf-8")
                    except:
                        thisExifMake = ""
                    try:
                        thisExifModel = exif_dict["0th"][piexif.ImageIFD.Model].decode("utf-8")
                    except:
                        thisExifModel = ""
                    try:
                        thisExifImageDescription = exif_dict["0th"][piexif.ImageIFD.ImageDescription].decode("utf-8")
                    except:
                        thisExifImageDescription = ""
                    try:
                        thisExifLensMake = exif_dict["Exif"][piexif.ExifIFD.LensMake].decode("utf-8")
                    except:
                        thisExifLensMake = ""
                    try:
                        thisExifLensModel = exif_dict["Exif"][piexif.ExifIFD.LensModel].decode("utf-8")
                    except:
                        thisExifLensModel = ""
                    try:
                        thisExifUserComment = exif_dict["Exif"][piexif.ExifIFD.UserComment].decode("utf-8")
                    except:
                        thisExifUserComment = ""
                    try:
                        thisExifArtist = exif_dict["0th"][piexif.ImageIFD.Artist].decode("utf-8")
                    except:
                        thisExifArtist = ""
                    try:
                        thisExifCopyright = exif_dict["0th"][piexif.ImageIFD.Copyright].decode("utf-8")
                    except:
                        thisExifCopyright = ""
                    try:
                        thisExifDate = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode("utf-8")
                    except:
                        thisExifDate = ""
                   
                    
                #set flags if variables are blank
                if thisExifMake == "": blankMakeExists = True
                if thisExifModel == "": blankModelExists = True
                if thisExifImageDescription == "": blankImageDescriptionExists = True
                if thisExifLensMake == "": blankLensMakeExists = True
                if thisExifLensModel == "": blankLensModelExists = True
                if thisExifUserComment== "": blankUserCommentExists = True
                if thisExifArtist == "": blankArtistExists = True
                if thisExifCopyright== "": blankCopyrightExists = True
                if thisExifDate == "": blankDateExists = True
                else:
                    #parse EXIF data for date/time components
                    thisExifYear = thisExifDate[0:4]
                    thisExifMonth = thisExifDate[5:7]
                    thisExifDay = thisExifDate[8:10]
                    thisExifHour = thisExifDate[11:13]
                    thisExifMinute = thisExifDate[14:16]
                    thisExifSecond = thisExifDate[17:19]
                    
                #if this is the first file in the selection, set the whole selection's variables to this equal those
                #of this first file. Later, we'll compare each file's data against these exif variables to see
                #if data varies between files
                if isFirstEntry == True:
                    exifMake = thisExifMake
                    exifModel = thisExifModel
                    exifImageDescription = thisExifImageDescription
                    exifLensMake= thisExifLensMake
                    exifLensModel = thisExifLensModel
                    exifUserComment= thisExifUserComment
                    exifArtist= thisExifArtist
                    exifCopyright = thisExifCopyright
                    exifYear = thisExifYear
                    exifMonth = thisExifMonth
                    exifDay = thisExifDay
                    exifHour = thisExifHour
                    exifMinute = thisExifMinute
                    exifSecond = thisExifSecond
                    #now that we've processed the first file, set the isFirstEntry to False
                    isFirstEntry = False
                    
                else:
                    #check to see if this file's data varies from the others in the selection so far
                    if exifMake != thisExifMake: varyingMakes = True
                    if exifModel != thisExifModel: varyingModels = True
                    if exifImageDescription != thisExifImageDescription: varyingImageDescriptions = True
                    if exifLensMake != thisExifLensMake: varyingLensMakes= True
                    if exifLensModel != thisExifLensModel: varyingLensModels = True
                    if exifUserComment != thisExifUserComment: varyingUserComments = True
                    if exifArtist != thisExifArtist: varyingArtists = True
                    if exifCopyright != thisExifCopyright: varyingCopyrights = True
                    if exifYear != thisExifYear: varyingExifYears = True
                    if exifMonth != thisExifMonth: varyingExifMonths = True
                    if exifDay != thisExifDay: varyingExifDays = True
                    if exifHour != thisExifHour: varyingExifHours = True
                    if exifMinute != thisExifMinute: varyingExifMinutes = True
                    if exifSecond != thisExifSecond: varyingExifSeconds = True
                    
            #Now that we've looped through all selected files, set the display text boxes to the data
            #of the last files processed.  This will be overwritten if any files' data was blank or varied.
            self.txtCameraMake.setText(thisExifMake)
            self.txtCameraModel.setText(thisExifModel)
            self.txtImageDescription.setText(thisExifImageDescription)
            self.txtLensMake.setText(thisExifLensMake)
            self.txtLensModel.setText(thisExifLensModel)
            self.txtUserComment.setText(thisExifUserComment)
            self.txtArtist.setText(thisExifArtist)
            self.txtCopyright.setText(thisExifCopyright)
            self.txtYear.setText(thisExifYear)
            self.txtMonth.setText(thisExifMonth)
            self.txtDay.setText(thisExifDay)
            self.txtHour.setText(thisExifHour)
            self.txtMinute.setText(thisExifMinute)
            self.txtSecond.setText(thisExifSecond)
            
            #overwrite the displayed data if any selected files had blank or varying data
            if varyingMakes == True: self.txtCameraMake.setText("<Values vary>")
            if blankMakeExists == True: self.txtCameraMake.setText("<Some are null>")
            if varyingModels == True: self.txtCameraModel.setText("<Values vary>")
            if blankModelExists == True: self.txtCameraModel.setText("<Some are null>")
            if varyingImageDescriptions == True: self.txtImageDescription.setText("<Values vary>")
            if blankImageDescriptionExists == True: self.txtImageDescription.setText("<Some are null>")
            if varyingLensMakes == True: self.txtLensMake.setText("<Values vary>")
            if blankLensMakeExists == True: self.txtLensMake.setText("<Some are null>")
            if varyingLensModels == True: self.txtLensModel.setText("<Values vary>")
            if blankLensModelExists == True: self.txtLensModel.setText("<Some are null>")
            if varyingUserComments == True: self.txtUserComment.setText("<Values vary>")
            if blankUserCommentExists == True: self.txtUserComment.setText("<Some are null>")
            if varyingArtists == True: self.txtArtist.setText("<Values vary>")
            if blankArtistExists == True: self.txtArtist.setText("<Some are null>")
            if varyingCopyrights == True: self.txtCopyright.setText("<Values vary>")
            if blankCopyrightExists== True: self.txtCopyright.setText("<Some are null>")
            if varyingExifYears == True: self.txtYear.setText("<Vary>")
            if varyingExifMonths == True: self.txtMonth.setText("<V>")
            if varyingExifDays == True: self.txtDay.setText("<V>")
            if varyingExifHours == True: self.txtHour.setText("<Vary>")
            if varyingExifMinutes == True: self.txtMinute.setText("<V>")
            if varyingExifSeconds == True: self.txtSecond.setText("<V>")
            if blankDateExists == True:
                self.txtYear.setText("<Null>")
                self.txtMonth.setText("<N>")
                self.txtDay.setText("<N>")
                self.txtHour.setText("<Null>")
                self.txtMinute.setText("<N>")
                self.txtSecond.setText("<N>")
            for c in self.tabExifData.children():
                if "txt" in c.objectName(): c.setCursorPosition(0)

    def DisplayNewFilename(self):
        #routine to create the new filename for the selected photo in list.
        #this routine itself does not rename the file. It only creates the hypothetical file name.
        #first, clear the displayed sample file name
        #create the new file name, using the user's specifications
        #only proceed if lstPhotos isn't empty
        #if current row is selected, display its sample file name
        #display just the basename of the file, not its entire path
        #if the clicked file isn't selected, use the topmost selected file instead
        #display just the basename of the file, not its entire path
        self.lblSampleNewFilename.setText("")
        if self.GetAffectedRowsCount("selected") > 0:
            if self.lstPhotos.item(self.lstPhotos.currentRow()).isSelected() == True:
                newName = self.GetNewFilename(int(self.lstPhotos.currentRow()))
            else:
                selRows = self.GetAffectedRows("selected")
                newName = self.GetNewFilename(int(selRows[0]))
            self.lblSampleNewFilename.setText(basename(newName))
            self.lblSampleNewFilename.show()


    def eventFilter(self, sourceObj, event):

        #routine to handle events on objects, like clicks, lost focus, gained forcus, etc.
        objName = str(sourceObj.objectName())
        
        if event.type() == QtCore.QEvent.Resize:
            if objName == "MainWindow":
                self.ResizeWindow(sourceObj)

        if event.type() == QtCore.QEvent.KeyRelease:
            #if the clicked text box is one that expects only digits, remove any non-digit characters typed in.
            if sourceObj is not None:
                key = event.key()
                if sourceObj.parent() is  not None:
                    if sourceObj.parent().objectName() == "tabDate" and objName != "timeOriginalDate":
                        if key not in (QtCore.Qt.Key_Right,  QtCore.Qt.Key_Left, QtCore.Qt.Key_End,  QtCore.Qt.Key_Home):
                            sourceObj.setText(re.sub("\D", "", str(sourceObj.text())))
                            #if the clicked text box has limits on its number, force the user to use the correct number (e.g., 1-12 for a month value)
                            if "txt" in objName:
                                if sourceObj.text() != "":
                                    if objName in ("txtYear",  "txtShiftYear"):
                                        if len(sourceObj.text()) > 4:
                                            sourceObj.setText(sourceObj.text()[0:4])
                                    if objName in ("txtMonth",  "txtShiftMonth"):
                                        if int(sourceObj.text()) > 12:
                                            sourceObj.setText("12")
                                    if objName in ("txtDay"):
                                        if int(sourceObj.text()) > 31:
                                            sourceObj.setText("31")
                                    if objName in ("txtShiftDay") and "YMDhms" in self.cboTimeShift.currentText():
                                        if int(sourceObj.text()) > 31:
                                            sourceObj.setText("31")
                                    if objName in ("txtHour",  "txtShiftHour"):
                                        if int(sourceObj.text()) > 23:
                                            sourceObj.setText("23")
                                    if objName in ("txtMinute", "txtSecond",  "txtShiftMinute",  "txtShiftSecond"):
                                        if int(sourceObj.text()) > 59:
                                            sourceObj.setText("59")

                    if sourceObj.parent().objectName() == "tabRename":
                        if key not in (QtCore.Qt.Key_Right,  QtCore.Qt.Key_Left, QtCore.Qt.Key_End,  QtCore.Qt.Key_Home):
                            for c in sourceObj.children():
                                if "txt" in objName: #prevent user from entering invalid slash or backslash characters
                                    if event.key() == QtCore.Qt.Key_Slash or event.key() == QtCore.Qt.Key_Backslash:
                                        sourceObj.setText(sourceObj.text()[0:len(sourceObj.text())-1])
                                    self.DisplayNewFilename()
                
                if objName == "lstPhotos":   #handle navigation keys for lstPhotos.  the ListPhotosClicked needs to be called for each of the following key presses
                    if key in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_A, QtCore.Qt.Key_End, QtCore.Qt.Key_Home, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown):
                        self.ListPhotosClicked()

        #need to check if date/time text boxes have < character, indicating null, varying, or blank, so they need to be set to blank so
        #the non-digit characters are not written to the time/date string in the EXIF data
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if "txt" in objName:
                if "<" in sourceObj.text():
                    sourceObj.setText("")
                    
        if event.type() == QtCore.QEvent.FocusOut:
            if objName == "txtStartNumber":
                self.txtStartNumber.setText(re.sub("\D", "", str(self.txtStartNumber.text())))
                if self.txtStartNumber.text() == "": self.txtStartNumber.setText("0")
        
        if event.type() == QtCore.QEvent.ChildRemoved:
            if objName == "lstPhotos":
                basenames = [str(self.lstPhotos.item(i).text()) for i in range(self.lstPhotos.count())]
                self.db.adjustOrder(basenames)
                self.DisplayEXIFData()
    
        #this is the default return. GUI needs it to run properly without throwing errors
        return QtWidgets.QWidget.eventFilter(self, sourceObj, event)


    def ExifCheckboxClicked(self):
        #this routine enables the Change Exif button if an any checkbox  on tabEIFData is clicked on
        #start by setting flag to false.  It will be set to true only if a checkbox is found to be checked
        self.btnChangeExif.setEnabled(False)
        #loop thorugh all objects on the tab, and check if a checkbox is set to true
        for c in self.tabExifData.children():
            if "chk" in c.objectName():
                if c.isChecked(): self.btnChangeExif.setEnabled(True)


    def ExitApp(self):
        sys.exit()
        

    def FormatMessageBox(self,msg):
        #apply the stylesheet created when the main window is instantiated (above) to a dialog box
        #this lets us have one stylesheet to edit in one place, rather than specifying style elements in every routine that
        #creates a diaglog box
        msg.setStyleSheet(self.thisDialogStylesheet)
        return msg


    def GetAffectedRows(self,  mode):
        #routine to return the rows selected or all rows
        #rows can be manually selected, or all rows can be selected using the cboNumbers combobox
        #if rows are selected individually in lstPhotos, cycle through them and add them to the list
        #if all rows are selected, cycle through them and add them to the list
        #unfortunately, there doesn't seem to be a rows() property to do this without looping through the list.
        #sort the list because sometimes Python doesn't do it automatically
        #return the sorted list of row integers
        selRows = []
        if mode == "chosen" and self.cboRenameFiles.currentText() == "All files":
            for r in range(self.lstPhotos.count()):
                selRows.append(r)
        else:
            for i in self.lstPhotos.selectedIndexes():
                selRows.append(int(i.row()))
        selRows.sort()
        return selRows


    def GetAffectedRowsCount(self,  mode):
        return len(self.GetAffectedRows(mode))


    def GetFormattedNumber(self, thisRow):
        specifiedStartNumber = str(self.txtStartNumber.text())
        specifiedStartNumber = re.sub("\D", "", specifiedStartNumber)
        specifiedLeadingZeros = re.search('(?!0)', specifiedStartNumber).start()
        if specifiedStartNumber == "":
            specifiedStartNumber = "0"
        photoNumberStartInt = int(specifiedStartNumber)
        if "Specify" not in self.cboNumbers.currentText():
            specifiedLeadingZeros = 0
        if  "No number" in self.cboNumbers.currentText(): #No numbers
            return ""
        if "From 1" in self.cboNumbers.currentText(): #Number from 1 (continues these steps to add padding)
            if self.cboRenameFiles.currentText() == "All files":
                thisPhotoNumber = thisRow + 1
            if self.cboRenameFiles.currentText() == "Selected only":
                thisPhotoCount = 0
                for i in self.GetAffectedRows("chosen"):
                    if int(i) == thisRow:
                        thisPhotoNumber = thisPhotoCount + 1
                        break
                    thisPhotoCount += 1
            thisPhotoNumberString = str(thisPhotoNumber)
            if "pad" not in self.cboNumbers.currentText():
                return thisPhotoNumberString
        if "Specify" in self.cboNumbers.currentText(): #Number from Specified (continues these steps to add padding)
                if self.cboRenameFiles.currentText() == "All files":
                    thisPhotoNumber = thisRow + photoNumberStartInt
                if self.cboRenameFiles.currentText() == "Selected only":
                    thisPhotoCount = 0
                    for i in self.GetAffectedRows("chosen"):
                        if int(i) == thisRow:
                            thisPhotoNumber = thisPhotoCount + photoNumberStartInt
                            break
                        thisPhotoCount += 1
                thisPhotoNumberString = str(thisPhotoNumber)
                if specifiedLeadingZeros > 0:
                    zerosToPad = len(re.sub("\D", "", self.txtStartNumber.text())) - len(thisPhotoNumberString)
                    thisPhotoNumberString = ("0" * zerosToPad) + thisPhotoNumberString
                if "pad" not in self.cboNumbers.currentText():
                    return thisPhotoNumberString
        if "pad" in self.cboNumbers.currentText(): #add padding zeros
            imageCountMaxString = str(self.GetAffectedRowsCount("chosen") + photoNumberStartInt -1)
            zerosToPad = len(imageCountMaxString) - len(thisPhotoNumberString) + specifiedLeadingZeros
            thisPhotoNumberString = ("0" * zerosToPad) + thisPhotoNumberString
        return thisPhotoNumberString


    def GetNewFilename(self, r):
        p = self.db.getPhoto(r)
        oldName = p["filename"]
        newName = p["path"] + "/"
        existingBasename = p["basename"]
        suffix = p["suffix"]
        thisPhotoNumberString = self.GetFormattedNumber(r)
        specifiedBase = re.sub('[\\\/]', '',  self.txtFilename.text())
        if self.cboDateOptions.currentText() == "No date":
            OriginalDate = ""
        else:
            OriginalDate = str(self.GetFormattedOriginalDate(oldName))
        if "Use existing suffix" not in self.cboSuffix.currentText():
            if "Upper case" in self.cboSuffix.currentText():
                suffix = suffix.upper()
            if "Lower case" in self.cboSuffix.currentText():
                suffix = suffix.lower()
            if "Custom" in self.cboSuffix.currentText():
                suffix = "." + self.txtSuffix.text()
        if self.cboNumbers.currentText() != "No number": #User has chosen to number files
            if self.cboFilenameBase.currentText() == "Use existing file name" and self.cboNumberPosition.currentText() == "Number at start":
                newName = newName + thisPhotoNumberString + "-"
                if OriginalDate != "":
                    newName = newName + OriginalDate + "-"
                newName = newName + existingBasename + suffix
            if self.cboFilenameBase.currentText() == "Use existing file name" and self.cboNumberPosition.currentText() == "Number at end":
                newName = newName + existingBasename
                newName = newName + "-" + thisPhotoNumberString
                if OriginalDate != "":
                    newName = newName + "-" + OriginalDate
                newName = newName + suffix
            if self.cboFilenameBase.currentText() == "Specify base name" and self.cboNumberPosition.currentText() == "Number at start":
                newName = newName + thisPhotoNumberString
                if OriginalDate != "":
                    newName = newName + "-" + OriginalDate
                if specifiedBase != "":
                    newName = newName + "-"
                newName = newName + specifiedBase
                newName = newName + suffix
            if self.cboFilenameBase.currentText() == "Specify base name" and self.cboNumberPosition.currentText() == "Number at end":
                newName = newName + specifiedBase
                if specifiedBase != "":
                    newName = newName + "-"
                newName = newName + thisPhotoNumberString
                if OriginalDate != "":
                    newName = newName + "-" + OriginalDate
                newName = newName + suffix
        if self.cboNumbers.currentText() == "No number": #User has chosen NOT to number files
            if self.cboFilenameBase.currentText() == "Use existing file name" and self.cboNumberPosition.currentText() == "Number at start":
                if OriginalDate != "":
                    newName = newName + OriginalDate + "-"
                newName = newName + existingBasename + suffix
            if self.cboFilenameBase.currentText() == "Use existing file name" and self.cboNumberPosition.currentText() == "Number at end":
                newName = newName + existingBasename
                if OriginalDate != "":
                    newName = newName + "-" + OriginalDate
                newName = newName + suffix
            if self.cboFilenameBase.currentText() == "Specify base name" and self.cboNumberPosition.currentText() == "Number at start":
                if OriginalDate != "":
                    newName = newName + OriginalDate
                if specifiedBase != "" and OriginalDate != "":
                    newName = newName + "-"
                newName = newName + specifiedBase
                newName = newName + suffix
            if self.cboFilenameBase.currentText() == "Specify base name" and self.cboNumberPosition.currentText() == "Number at end":
                newName = newName + specifiedBase
                if OriginalDate != "":
                    newName = newName + "-" + OriginalDate
                newName = newName + suffix
        return newName


    def GetFormattedOriginalDate(self, path):
        try:
            exif_dict = piexif.load(path)
        except Exception:
            pass
        try:
            thisExifDate = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()
            thisExifDate = thisExifDate.replace(":","")
            thisExifDate = thisExifDate.replace(" ","")
            #format date per user setting in cboDateOptions. No need to format for YYYYMMDDHHMMSS option
            #because thisExifDate is already in that format by default
            if self.cboDateOptions.currentText() == "YMD_hms":
                thisExifDate = thisExifDate[0:8] + "_" + thisExifDate[8:]
            if self.cboDateOptions.currentText() == "Y-M-D_hms":
                thisExifDate = thisExifDate[0:4] + "-" + thisExifDate[4:6] + "-" + thisExifDate[6:8]  + "_" + thisExifDate[8:]
            if self.cboDateOptions.currentText() == "Y-M-D_h-m-s":
                thisExifDate = thisExifDate[0:4] + "-" + thisExifDate[4:6] + "-" + thisExifDate[6:8]  + "_" + thisExifDate[8:10] + "-" + thisExifDate[10:12] + "-" + thisExifDate[12:]
            if self.cboDateOptions.currentText() == "Custom":
                Y = thisExifDate[0:4]
                M = thisExifDate[4:6]
                D = thisExifDate[6:8]
                h = thisExifDate[8:10]
                m = thisExifDate[10:12]
                s = thisExifDate[12:]
                thisPattern = self.txtDatePattern.text()
                thisPattern= re.sub('[^YMDhms`\-\=\!\@\#\$\%\^\&\*\(\)\_\+\[\]\\{\}\:\'\"\;\.\,\?\<\>\~]', '', thisPattern) #remove all non-meaningful letters from pattern
                if "Y" in thisPattern:  thisPattern = thisPattern.replace("Y", Y)
                if "M" in thisPattern: thisPattern = thisPattern.replace("M",  M)
                if "D" in thisPattern: thisPattern = thisPattern.replace("D",  D)
                if "h" in thisPattern: thisPattern = thisPattern.replace("h",  h)
                if "m" in thisPattern: thisPattern = thisPattern.replace("m",  m)
                if "s" in thisPattern: thisPattern = thisPattern.replace("s",  s)
                thisExifDate = thisPattern
            return thisExifDate
        except Exception:
            return ""


    def GetPixmapForThumbnail(self, p,  r):
        if "exif" in p:
            exif_dict  = p["exif"]
            try:
                pmOrientation = int(exif_dict["0th"][piexif.ImageIFD.Orientation] )
            except:
                pmOrientation = 1
            try:
                thumbimg = exif_dict["thumbnail"]
            except:
                thumbimg = None
        else:
            thumbimg = None

        if thumbimg is None:
            qimage = QtGui.QImage(p["filename"])
        else:
            qimage = QtGui.QImage()
            qimage.loadFromData(thumbimg, format='JPG')
        if pmOrientation == 2: qimage = qimage.mirrored(True,  False)
        if pmOrientation == 3: qimage = qimage.transformed(QtGui.QTransform().rotate(180))
        if pmOrientation == 4: qimage = qimage.mirrored(False,  True)
        if pmOrientation == 5: 
            qimage = qimage.mirrored(True,  False)
            qimage = qimage.transformed(QtGui.QTransform().rotate(270))
        if pmOrientation == 6: qimage = qimage.transformed(QtGui.QTransform().rotate(90))
        if pmOrientation == 7:          
            qimage = qimage.mirrored(True,  False)
            qimage = qimage.transformed(QtGui.QTransform().rotate(90))
        if pmOrientation == 8: qimage = qimage.transformed(QtGui.QTransform().rotate(270))
        
        pm = QtGui.QPixmap()
        pm.convertFromImage(qimage)
            
        if pm.height() > pm.width():
            pm = pm.scaledToHeight(281)
        else:
            pm = pm.scaledToWidth(500)
        return pm


    def ListPhotosClicked(self):
            self.DisplayNewFilename()
            self.DisplayBigPhoto()
            self.DisplayEXIFData()


    def CheckDeleteChanged(self):
        if self.chkDelete.isChecked() is True or self.chkDeleteXMP.isChecked() is True:
            self.btnDelete.setEnabled(True)
        else:
            self.btnChangeDate.setEnabled(False)


    def CheckOriginalDateChanged(self):
        if self.chkOriginalDate.isChecked() is True:
            self.chkShiftDate.setChecked(False)
        self.btnChangeDate.setEnabled(False)
        for c in self.tabDate.children():
            if "chk" in c.objectName():
                if c.isChecked(): self.btnChangeDate.setEnabled(True)


    def CheckOriginalTimeChanged(self):
        if self.chkOriginalTime.isChecked() is True:
            self.chkShiftDate.setChecked(False)
        self.btnChangeDate.setEnabled(False)
        for c in self.tabDate.children():
            if "chk" in c.objectName():
                if c.isChecked(): self.btnChangeDate.setEnabled(True)


    def CheckShiftDateChanged(self):
        if self.chkShiftDate.isChecked() is True:
            self.chkOriginalDate.setChecked(False)
            self.chkOriginalTime.setChecked(False)
        self.btnChangeDate.setEnabled(False)
        for c in self.tabDate.children():
            if "chk" in c.objectName():
                if c.isChecked(): self.btnChangeDate.setEnabled(True)


    def ChooseFiles(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog            
        
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Choose Image files",
            "",
            "JPEG Images (*.jpg *.jpeg);;TIFF Images (*.tif *.tiff);;Bitmap Images (*.bmp);;All Supported Images (*.jpg *.jpeg *.bmp *.gif *.mng *.png *.pbm *.pgm *.ppm *.tif *.tiff *.xbm *.xpm *.svg *.tga )",
            options = options
            )            
        
        if files:

            self.setCursor(QtCore.Qt.WaitCursor)

            self.lblBigPhoto.hide()
            self.lblProgressBar.setText("Reading photo data...")
            self.lblProgressBar.show()
            self.progressBar.setValue(0)
            self.progressBar.show()
            
            self.db.clearDb()
            self.db.createDb(files)

            self.setCursor(QtCore.Qt.ArrowCursor)
            self.progressBar.hide()
            self.lblProgressBar.hide()

            self.LoadPhotoList(self.db.getAllPhotos())


    def LoadPhotoList(self, photos):
        self.setCursor(QtCore.Qt.WaitCursor)
        self.lstPhotos.clear()
        self.lblBigPhoto.hide()
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.lblProgressBar.setText("Loading photos into list...")
        self.lblProgressBar.show()
        totalFiles = len(photos)
        r = 0
        for p in photos:
            itm = QtWidgets.QListWidgetItem(p["basename"] + p["suffix"])
            pm = self.GetPixmapForThumbnail(p,  r)
            itm.setIcon(QtGui.QIcon(pm))
            self.lstPhotos.addItem(itm)
            self.lstPhotos.repaint()
            r += 1
            self.progressBar.setValue(int(100*r/totalFiles))
            QtWidgets.qApp.processEvents()
        self.lblPath.setText(photos[0]["path"])
        self.thisPath = photos[0]["path"] +"/"
        self.lstPhotos.setCurrentRow(0)
        self.DisplayNewFilename()
        self.DisplayEXIFData()
        self.progressBar.hide()
        self.lblProgressBar.hide()
        self.DisplayBigPhoto()
        self.setCursor(QtCore.Qt.ArrowCursor)


    def RenameFiles(self):
        if self.GetAffectedRowsCount("chosen") > 0:
            self.setCursor(QtCore.Qt.WaitCursor)
            if self.CheckIfRenamingWouldOverwriteFiles() == True:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("The current renaming settings would overwrite one or more files.\n(One or more files with the new names already exist.)\n\nPlease change the renaming settings.\n")
                msg.setWindowTitle("Overwrite Warning")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg = self.FormatMessageBox(msg)
                msg.exec_()
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Question)
                if self.cboRenameFiles.currentText() == "All files": numberOfFiles = self.lstPhotos.count()
                if self.cboRenameFiles.currentText() == "Selected only": numberOfFiles = self.GetAffectedRowsCount("chosen")
                msgText = str(numberOfFiles) + ' files will safely be renamed, in the style of \n\n"'
                msgText = msgText + str(self.lblSampleNewFilename.text()) + "\n"
                msg.setText(msgText)
                msg.setWindowTitle("Safe to Rename")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msg = self.FormatMessageBox(msg)
                result = msg.exec_()
                if result == QtWidgets.QMessageBox.Ok:
                    for r in self.GetAffectedRows("chosen"):
                        p = self.db.getPhoto(r)
                        oldName = p["filename"]
                        newName = self.GetNewFilename(r)
                        if isfile(oldName) and not isfile(newName):
                            os.rename(oldName, newName)
                            print(oldName + " -> " + newName)
                            self.lstPhotos.item(r).setText(basename(newName))
                            if self.chkSidecars.isChecked() and isfile(oldName + ".xmp"):
                                os.rename(oldName + ".xmp", newName + ".xmp")
                            self.db.updateName(r,  newName)
            self.setCursor(QtCore.Qt.ArrowCursor)


    def ResizeWindow(self,  mainWindow):
        mainWindowWidth = mainWindow.frameGeometry().width()
        mainWindowHeight = mainWindow.frameGeometry().height()
        tabOptionsY = 70 + int(.94*(mainWindowHeight -70)) - 561
        lblBigPhotoWidth = 500*(tabOptionsY -70)/281
        lblBigPhotoHeight = tabOptionsY -80
        
        if lblBigPhotoWidth > mainWindowWidth/2:
            lblBigPhotoWidth = int(mainWindowWidth/2)
        
        if lblBigPhotoWidth > 440:
            lblBigPhotoX = mainWindowWidth - lblBigPhotoWidth -10 
            tabOptionsX = mainWindowWidth - lblBigPhotoWidth -10 + int((lblBigPhotoWidth - 440)/2)
            lstPhotosWidth = mainWindowWidth - lblBigPhotoWidth - 40
        else:
            tabOptionsX = mainWindowWidth - 493
            lblBigPhotoX = tabOptionsX - int((lblBigPhotoWidth - 440)/2)
            lstPhotosWidth = mainWindowWidth - 523

        self.tabOptions.setGeometry(QtCore.QRect(tabOptionsX, tabOptionsY,  440,  561))  
        self.lblBigPhoto.setGeometry(QtCore.QRect(lblBigPhotoX, 70,  lblBigPhotoWidth, lblBigPhotoHeight))
        self.progressBar.setGeometry(QtCore.QRect(lblBigPhotoX, 185,  lblBigPhotoWidth, 51))
        self.DisplayBigPhoto()
        self.lblProgressBar.setGeometry(QtCore.QRect(lblBigPhotoX, 250,  441,  23))
        self.lstPhotos.setGeometry(QtCore.QRect(20 , 70,  lstPhotosWidth,   int(.94*(mainWindowHeight -70))))
        self.lstPhotos.setIconSize(QtCore.QSize(int(100*mainWindowWidth/1183),  int(100*mainWindowHeight/980)))
        
        lstPhotosFont = QtGui.QFont()
        lstPhotosFont.setPointSize(int(14*mainWindowHeight/1183))
        self.lstPhotos.setFont(lstPhotosFont)
    
        
    def RotateImages(self):        
        if self.lstPhotos.count() > 0 and ("No" not in self.cboRotate.currentText() or "No" not in self.cboMirror.currentText()):
            msgtext = 'Image orientation for ' + str(self.GetAffectedRowsCount("chosen")) + ' files will be changed.'
            msgtext = msgtext + "\n\nThis operation only affects .jpg and .jpeg files.\n"
            msg = QtWidgets.QMessageBox()
            msg.setText(msgtext)
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setWindowTitle("Editing Image Orientation")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg = self.FormatMessageBox(msg)
            result = msg.exec_()

            if result == QtGui.QMessageBox.Ok:
                self.lblBigPhoto.hide()
                self.lblProgressBar.setText("Writing original date/time to files...")
                self.lblProgressBar.show()
                self.progressBar.setValue(0)
                self.progressBar.show()
                
                count = 0
                totalFiles = self.GetAffectedRowsCount("chosen")
                selRows = self.GetAffectedRows("chosen")
                for r in selRows:
                    p = self.db.getPhoto(r)
                    if p["suffix"] in (".jpg", ".JPG", ".jpeg", ".JPEG"):
                        exif_dict = p["exif"] #exif_dict = piexif.load(p["filename"]) 
                        if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                            thisRotation = int(exif_dict["0th"][piexif.ImageIFD.Orientation] )
                        else:
                            thisRotation = 1
                        if "90" in self.cboRotate.currentText():
                            if thisRotation == 1: thisRotation = 6
                            elif thisRotation == 2: thisRotation = 7
                            elif thisRotation == 3: thisRotation = 8
                            elif thisRotation == 4: thisRotation = 5
                            elif thisRotation == 5: thisRotation = 2
                            elif thisRotation == 6: thisRotation = 3
                            elif thisRotation == 7: thisRotation = 4
                            elif thisRotation == 8: thisRotation = 1

                        if "180" in self.cboRotate.currentText():
                            if thisRotation == 1: thisRotation = 3
                            elif thisRotation == 2: thisRotation = 4
                            elif thisRotation == 3: thisRotation = 1
                            elif thisRotation == 4: thisRotation = 2
                            elif thisRotation == 5: thisRotation = 7
                            elif thisRotation == 6: thisRotation = 8
                            elif thisRotation == 7: thisRotation = 5
                            elif thisRotation == 8: thisRotation = 6

                        if "270" in self.cboRotate.currentText():
                            if thisRotation == 1: thisRotation = 8
                            elif thisRotation == 2: thisRotation = 5
                            elif thisRotation == 3: thisRotation = 6
                            elif thisRotation == 4: thisRotation = 7
                            elif thisRotation == 5: thisRotation = 4
                            elif thisRotation == 6: thisRotation = 1
                            elif thisRotation == 7: thisRotation = 2
                            elif thisRotation == 8: thisRotation = 3

                        if "Horizontal" in self.cboMirror.currentText():
                            if thisRotation == 1: thisRotation = 2
                            elif thisRotation == 2: thisRotation = 1
                            elif thisRotation == 3: thisRotation = 4
                            elif thisRotation == 4: thisRotation = 3
                            elif thisRotation == 5: thisRotation = 6
                            elif thisRotation == 6: thisRotation = 5
                            elif thisRotation == 7: thisRotation = 8
                            elif thisRotation == 8: thisRotation = 7

                        if "Vertical" in self.cboMirror.currentText():
                            if thisRotation == 1: thisRotation = 4
                            elif thisRotation == 2: thisRotation = 3
                            elif thisRotation == 3: thisRotation = 2
                            elif thisRotation == 4: thisRotation = 1
                            elif thisRotation == 5: thisRotation = 8
                            elif thisRotation == 6: thisRotation = 7
                            elif thisRotation == 7: thisRotation = 6
                            elif thisRotation == 8: thisRotation = 5
                        
                        exif_dict["0th"][piexif.ImageIFD.Orientation] = thisRotation

                        for t in (282,  283): #sanitize exif data so it's compatible with piexif expectations
                            if t in exif_dict["0th"]:
                                if type(exif_dict["0th"][t]) is not tuple:
                                    exif_dict["0th"][t] = (int(exif_dict["0th"][t]),  1)
                        if 41729 in exif_dict["Exif"]:
                            if type(exif_dict["Exif"][41729]) is not bytes:
                                if exif_dict["Exif"][41729] == 1:
                                    exif_dict["Exif"][41729]  = b'\x01'
                                    
                        exif_bytes = piexif.dump(exif_dict)
                        piexif.insert(exif_bytes, p["filename"])
                        self.db.updateExif(r, exif_dict)
                        pm = self.GetPixmapForThumbnail(p,  r)
                        self.lstPhotos.item(r).setIcon(QtGui.QIcon(pm))
                        self.progressBar.setValue(int(100*count/totalFiles))
                        count += 1
                        QtWidgets.qApp.processEvents()
                        
        self.lblProgressBar.hide()
        self.progressBar.hide()
        self.lstPhotos.repaint()
        self.DisplayBigPhoto()
        self.lblBigPhoto.show()
        self.setCursor(QtCore.Qt.ArrowCursor)


    def SanitizeDateTime(self):
        for c in self.tabDate.children():
            if "txt" in c.objectName():
                if "Year" in c.objectName():
                    while len(c.text()) < 4:
                        c.setText("0" + c.text())
                else:
                    while len(c.text()) < 2:
                        c.setText("0" + c.text())


    def setProgressBarValue(self,  value):
        self.progressBar.setValue(value)
        
        
    def SortPhotoListAlphabetically(self):
        if self.lstPhotos.count() > 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setText('Photos will be listed by creation date.\n\nPhotos without a creation date be listed at the top.\n\nThis will not rename the files.\n')
            msg.setWindowTitle("Order by Creation Date?")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg = self.FormatMessageBox(msg)
            result = msg.exec_()
            if result == QtWidgets.QMessageBox.Ok:
                self.setCursor(QtCore.Qt.WaitCursor)
                self.db.sortAlphabetically()
                self.lstPhotos.sortItems()
                self.setCursor(QtCore.Qt.ArrowCursor)


    def SortPhotoListByOriginalDate(self):
        if self.lstPhotos.count() > 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setText('Photos will be listed by creation date.\n\nPhotos without a creation date be listed at the top.\n\nThis will not rename the files.\n')
            msg.setWindowTitle("Order by Creation Date?")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg = self.FormatMessageBox(msg)
            result = msg.exec_()
            if result == QtWidgets.QMessageBox.Ok:
                self.setCursor(QtCore.Qt.WaitCursor)
                self.db.sortByOriginalDate()
                self.LoadPhotoList(self.db.getAllPhotos())
                self.setCursor(QtCore.Qt.ArrowCursor)


    def ToggleFullScreen(self):
        if self.windowState() == QtCore.Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()


    def TimeOriginalDateChanged(self):
        newDate = self.timeOriginalDate.date()
        self.txtYear.setText(str(newDate.year()))
        self.txtMonth.setText(str(newDate.month()))
        self.txtDay.setText(str(newDate.day()))
        self.txtYear.setFocus()


    def WriteExifData(self):
        self.setCursor(QtCore.Qt.WaitCursor)
        
        if self.lstPhotos.count() > 0:
            exifMake = str(self.txtCameraMake.text())
            exifModel = str(self.txtCameraModel.text())
            exifImageDescription = str(self.txtImageDescription.text())
            exifLensMake = str(self.txtLensMake.text())
            exifLensModel = str(self.txtLensModel.text())
            exifUserComment = str(self.txtUserComment.text())
            exifArtist = str(self.txtArtist.text())
            exifCopyright = str(self.txtCopyright.text())
            
            badExifData = False
            if self.chkCameraMake.isChecked() == True and "<" in exifMake:
                badExifData = True
            if self.chkCameraModel.isChecked() == True and "<" in exifModel:
                badExifData = True
            if self.chkImageDescription.isChecked() == True and "<" in exifImageDescription:
                badExifData = True
            
            if self.chkLensMake.isChecked() == True and "<" in exifLensMake:
                badExifData = True
            if self.chkLensModel.isChecked() == True and "<" in exifLensModel:
                badExifData = True
            if self.chkUserComment.isChecked() == True and "<" in exifUserComment:
                badExifData = True
            if self.chkArtist.isChecked() == True and "<" in exifArtist:
                badExifData = True
            if self.chkCopyright.isChecked() == True and "<" in exifCopyright:
                badExifData = True
           
            if badExifData == True:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setWindowTitle("Invalid EXIF entries")
                msg.setText('One or more EXIF entries are invalid. Please correct them.\n')
                msg = self.FormatMessageBox(msg)
                result = msg.exec_()
            
            else:
                msgtext = 'EXIF data for ' + str(self.GetAffectedRowsCount("chosen")) + ' files will be changed.'
                if self.chkCameraMake.isChecked()  == True:
                    msgtext = msgtext + "\n\nCamera Make will be set to:\n'" + exifMake + "'"
                if self.chkCameraModel.isChecked()  == True:
                    msgtext = msgtext + "\n\nCamera Model will be set to:\n'" + exifModel + "'"
                if self.chkImageDescription.isChecked()  == True:
                    msgtext = msgtext + "\n\nImage Description  will be set to:\n'" + self.txtImageDescription.text() + "'"
                if self.chkLensMake.isChecked()  == True:
                    msgtext = msgtext + "\n\nLens Make will be set to:\n'" + exifLensMake + "'"
                if self.chkLensModel.isChecked()  == True:
                    msgtext = msgtext + "\n\nLens Model will be set to:\n'" + exifLensModel + "'"
                if self.chkUserComment.isChecked()  == True:
                    msgtext = msgtext + "\n\nUser Comment will be set to:\n'" + exifUserComment + "'"
                if self.chkArtist.isChecked()  == True:
                    msgtext = msgtext + "\n\nArtist will be set to:\n'" + exifArtist + "'"
                if self.chkCopyright.isChecked()  == True:
                    msgtext = msgtext + "\n\nCopyright will be set to:\n'" + exifCopyright + "'"
#                if self.chkOriginalDate.isChecked() == True:
#                    msgtext = msgtext + "\n\nOriginal Image Date will be set to:\n'" + exifDate + "'"
                if self.chkEmbedThumbnail.isChecked() == True:
                    if "all" in self.cboThumbnail.currentText():
                        msgtext = msgtext + "\n\nThumbnail will be embedded into ALL images.\n"
                    if "absent" in self.cboThumbnail.currentText():
                        msgtext = msgtext + "\n\nThumbnail will be embedded only into images without one.\n"
                msgtext = msgtext + "\n\nThis operation only affects JPEG files.\n"
                msg = QtWidgets.QMessageBox()
                msg.setText(msgtext)
                msg.setIcon(QtWidgets.QMessageBox.Question)
                msg.setWindowTitle("Write EXIF Data")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msg = self.FormatMessageBox(msg)
                result = msg.exec_()
                
                if result == QtWidgets.QMessageBox.Ok:
                    self.lblBigPhoto.hide()
                    self.lblProgressBar.setText("Writing EXIF data to files...")
                    self.lblProgressBar.show()
                    self.progressBar.setValue(0)
                    self.progressBar.show()
                    R = 0
                    totalFiles = self.GetAffectedRowsCount("chosen")
                    selRows = self.GetAffectedRows("chosen")
                    for r in selRows:
                        p = self.db.getPhoto(r)
                        if p["suffix"] in (".jpg", ".jpeg", ".JPG", ".JPEG"):
                            exif_dict = p["exif"] #exif_dict = piexif.load(p["filename"]) 
                            if self.chkCameraMake.isChecked()  == True:
                                exif_dict["0th"][piexif.ImageIFD.Make] = exifMake.encode('utf-8')
                            if self.chkCameraModel.isChecked()  == True:
                                exif_dict["0th"][piexif.ImageIFD.Model] = exifModel.encode('utf-8')
                            if self.chkImageDescription.isChecked()  == True:
                                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = exifImageDescription.encode('utf-8')
                            if self.chkLensMake.isChecked()  == True:
                                exif_dict["Exif"][piexif.ExifIFD.LensMake] = exifLensMake.encode('utf-8')
                            if self.chkLensModel.isChecked()  == True:
                                exif_dict["Exif"][piexif.ExifIFD.LensModel] = exifLensModel.encode('utf-8')
                            if self.chkUserComment.isChecked()  == True:
                                exif_dict["Exif"][piexif.ExifIFD.UserComment] = exifUserComment.encode('utf-8')
                            if self.chkArtist.isChecked()  == True:
                                exif_dict["0th"][piexif.ImageIFD.Artist] = exifArtist.encode('utf-8')
                            if self.chkCopyright.isChecked()  == True:
                                exif_dict["0th"][piexif.ImageIFD.Copyright] = exifCopyright.encode('utf-8')
#                            if self.chkOriginalDate.isChecked()  == True:
#                                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exifDate.encode('utf-8')
                            
                            if self.chkEmbedThumbnail.isChecked()  == True:
                                if "Write all" in self.cboThumbnail.currentText() or exif_dict["thumbnail"] is None:
                                    pm = QtGui.QPixmap()
                                    try:
                                            pmOrientation = exif_dict["0th"][piexif.ImageIFD.Orientation]
                                    except:
                                            pmOrientation= 1
                                            
                                    if exif_dict["thumbnail"] is None: #no thumbnail in file, but we can save time by using lstPhotos icon
                                        icon = self.lstPhotos.item(r).icon() #get icon from lstPhotos
                                        pm = icon.pixmap(icon.availableSizes()[0]) #get pixmap from icon
                                        #undo rotation of image that was done when pm was first generated
                                        if pmOrientation == 1:#no need to do anything. pmOrientation has not rotated icon.
                                            pass  
                                        if pmOrientation == 2:#icon is mirrored horizontally. Undo that.
                                            pm = pm.transformed(QtGui.QTransform().scale(-1, 1))
                                        if pmOrientation == 3:#icon is rotated 180. Undo that.
                                            pm = pm.transformed(QtGui.QTransform().rotate(180))
                                        if pmOrientation == 4:#icon is mirrored vertically. Undo that.
                                            pm = pm.transformed(QtGui.QTransform().scale(1, -1)) 
                                        if pmOrientation == 5:# icon is mirrored horizontally and rotated 270. Undo that.
                                            pm = pm.transformed(QtGui.QTransform().scale(-1, 1))
                                            pm = pm.transformed(QtGui.QTransform().rotate(270))
                                        if pmOrientation == 6:# icon is rotated 90. Undo that.
                                            pm = pm.transformed(QtGui.QTransform().rotate(270))
                                        if pmOrientation == 7:# icon is mirrored horizontally and rotated 90. Undo that.
                                            pm = pm.transformed(QtGui.QTransform().scale(-1, 1))
                                            pm = pm.transformed(QtGui.QTransform().rotate(90)) 
                                        if pmOrientation == 8:# icon is rotated 270. Undo that.
                                            pm = pm.transformed(QtGui.QTransform().rotate(90)) 
                                        thisThumbnail = self.ConvertPixmapToJpeg(pm)

                                    else: #thumb exists in file, but user wants to write all, so generate fresh high-quality thumb from image
                                        qimage = QtGui.QImage(p["filename"])
                                        pm.convertFromImage(qimage)
                                        print("write exif data: " + p["filename"] + " orientation is " + str(pmOrientation))
                                        if pmOrientation in [1, 2,  3,  4]: #scale the pixmap appropriately according to the image's orientation
                                            if pm.height() > pm.width():
                                                pm = pm.scaledToHeight(281)
                                            else:
                                                pm = pm.scaledToWidth(500)
                                        if pmOrientation in [5,  6, 7,  8]:
                                            if pm.height() > pm.width():
                                                pm = pm.scaledToHeight(500)
                                            else:
                                                pm = pm.scaledToWidth(281)
                                        #save thisThumbnail without rotation to insert into file
                                        thisThumbnail = self.ConvertPixmapToJpeg(pm) 
                                        #Before displaying newly generated thumb in lstPhotos, rotate according to orientation.
                                        if pmOrientation == 1:#no need to do anything. pmOrientation has not rotated icon.
                                            pass  
                                        if pmOrientation == 2:#icon needs to be mirrored horizontally
                                            pm = pm.transformed(QtGui.QTransform().scale(-1, 1))
                                        if pmOrientation == 3:#icon needs to be rotated 180. 
                                            pm = pm.transformed(QtGui.QTransform().rotate(180))
                                        if pmOrientation == 4:#icon needs to be mirrored vertically. 
                                            pm = pm.transformed(QtGui.QTransform().scale(1, -1)) 
                                        if pmOrientation == 5:# icon needs to be mirrored horizontally and rotated 270. 
                                            pm = pm.transformed(QtGui.QTransform().scale(-1, 1))
                                            pm.transformed(QtGui.QTransform().rotate(270))
                                        if pmOrientation == 6:# icon needs to be rotated 90. 
                                            pm = pm.transformed(QtGui.QTransform().rotate(90))
                                        if pmOrientation == 7:# icon needs to be mirrored horizontally and rotated 90. 
                                            pm = pm.transformed(QtGui.QTransform().scale(-1, 1))
                                            pm = pm.transformed(QtGui.QTransform().rotate(90)) 
                                        if pmOrientation == 8:# icon needs to be rotated 270. 
                                            pm = pm.transformed(QtGui.QTransform().rotate(270)) 
                                        #insert new icon into lstPhotos
                                        self.lstPhotos.item(r).setIcon(QtGui.QIcon(pm))

                                    exif_dict['thumbnail'] = thisThumbnail
        
                            for t in (282,  283): #sanitize exif data so it's compatible with piexif expectations
                                if t in exif_dict["0th"]:
                                    if type(exif_dict["0th"][t]) is not tuple:
                                        exif_dict["0th"][t] = (int(exif_dict["0th"][t]),  1)
                            if 41729 in exif_dict["Exif"]:
                                if type(exif_dict["Exif"][41729]) is not bytes:
                                    if exif_dict["Exif"][41729] == 1:
                                        exif_dict["Exif"][41729]  = b'\x01'
                            exif_bytes = piexif.dump(exif_dict)
                            try:
                                piexif.insert(exif_bytes, p["filename"])
                                self.db.updateExif(r, exif_dict)
                            except:
                                print("failed to write to " + p["filename"])
                            self.progressBar.setValue(int(100*R/totalFiles))
                            R += 1
                            QtWidgets.qApp.processEvents()
                            
            self.lstPhotos.repaint()
            self.DisplayEXIFData()
            self.lblProgressBar.hide()
            self.progressBar.hide()
            self.DisplayBigPhoto()
            self.setCursor(QtCore.Qt.ArrowCursor)


    def WriteExifDate(self):
        self.SanitizeDateTime()

        if self.lstPhotos.count() > 0:
            badExifData = False
            if self.chkOriginalDate.isChecked() is True:
                exifDate = str(self.txtYear.text())
                exifDate = exifDate + ":" + str(self.txtMonth.text())
                exifDate = exifDate + ":" + str(self.txtDay.text())
                if "<" in exifDate: 
                    if "<" in str(self.txtYear.text()) and self.cboDateEdit.currentText() == "Edit year": badExifData = True
                    if "<" in str(self.txtMonth.text()) and self.cboDateEdit.currentText() == "Edit month": badExifData = True
                    if "<" in str(self.txtDay.text()) and self.cboDateEdit.currentText() == "Edit day": badExifData = True
                    if "<" in exifDate and self.cboDateEdit.currentText() == "Edit all parts": badExifData = True
            if self.chkOriginalTime.isChecked() is True:
                exifTime = str(self.txtHour.text())
                exifTime = exifTime + ":" + str(self.txtMinute.text())
                exifTime = exifTime + ":" + str(self.txtSecond.text())
                if "<" in exifTime:                 
                    if "<" in str(self.txtHour.text()) and self.cboTimeEdit.currentText() == "Edit hour": badExifData = True
                    if "<" in str(self.txtMinute.text()) and self.cboTimeEdit.currentText() == "Edit minute": badExifData = True
                    if "<" in str(self.txtSecond.text()) and self.cboTimeEdit.currentText() == "Edit second": badExifData = True
                    if "<" in exifTime and self.cboTimeEdit.currentText() == "Edit all parts": badExifData = True
            if self.chkShiftDate.isChecked() is True:
                exifShift = str(self.txtShiftYear.text())
                exifShift = exifShift + ":" + str(self.txtShiftMonth.text())
                exifShift = exifShift + ":" + str(self.txtShiftDay.text())
                exifShift = exifShift + " " + str(self.txtShiftHour.text())
                exifShift = exifShift + ":" + str(self.txtShiftMinute.text())
                exifShift = exifShift + ":" + str(self.txtShiftSecond.text())

            if badExifData == True:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setWindowTitle("Invalid date or time entries")
                msg.setText('One or more date or time entries are invalid. Please correct them.\n')
                msg = self.FormatMessageBox(msg)
                result = msg.exec_()
           
            else:#no pertinent bad data exists
                msgtext = 'Original image date/time data for ' + str(self.GetAffectedRowsCount("chosen")) + ' files will be changed.'
                
                if self.chkOriginalDate.isChecked() is True:
                    if self.cboDateEdit.currentText() == "Edit year": 
                        msgtext = msgtext + "\n\nOriginal Image Date year will be set to: '" + str(self.txtYear.text()) + "'"
                    if self.cboDateEdit.currentText() == "Edit month":
                        msgtext = msgtext + "\n\nOriginal Image Date month will be set to: '" + str(self.txtMonth.text()) + "'"
                    if self.cboDateEdit.currentText() == "Edit day":
                        msgtext = msgtext + "\n\nOriginal Image Date day will be set to: '" + str(self.txtDay.text()) + "'"
                    if self.cboDateEdit.currentText() == "Edit all parts":
                        msgtext = msgtext + "\n\nOriginal Image Date will be set to: '" + exifDate + "'"

                if self.chkOriginalTime.isChecked() is True:
                    if self.cboTimeEdit.currentText() == "Edit hour": 
                        msgtext = msgtext + "\n\nOriginal Image Date hour will be set to: '" + str(self.txtHour.text()) + "'"
                    if self.cboTimeEdit.currentText() == "Edit minute":
                        msgtext = msgtext + "\n\nOriginal Image Date month will be set to: '" + str(self.txtMinute.text()) + "'"
                    if self.cboTimeEdit.currentText() == "Edit second":
                        msgtext = msgtext + "\n\nOriginal Image Date day will be set to: '" + str(self.txtSecond.text()) + "'"
                    if self.cboTimeEdit.currentText() == "Edit all parts":
                        msgtext = msgtext + "\n\nOriginal Image Date will be set to: '" + exifTime + "'"
                    
                if self.chkShiftDate.isChecked() is True:
                    if "Add" in self.cboTimeShift.currentText():
                        msgtext = msgtext + "\n\nOriginal Image Date/Time will be INCREASED by: '" + exifShift
                    if "Subtract" in self.cboTimeShift.currentText():
                        msgtext = msgtext + "\n\nOriginal Image Date/Time will be DECREASED by: '" + exifShift
                        
                msgtext = msgtext + "\n\nThis operation only affects .jpg and .jpeg files.\n"
                msg = QtWidgets.QMessageBox()
                msg.setText(msgtext)
                msg.setIcon(QtWidgets.QMessageBox.Question)
                msg.setWindowTitle("Editing Image Original Date and Time")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msg = self.FormatMessageBox(msg)
                result = msg.exec_()

                if result == QtWidgets.QMessageBox.Ok:
                    self.lblBigPhoto.hide()
                    self.lblProgressBar.setText("Writing original date/time to files...")
                    self.lblProgressBar.show()
                    self.progressBar.setValue(0)
                    self.progressBar.show()
                    
                    count = 0
                    totalFiles = self.GetAffectedRowsCount("chosen")
                    selRows = self.GetAffectedRows("chosen")
                    for r in selRows:
                        p = self.db.getPhoto(r)
                        if p["suffix"] in (".jpg", ".JPG", ".jpeg", ".JPEG"):
                            exif_dict = p["exif"] #exif_dict = piexif.load(p["filename"]) 
                            if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                                thisExifTimestamp = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode("utf-8")
                            else:
                                thisExifTimestamp = "0000:00:00 00:00:00"
                            
                            if self.chkOriginalDate.isChecked() is True:
                                if self.cboDateEdit.currentText() == "Edit year": 
                                    thisExifTimestamp = str(self.txtYear.text()) + thisExifTimestamp[4:]
                                if self.cboDateEdit.currentText() == "Edit month":
                                    thisExifTimestamp = thisExifTimestamp[0:5] + str(self.txtMonth.text()) + thisExifTimestamp[7:]
                                if self.cboDateEdit.currentText() == "Edit day":
                                    thisExifTimestamp = thisExifTimestamp[0:8] + str(self.txtDay.text()) + thisExifTimestamp[10:]
                                if self.cboDateEdit.currentText() == "Edit all parts":
                                    thisExifTimestamp = exifDate  + thisExifTimestamp[10:]
                                
                            if self.chkOriginalTime.isChecked() is True:
                                if self.cboTimeEdit.currentText() == "Edit hour": 
                                    thisExifTimestamp = thisExifTimestamp[0:11] + str(self.txtHour.text()) + thisExifTimestamp[13:]
                                if self.cboTimeEdit.currentText() == "Edit minute":
                                    thisExifTimestamp = thisExifTimestamp[0:14] + str(self.txtMinute.text()) + thisExifTimestamp[16:]
                                if self.cboTimeEdit.currentText() == "Edit second":
                                    thisExifTimestamp = thisExifTimestamp[0:17] + str(self.txtSecond.text())
                                if self.cboTimeEdit.currentText() == "Edit all parts":
                                    thisExifTimestamp = thisExifTimestamp[0:11] + exifTime 

                            if self.chkShiftDate.isChecked() is True:
                                thisYear = int(thisExifTimestamp[0:4])
                                thisMonth = int(thisExifTimestamp[5:7])
                                thisDay = int(thisExifTimestamp[8:10])
                                thisHour = int(thisExifTimestamp[11:13])
                                thisMinute = int(thisExifTimestamp[14:16])
                                thisSecond = int(thisExifTimestamp[17:19])
                                shiftYear = int(self.txtShiftYear.text())
                                shiftMonth = int(self.txtShiftMonth.text())
                                shiftDay = int(self.txtShiftDay.text())
                                shiftHour = int(self.txtShiftHour.text())
                                shiftMinute = int(self.txtShiftMinute.text())
                                shiftSecond = int(self.txtShiftSecond.text())
                                
                                if "Add" == self.cboTimeShift.currentText():
                                    newYear = thisYear + shiftYear
                                    newMonth = thisMonth + shiftMonth
                                    newDay = thisDay + shiftDay
                                    newHour = thisHour + shiftHour
                                    newMinute = thisMinute + shiftMinute
                                    newSecond = thisSecond + shiftSecond
                                    
                                    if newSecond > 59:
                                        newMinute += 1
                                        newSecond = newSecond - 60
                                    if newMinute > 59:
                                        newHour += 1
                                        newMinute = newMinute - 60
                                    if newHour > 23:
                                        newDay += 1
                                        newHour = newHour - 24
                                    if newDay > 28:
                                        if newMonth == 2: #February
                                            if newYear % 4 == 0: #it's a leap year, so Feb has 29 days 
                                                if newDay > 29:
                                                    newMonth += 1
                                                    newDay = newDay - 29
                                            else: #it's not a leap year, so Feb has 28 days
                                                newMonth += 1
                                                newDay = newDay -28
                                        elif newMonth in (3,  4,  6,  9,  11): # Mar, Apr, Jun, Aug, Nov have 30 days
                                                if newDay > 30:
                                                    newMonth += 1
                                                    newDay = newDay - 30
                                        elif newMonth in (1,  5,  7,  10,  12): # Jan, May, Jul, Oct, Dec have 31 days
                                                if newDay > 31:
                                                    newMonth += 1
                                                    newDay = newDay - 31
                                    if newMonth > 12:
                                        newYear += 1
                                        newMonth = newMonth - 12
                                    
                                if "Subtract" == self.cboTimeShift.currentText():
                                    newYear = thisYear - shiftYear
                                    newMonth = thisMonth - shiftMonth
                                    newDay = thisDay - shiftDay
                                    newHour = thisHour - shiftHour
                                    newMinute = thisMinute - shiftMinute
                                    newSecond = thisSecond - shiftSecond
                                    
                                    if newMonth < 1:
                                        newYear -= 1
                                        newMonth = 12 + newMonth
                                    if newSecond < 0:
                                        newMinute -= 1
                                        newSecond = 60 + newSecond 
                                    if newMinute < 0:
                                        newHour -= 1
                                        newMinute = 60 + newMinute
                                    if newHour < 0:
                                        newDay -= 1
                                        newHour = 24 - newHour
                                    if newDay < 1:
                                        newMonth -= 1
                                        if newMonth == 2: #February
                                            if newYear % 4 == 0: #it's a leap year, so Feb has 29 days 
                                                newDay = 29 + newDay
                                            else: #it's not a leap year, so Feb has 28 days
                                                newDay = 28 + newDay
                                        elif newMonth in (3,  4,  6,  9,  11): # Mar, Apr, Jun, Aug, Nov have 30 days
                                                newDay = 30 + newDay
                                        elif newMonth in (0,  1,  5,  7,  10,  12): # Jan, May, Jul, Oct, Dec have 31 days
                                                newDay = 31 + newDay
                                    if newMonth < 1:
                                        newMonth = 12 + newMonth 
                                        newYear -= 1

                                newYearString = str(newYear)
                                newMonthString = str(newMonth)
                                newDayString = str(newDay)
                                newHourString = str(newHour)
                                newMinuteString = str(newMinute)
                                newSecondString = str(newSecond)
                                while len(newYearString) < 4:
                                    newYearString = "0" + newYearString
                                while len(newMonthString) < 2:
                                    newMonthString = "0" + newMonthString
                                while len(newDayString) < 2:
                                    newDayString = "0" + newDayString
                                while len(newHourString) < 2:
                                    newHourString = "0" + newHourString
                                while len(newMinuteString) < 2:
                                    newMinuteString = "0" + newMinuteString
                                while len(newSecondString) < 2:
                                    newSecondString = "0" + newSecondString                                        
                                thisExifTimestamp = newYearString + ":" + newMonthString + ":" + newDayString + " " + newHourString + ":" + newMinuteString + ":" + newSecondString
                            
                            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = thisExifTimestamp.encode('utf-8')
                            
                            for t in (282,  283): #sanitize exif data so it's compatible with piexif expectations
                                if t in exif_dict["0th"]:
                                    if type(exif_dict["0th"][t]) is not tuple:
                                        exif_dict["0th"][t] = (int(exif_dict["0th"][t]),  1)
                            if 41729 in exif_dict["Exif"]:
                                if type(exif_dict["Exif"][41729]) is not bytes:
                                    if exif_dict["Exif"][41729] == 1:
                                        exif_dict["Exif"][41729]  = b'\x01'
                                        
                            exif_bytes = piexif.dump(exif_dict)
                            piexif.insert(exif_bytes, p["filename"])
                            self.db.updateExif(r, exif_dict)
                            self.progressBar.setValue(int(100*count/totalFiles))
                            count += 1
                            QtWidgets.qApp.processEvents()
                            
                    self.DisplayEXIFData()
                    self.lblProgressBar.hide()
                    self.progressBar.hide()
                    self.lblBigPhoto.show()
            self.setCursor(QtCore.Qt.ArrowCursor)


class photoDb():

    def __init__(self,  mainwindow):
        self.db = []
        self.mainwindow = mainwindow

    def adjustOrder(self,  basenames):
        temp = []
        for bn in basenames:
            for p in self.db:
                if p["basename"] + p["suffix"] == bn:
                    temp.append(p)
                    break
        self.db = temp

    def clearDb(self):
        self.db = []

    def createDb(self,  files):
        R = 0
        totalFiles = len(files)
        for f in files:#append photos one at a time so we can use the progress bar in this class
            p = {} #clear data in p and declare it as a dictionary
            p["basename"],  p["suffix"] = os.path.splitext(basename(f))
            p["path"] = dirname(f)
            p["filename"] = f
            try:
                p["exif"] = piexif.load(f)
            except:
                pass
            if "exif" in p:
                try:
                    p["originaldate"] = p["exif"]["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()
                except:
                    p["originaldate"] = ""
            self.db.append(p)
            self.mainwindow.setProgressBarValue(int(100*R/totalFiles))
            QtWidgets.qApp.processEvents()
            R += 1

    def deleteRow(self,  row):
        del self.db[row]

        
    def getAllPhotos(self):
        return self.db


    def getPhoto(self,  row):
        return self.db[row]


    def sortAlphabetically(self):
        self.db = sorted(self.db, key=lambda k: k['basename'])


    def sortByOriginalDate(self):
        self.db = sorted(self.db, key=lambda k: k['originaldate'])


    def updateExif(self, row,  exif_dict):
        self.db[row]["exif"] = exif_dict


    def updateName(self,  row,  filename):
        self.db[row]["filename"] = filename
        self.db[row]["basename"],  self.db[row]["suffix"] = os.path.splitext(basename(filename))
        self.db[row]["path"] = dirname(filename)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
