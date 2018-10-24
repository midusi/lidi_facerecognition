from datetime import datetime,date
import pyttsx3


class SoundGreeter:
    def __init__(self,person_db,settings):
        self.update_person_db(person_db)
        self.settings=settings
        self.last_greeting_time=datetime.now()
        self.engine = pyttsx3.init()
        self.engine.setProperty("voice","spanish-latin-am")

    def get_message_template(self,current_time):
        hour=current_time.hour
        if hour>5 and hour<14:
            message="Buen dia"
        elif hour<19:
            message="Buenas tardes"
        else:
            message="Buenas noches"
        return message

    def update_objects_tracked(self,objects_tracked):

        if not self.settings.sound.voice_greeting_enabled:
            return

        now = datetime.now()
        message_template=self.get_message_template(now)
        for object_tracked in objects_tracked:
            if object_tracked.tracking_converged() and object_tracked.recognized():
                class_id=object_tracked.class_id()
                if not class_id in self.greet_time:
                    greet=True
                else:
                    last_user_greeting = self.greet_time[class_id]
                    greet=not last_user_greeting.date()==now.date()

                if greet:
                    self.greet_time[class_id] = now
                    person=self.person_db[class_id]

                    message=f"{message_template} {person.name}"
                    self.engine.say(message)
                    self.engine.runAndWait()



    def update_person_db(self,person_db):
        self.person_db = person_db
        self.greet_time = {}