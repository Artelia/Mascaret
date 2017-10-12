# chercher :  declar
#***************************
try:
    from matplotlib.backends.backend_qt4agg\
        import NavigationToolbar2QTAgg as NavigationToolbar

except:
    from matplotlib.backends.backend_qt4agg \
        import NavigationToolbar2QT as NavigationToolbar
# **************************************


self.verticalLayout_99 = QtGui.QVBoxLayout()
self.verticalLayout_99.setObjectName(_fromUtf8("verticalLayout_99"))
self.toolbar = NavigationToolbar(ProfilGraph.canvas, ProfilGraph)
self.verticalLayout_99.addWidget(ProfilGraph.canvas)
self.verticalLayout_99.addWidget(self.toolbar)
self.horizontalLayout_3.addLayout(self.verticalLayout_99)
# **************************************
class NavigationToolbar(NavigationToolbar):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar.toolitems if
                  t[0] in ('Home','Back','Forward', 'Pan', 'Zoom', 'Save')]
                  
#*****************************************
#suprimmer les deux dernière lignes