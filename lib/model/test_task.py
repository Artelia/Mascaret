from qgis.PyQt.QtCore import QObject, pyqtSignal, Qt
from qgis.core import QgsTask, QgsApplication, Qgis, QgsMessageLog

MESSAGE_CATEGORY = "Mascaret"

class TaskSignals(QObject):
    model_completed = pyqtSignal(int, dict)
    launch_completed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

class TaskMascaret2(QgsTask):
    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)
        self.signal = TaskSignals()
        self.signal.moveToThread(QgsApplication.instance().thread())

    def run(self):
        QgsMessageLog.logMessage("Run started rrrr", MESSAGE_CATEGORY, Qgis.Info)
        self.signal.launch_completed.emit(True)
        return True

# Exemple d'objet receveur
class Receiver(QObject):
    def __init__(self):
        super().__init__()

    def test(self, success):
        print(f"Signal reçu ! Succès = {success}")

