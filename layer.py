class RuntimeData:
    def __init__(self):
        self.fft = None
        self.bpm = 0
        self.beat = 0
        self.beataccum = 0

class BaseLayer():
    def __init__(self):
        self.level = 0

    def render(self, runtimeData):
        pass

    def getData(self):
        return None

    def setData(self, data):
        pass

