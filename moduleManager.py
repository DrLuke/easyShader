import importlib
from glob import glob

from inotify_simple import INotify, flags

import traceback
import sys

from layer import BaseLayer



class ModuleManager():
    def __init__(self):
        fl = flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF
        self.i = INotify()
        self.watch = self.i.add_watch("layers", fl)

        self.layers = {}
        self.layersOrdered = []

        files = glob("layers/*.py")

        for file in files:
            self.createLayer(file[7:])

        self.reorderLayers()


    def checkNotify(self):
        events = self.i.read(timeout=0)
        for event in events:
            self.checkEvent(event)

    def checkEvent(self, event):
        name = event.name
        if "___jb_tmp___" in event.name:    # Thanks jetbrains
            name = name[:-12]

        if "___jb_old___" in event.name:    # Thanks jetbrains
            return

        if not name[-3:] == ".py":
            return

        if event.mask & flags.ISDIR:
            return

        if event.mask & (flags.MODIFY):
            try:
                self.replaceLayer(name)
            except Exception as exc:
                print(traceback.format_exc(), file=sys.stderr)
                print(exc, file=sys.stderr)

        if event.mask & flags.DELETE:
            try:
                self.deleteLayer(name)
            except Exception as exc:
                print(traceback.format_exc(), file=sys.stderr)
                print(exc, file=sys.stderr)

        self.reorderLayers()

    def replaceLayer(self, name):
        if name in self.layers:
            cl = type(self.layers[name])
            mod = cl.__shadermod__
            importlib.reload(mod)
            cl = mod.Layer
            cl.__shadermod__ = mod
        else:
            cl = self.getLayerClass(name)

        newObj = cl()

        if name in self.layers:
            prevData = self.layers[name].getData()
            if prevData is not None:
                newObj.setData(prevData)

        self.layers[name] = newObj

        print("\033[92m*** SUCCESSFULLY RELOADED:\033[0m " + name)

    def createLayer(self, name):
        if name in self.layers:
            return
        try:
            cl = self.getLayerClass(name)
            self.layers[name] = cl()
        except Exception as exc:
            print(traceback.format_exc(), file=sys.stderr)
            print(exc, file=sys.stderr)
            self.layers[name] = BaseLayer()

    def deleteLayer(self, name):
        del self.layers[name]

    def getLayerClass(self, name):
        importlib.invalidate_caches()
        newmod = importlib.import_module("layers." + name[:-3])
        newclass = newmod.Layer
        newclass.__shadermod__ = newmod

        return newclass

    def reorderLayers(self):
        self.layersOrdered = sorted(self.layers.values(), key=lambda x: x.level)

