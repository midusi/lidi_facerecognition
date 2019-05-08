from PyQt5.QtCore import (QThread, Qt, pyqtSignal,pyqtSlot)
from PyQt5.QtCore import QObject
from backend.greeting import  SoundGreeter

class GreetingWorker(QObject):

    def __init__(self,person_db,settings):
        super().__init__()
        self.greeter=SoundGreeter(person_db,settings)

    @pyqtSlot(object)
    def update_tracked_objects(self, objects_tracked):
        self.greeter.update_objects_tracked(objects_tracked)

    def update_person_db(self,person_db):
        self.greeter.update_person_db(person_db)