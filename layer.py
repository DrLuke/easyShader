class RuntimeData:
    def __init__(self):
        self.fft = None
        self.bpm = 0
        self.beat = 0
        self.beataccum = 0
        self.time = 0
        self.dt = 0.1
        self.res = [1024, 768]
        self.fbo = None
        self.fbotexture = None

        self.uniforms = {}

from inotify_simple import INotify, flags
class FileWatch:
    def __init__(self, path):
        self.path = path
        fl = flags.MODIFY
        self.i = INotify()
        self.watch = self.i.add_watch(self.path, fl)
        with open(self.path, "r") as f:
            self.content = f.read()

    def check(self):
        events = self.i.read(timeout=0)
        for event in events:
            if event.mask | flags.MODIFY:
                with open(self.path, "r") as f:
                    self.content = f.read()
            return True
        return False


class BaseLayer():
    def __init__(self):
        self.level = 0
        self.disabled = False

        self.init()

    def init(self):
        pass

    def render(self, runtimeData):
        pass

    def getData(self):
        return None

    def setData(self, data):
        pass

    def checkUniform(self, runtime, layer, uniform, default=0):
        if layer in runtime.uniforms:
            if uniform in runtime.uniforms[layer]:
                return runtime.uniforms[layer][uniform]
        return default




