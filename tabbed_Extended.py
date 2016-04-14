from tabbedUI import Ui_MainWindow
from PyQt4 import QtCore, QtGui
import ydmAPI

class YDMWindow(Ui_MainWindow):

	def handleEvents(self):
		self.btnDownloadList.clicked.connect(self.download_list)
		self.btnParseVidLink.clicked.connect(self.getVidLink)
		self.btnFolderVid.clicked.connect(self.change_folder)

	def setDefaults(self):
		self.txtFolderVid.setText(ydmAPI.getDownloadDir())
		print("Damn")

	def download_list(self):
		print('Download List Called...')
		print(self.txtUrlList.text())

	def getVidLink(self):
		qualityCombo = self.comboQuality
		print('Download Video: ')
		pageURL = self.txtUrlVid.text()
		details = ydmAPI.getVideoDetails(pageURL)
		while(qualityCombo.currentIndex() > -1):
			qualityCombo.removeItem(qualityCombo.currentIndex())
		for detail in details:
			qualityCombo.addItem("{0} ({1} MB)".format(detail['resolution'], detail['size']))
			self.txtVidFilename.setText(detail['filename'])
		self.btnDownloadVid.setEnabled(True)

	def change_folder(self):
		path = ydmAPI.askdirectory()
		self.txtFolderVid.setText(path)


if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	MainWindow = QtGui.QMainWindow()

	ydmUi = YDMWindow()

	# CALL THE SETUP/INIT/HANDLE FOR YDMUI IN PROPER ORDER
	ydmUi.setupUi(MainWindow)

	ydmUi.handleEvents()
	ydmUi.setDefaults()

	MainWindow.show()
	sys.exit(app.exec_())
