from datetime import datetime

def get_epochtime_ms():
    return round(datetime.utcnow().timestamp() * 1000)

class Clock:
    def __init__(self):
        self.time=self.now()
    def now(self):
        return get_epochtime_ms()
    def update(self):
        elapsed=self.elapsed()
        self.time=self.now()
        return elapsed
    def elapsed(self):
        return self.now()-self.time


class Profiler:

    def __init__(self):
        self.reset()
    def event(self, name):
        self.measures.append(get_epochtime_ms())
        self.names.append(name)
    def summary(self):
        if len(self.measures)>1:
            # deltas=[j-i for i, j in zip()]
            vals=zip(self.names[:-1], self.names[1:],self.measures[:-1],self.measures[1:])
            tags = [f"{n1} to {n2}: {t2-t1}ms" for n1,n2,t1,t2 in vals]
            return "\n".join(tags)
        elif len(self.measures)==1:
            return f"One measure ({self.name[0]})."
        else:
            return "No measures."
    def reset(self):
        self.measures=[]
        self.names=[]


class FPS:
    def __init__(self):
        self.last=get_epochtime_ms()

        self.fps=0
    def frame_processed(self):
        self.last = get_epochtime_ms()
        return get_epochtime_ms()
    def update(self):
        elapsed=self.elapsed()
        self.time=self.now()
        return elapsed
    def fps(self):
        return self.fps
