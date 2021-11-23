import itertools
from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import *
import sys

#fig, axes = plt.subplot(1, 1)
def graph_on_pick(evt):
    art = evt.artist
    print("artist :", art)

colors = ['b', 'r', 'g', 'c']
cc = itertools.cycle(colors)

fig = Figure()
canvas = FigureCanvas(fig)
ax1 = fig.add_subplot(111)

#fig, ax1 = pyplot.subplots()
#canvas = FigureCanvas(fig)
canvas.mpl_connect('pick_event', graph_on_pick)

wgt = QWidget()
lay = QVBoxLayout()
wgt.setLayout(lay)
lay.addWidget(canvas)

#pyplot.connect('pick_event', graph_on_pick)

l1,  = ax1.plot([1, 2], [5, 1], '-', color="blue", picker=5, label="a")
l2,  = ax1.plot([2, 1], [5, 3], '-', color="red", picker=5, label="b")
ax2 = ax1.twinx()
l3,  = ax2.plot([1, 2], [1, 7], '-', color="green", picker=5, label="c")

# legend1 = pyplot.legend([l1, l2, l3], ["l1", "l2", "l3"], loc=1)
# for legline in legend1.get_lines():
#     legline.set_picker(5)
# legend1.draggable(True)

legend2 = ax2.legend([l1, l2, l3], ["l1", "l2", "l3"], loc=1)
for legline in legend2.get_lines():
     legline.set_picker(5)
legend2.draggable(True)

canvas.draw()

#pyplot.gca().add_artist(legend1)

a = QApplication(sys.argv)
wgt.show()

r = a.exec_()



#pyplot.show()

# for p in parameters:
#
#     d1 = algo1(p)
#     d2 = algo2(p)
#     d3 = algo3(p)
#
#     c = next(cc)
#     axes.plot(d1, '-', color=c)
#     axes.plot(d2, '--', color=c)
#     axes.plot(d3, '.-', color=c)

# In total 3x3 lines have been plotted
# lines = axes.get_lines()
# legend1 = plt.legend([lines[i] for i in [0,1,2]], ["algo1", "algo2", "algo3"], loc=1)
# legend2 = plt.legend([lines[i] for i in [0,3,6]], parameters, loc=4)
# axes.add_artist(legend1)
# axes.add_artist(legend2)