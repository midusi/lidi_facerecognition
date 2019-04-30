import logging
import setproctitle
from abc import abstractmethod
import signal
class Worker:

    def __init__(self,name):
        self.stopped=False
        self.name=name
        logging.getLogger().setLevel(logging.INFO)


    def run(self):
        # ignore keyboard interrupts
        #signal.signal(signal.SIGINT, signal.SIG_IGN)

        process_title = self.tag(setproctitle.getproctitle())
        setproctitle.setproctitle(process_title)

        logging.info(self.tag("started"))
        try:
            self.work()
        except (KeyboardInterrupt, SystemExit) as e:
            self.stop()
        except Exception as e:
            logging.info(self.tag(f"Unknown exception {str(e)}..."))
            self.stop()
        finally:
            logging.info(self.tag("stopped"))

    @abstractmethod
    def work(self):
        pass

    def stop(self):
        self.stopped=True

    def tag(self,message):
        return f"[{self.name}] {message}"