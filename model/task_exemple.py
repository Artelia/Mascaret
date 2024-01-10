import random
from time import sleep
from qgis.core import QgsApplication, QgsTask, QgsMessageLog, Qgis

MESSAGE_CATEGORY = 'Task Subclass'

class TaskSubclass(QgsTask):
    """This shows how to subclass QgsTask"""
    def __init__(self, description, duration):
        super().__init__(description, QgsTask.CanCancel)
        self.duration = duration
        self.total = 0
        self.iterations = 0
        self.exception = None

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        wait_time = self.duration / 100
        for i in range(100):
            sleep(wait_time)
            # use setProgress to report progress
            self.setProgress(i)
            arandominteger = random.randint(0, 500)
            self.total += arandominteger
            self.iterations += 1
            # check isCanceled() to handle cancellation
            if self.isCanceled():
                return False
            # # simulate exceptions to show how to abort task
            # if arandominteger == 42:
                # # DO NOT raise Exception('bad value!')
                # # this would crash QGIS
                # self.exception = Exception('bad value!')
                # return False
        return True

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        if result:
            QgsMessageLog.logMessage('Task "{name}" completed\nTotal: {total} (with {iterations} iterations)'.format(name=self.description(),
                                                                                                                     total=self.total,
                                                                                                                     iterations=self.iterations),
                                     MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('Task "{name}" not successful but without exception (probably the task was manually ' \
                                        'canceled by the user)'.format(name=self.description()),
                                         MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage('Task "{name}" Exception: {exception}'.format(name=self.description(),
                                                                                       exception=self.exception),
                                         MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage('Task "{name}" was canceled'.format(name=self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()


from qgis.PyQt.QtCore import pyqtSignal, QObject
class DoStuff(QObject):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        """Example of the class that needs to get tasks done. """
        """Subclassed examples. """
        self.longtask = TaskSubclass('class method long', 20)
        self.shorttask = TaskSubclass('class method short', 10)
        self.minitask = TaskSubclass('class method mini', 5)
        # Subtasks to do.
        self.shortsubtask = TaskSubclass('class method subtask short', 5)
        self.longsubtask = TaskSubclass('class method subtask long', 10)
        self.shortestsubtask = TaskSubclass('class method subtask shortest', 4)
        # Add a subtask (shortsubtask) to shorttask that must run after
        # minitask and longtask has finished
        self.shorttask.addSubTask(self.shortsubtask,
                                  [self.minitask, self.longtask])
        # Add a subtask (longsubtask) to longtask that must be run
        # before the parent task
        self.longtask.addSubTask(self.longsubtask, [], 
                                 TaskSubclass.ParentDependsOnSubTask)
        # Add a subtask (shortestsubtask) to longtask
        self.longtask.addSubTask(self.shortestsubtask)

        """From function examples. """
        self.MESSAGE_CATEGORY = 'Task from Function'

        self.task1 = QgsTask.fromFunction(u'function task', self.internal_task, on_finished=self.completed, wait_time=6)
        self.task2 = QgsTask.fromFunction(u'function task 2', self.internal_task, on_finished=self.completed, wait_time=5)

    def do_subclassed_tasks(self):
        """Do tasks using QgsTask subclass. """
        QgsApplication.taskManager().addTask(self.longtask)
        QgsApplication.taskManager().addTask(self.shorttask)
        QgsApplication.taskManager().addTask(self.minitask)

    def do_from_function_tasks(self):
        """Do tasks from a function. """
        QgsApplication.taskManager().addTask(self.task1)
        QgsApplication.taskManager().addTask(self.task2)
        return ("aaa")

    def internal_task(self, task, wait_time):
        """
        Raises an exception to abort the task.
        Returns a result if success.
        The result will be passed together with the exception (None in
        the case of success) to the on_finished method
        """
        QgsMessageLog.logMessage('Started task {}'.format(task.description()),
                                 self.MESSAGE_CATEGORY, Qgis.Info)
        wait_time = wait_time / 100
        total = 0
        iterations = 0
        for i in range(100):
            sleep(wait_time)
            # use task.setProgress to report progress
            task.setProgress(i)
            arandominteger = random.randint(0, 500)
            total += arandominteger
            iterations += 1
            # check task.isCanceled() to handle cancellation
            if task.isCanceled():
                self.stopped(task)
                return None
            # # raise an exception to abort the task
            # if arandominteger == 42:
                # raise Exception('bad value!')
        return {'total': total, 'iterations': iterations,
                'task': task.description()}

    def stopped(self, task):
        QgsMessageLog.logMessage(
            'Task "{name}" was canceled'.format(
                name=task.description()),
            self.MESSAGE_CATEGORY, Qgis.Info)

    def completed(self, exception, result=None):
        """This is called when do_task is finished.
        Exception is not None if do_task raises an exception.
        Result is the return value of do_task."""
        if exception is None:
            if result is None:
                QgsMessageLog.logMessage(
                    'Completed with no exception and no result '\
                    '(probably manually canceled by the user)',
                    self.MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    'Task {name} completed\n'
                    'Total: {total} ( with {iterations} '
                    'iterations)'.format(
                        name=result['task'],
                        total=result['total'],
                        iterations=result['iterations']),
                    self.MESSAGE_CATEGORY, Qgis.Info)
        else:
            QgsMessageLog.logMessage("Exception: {}".format(exception),
                                     MESSAGE_CATEGORY, Qgis.Critical)
            raise exception
