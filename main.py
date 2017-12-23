#!/bin/python3

import glfw
import sys
import tkinter
import json

import socket
from select import select

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import *
from OpenGL.GL import shaders
import OpenGL

from layer import BaseLayer, RuntimeData
from moduleManager import ModuleManager

class Main:
    def __init__(self, monitor, vidmode, fullscreen):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 31337))

        self.modman = ModuleManager()

        self.runtimeData = RuntimeData()

        self.vidmode = vidmode
        if fullscreen:
            self.glfwWindow = glfw.create_window(vidmode[0][0], vidmode[0][1], "Pyree 3.0 Trial [EXPIRES IN 29 DAYS]", None, None)
        else:
            self.glfwWindow = glfw.create_window(vidmode[0][0], vidmode[0][1], "Pyree 3.0 Trial [EXPIRES IN 29 DAYS]", None, None)

        if not self.glfwWindow:
            glfw.terminate()
            print("Failed to initialize window", file=sys.stderr)
            sys.exit(1)

        while not glfw.window_should_close(self.glfwWindow):
            glfw.poll_events()

            glfw.make_context_current(self.glfwWindow)

            self.loop()

            glfw.swap_buffers(self.glfwWindow)

        glfw.terminate()

    def loop(self):
        self.pollNetwork()
        self.modman.checkNotify()

        #glClearColor(0.2, 0.3, 0.3, 1.0)
        #glClear(GL_COLOR_BUFFER_BIT)

        for layer in self.modman.layersOrdered:
            layer.render(self.runtimeData)


    def pollNetwork(self):
        rlist, wlist, elist = select([self.sock], [], [], 0)

        while rlist:
            data, addr = self.sock.recvfrom(50000)
            try:
                data = data.decode()
                self.parseData(data)
            except:
                pass

            rlist, wlist, elist = select([self.sock], [], [], 0)

    def parseData(self, data):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return

        self.runtimeData.beat = False
        if data["datatype"] == "beat":
            self.runtimeData.beat = True
            self.runtimeData.beataccum += 1

        if data["datatype"] == "fft":
            self.runtimeData.fft = data["fft"]

        if data["datatype"] == "uniform":
            pass



class VidmodePicker():
    def __init__(self):
        self.exit = True

        self.top = tkinter.Tk()

        monitors = glfw.get_monitors()
        self.vidmodes = []
        for mon in monitors:
            modes = glfw.get_video_modes(mon)
            for mode in modes:
                self.vidmodes.append((mon, mode))

                self.lb = tkinter.Listbox(self.top)

        for vidmode in self.vidmodes:
            mon = vidmode[0]
            mode = vidmode[1]
            indx = self.vidmodes.index(vidmode)

            self.lb.insert(indx, str(mode))

            self.lb.pack(fill=tkinter.BOTH, expand=1)

        self.cbvar = tkinter.BooleanVar()
        self.cb = tkinter.Checkbutton(self.top, {"text": "Fullscreen", "variable": self.cbvar})
        self.cb.toggle()
        self.cb.pack()

        self.ob = tkinter.Button(self.top, {"text": "Launch", "command": self.onOk})
        self.ob.pack()

        self.top.mainloop()

    def onOk(self, *args):
        if self.lb.curselection():
            self.selectedVidmode = self.vidmodes[self.lb.curselection()[0]]
            self.fullScreen = self.cbvar.get()
            self.exit = False
            self.top.destroy()



if __name__ == "__main__":
    if not glfw.init():
        print("Failed to initialize glfw", file=sys.stderr)
        sys.exit(1)

    vp = VidmodePicker()
    if vp.exit:
        sys.exit(0)

    A = Main(vp.selectedVidmode[0], vp.selectedVidmode[1], vp.fullScreen)
