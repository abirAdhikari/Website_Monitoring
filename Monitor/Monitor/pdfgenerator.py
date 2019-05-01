import sys
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets


class PdfGenerator(object):
	def __init__(self):
		pass
		
	def convert_it(self, src_file, dst_file):
		app = QtWidgets.QApplication(sys.argv)
		loader = QtWebEngineWidgets.QWebEngineView()
		loader.setZoomFactor(1)
		loader.page().pdfPrintingFinished.connect(
			lambda *args: print('finished:', args))
		url = QtCore.QUrl.fromLocalFile(src_file)
		loader.load(url)

		def emit_pdf(finished):
			loader.show()
			loader.page().printToPdf(dst_file)

		loader.loadFinished.connect(emit_pdf)

		app.exec()
		