# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_settings_Simple.ui'
#
# Created: Wed Sep 13 17:17:32 2017
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName(_fromUtf8("Settings"))
        Settings.resize(620, 473)
        Settings.setSizeGripEnabled(False)
        Settings.setModal(True)
        self.gridLayout = QtGui.QGridLayout(Settings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox_postgres = QtGui.QGroupBox(Settings)
        self.groupBox_postgres.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_postgres.sizePolicy().hasHeightForWidth())
        self.groupBox_postgres.setSizePolicy(sizePolicy)
        self.groupBox_postgres.setObjectName(_fromUtf8("groupBox_postgres"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_postgres)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.txt_path_postgres = QtGui.QLineEdit(self.groupBox_postgres)
        self.txt_path_postgres.setObjectName(_fromUtf8("txt_path_postgres"))
        self.horizontalLayout.addWidget(self.txt_path_postgres)
        self.bt_pathPostgres = QtGui.QPushButton(self.groupBox_postgres)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bt_pathPostgres.sizePolicy().hasHeightForWidth())
        self.bt_pathPostgres.setSizePolicy(sizePolicy)
        self.bt_pathPostgres.setObjectName(_fromUtf8("bt_pathPostgres"))
        self.horizontalLayout.addWidget(self.bt_pathPostgres)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_postgres, 2, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(Settings)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.open_lastChbox = QtGui.QCheckBox(self.groupBox_3)
        self.open_lastChbox.setChecked(True)
        self.open_lastChbox.setObjectName(_fromUtf8("open_lastChbox"))
        self.verticalLayout_8.addWidget(self.open_lastChbox)
        self.open_lastChbox_schema = QtGui.QCheckBox(self.groupBox_3)
        self.open_lastChbox_schema.setEnabled(True)
        self.open_lastChbox_schema.setChecked(True)
        self.open_lastChbox_schema.setObjectName(_fromUtf8("open_lastChbox_schema"))
        self.verticalLayout_8.addWidget(self.open_lastChbox_schema)
        self.debugModeChbox = QtGui.QCheckBox(self.groupBox_3)
        self.debugModeChbox.setObjectName(_fromUtf8("debugModeChbox"))
        self.verticalLayout_8.addWidget(self.debugModeChbox)
        self.gridLayout.addWidget(self.groupBox_3, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.actionBt_pathPostgres = QtGui.QAction(Settings)
        self.actionBt_pathPostgres.setObjectName(_fromUtf8("actionBt_pathPostgres"))
        self.actionTxt_path_postgres = QtGui.QAction(Settings)
        self.actionTxt_path_postgres.setObjectName(_fromUtf8("actionTxt_path_postgres"))

        self.retranslateUi(Settings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Settings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Settings.reject)
        QtCore.QObject.connect(self.bt_pathPostgres, QtCore.SIGNAL(_fromUtf8("clicked()")), self.actionBt_pathPostgres.trigger)
        QtCore.QObject.connect(self.txt_path_postgres, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.actionTxt_path_postgres.trigger)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(_translate("Settings", "Mascaret Options", None))
        self.groupBox_postgres.setTitle(_translate("Settings", "Postgres", None))
        self.bt_pathPostgres.setText(_translate("Settings", "Path Postgres", None))
        self.groupBox_3.setTitle(_translate("Settings", "Application", None))
        self.open_lastChbox.setText(_translate("Settings", "Load last Mascaret database when starting", None))
        self.open_lastChbox_schema.setText(_translate("Settings", "Load last schema when starting", None))
        self.debugModeChbox.setText(_translate("Settings", "Debugging mode", None))
        self.actionBt_pathPostgres.setText(_translate("Settings", "bt_pathPostgres", None))
        self.actionTxt_path_postgres.setText(_translate("Settings", "txt_path_postgres", None))

