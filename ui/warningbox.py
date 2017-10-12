
from PyQt4 import QtCore, QtGui


class Class_warningBox():
    """TODO add all select box """
    def __init__(self, mgis):
        self.mgis = mgis
        self.mdb = self.mgis.mdb

    def yes_no_q(self, msg, title=''):
        d = QtGui.QMessageBox()
        d.setWindowTitle(title)
        d.addButton(QtGui.QMessageBox.Yes)
        d.addButton(QtGui.QMessageBox.No)
        d.setDefaultButton(QtGui.QMessageBox.No)
        d.setText(msg)
        ret =d.exec_()

        if ret == QtGui.QMessageBox.Yes:
            return True
        else:
            return False