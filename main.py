#!/bin/python3

import glfw
import sys
import tkinter
import json

import socket
from select import select
import traceback

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
        self.runtimeData.res = vidmode[0]

        glfw.window_hint(glfw.AUTO_ICONIFY, False)

        self.vidmode = vidmode
        if fullscreen:
            self.glfwWindow = glfw.create_window(vidmode[0][0], vidmode[0][1], "Pyree 3.0 Trial [EXPIRES IN 29 DAYS]", monitor, None)
        else:
            self.glfwWindow = glfw.create_window(vidmode[0][0], vidmode[0][1], "Pyree 3.0 Trial [EXPIRES IN 29 DAYS]", None, None)

        if not self.glfwWindow:
            glfw.terminate()
            print("Failed to initialize window", file=sys.stderr)
            sys.exit(1)

        glfw.make_context_current(self.glfwWindow)
        glfw.poll_events()

        glViewport(0, 0, vidmode[0][0], vidmode[0][1])

        self.runtimeData.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.runtimeData.fbo)
        self.runtimeData.fbotexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.runtimeData.fbotexture)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, vidmode[0][0], vidmode[0][1], 0, GL_RGBA, GL_UNSIGNED_BYTE, None)


        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.runtimeData.fbotexture, 0)

        while not glfw.window_should_close(self.glfwWindow):
            glfw.make_context_current(self.glfwWindow)
            glfw.poll_events()

            self.loop()

            glfw.swap_buffers(self.glfwWindow)

        glfw.terminate()

    def loop(self):
        self.pollNetwork()
        self.modman.checkNotify()

        self.runtimeData.dt = glfw.get_time() - self.runtimeData.time
        self.runtimeData.time = glfw.get_time()

        #glClearColor(0.2, 0.3, 0.3, 1.0)
        #glClear(GL_COLOR_BUFFER_BIT)

        for layer in self.modman.layersOrdered:
            try:
                if not layer.disabled:
                    layer.render(self.runtimeData)
            except Exception as exc:
                layer.disabled = True
                print(traceback.format_exc(), file=sys.stderr)
                print(exc, file=sys.stderr)

                print("\033[1m\n\033[91m*** LAYER DISABLED: %s\033[0m")


        self.runtimeData.beat = False


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

        if data["datatype"] == "beat":
            self.runtimeData.beat = True
            self.runtimeData.beataccum += 1
            self.runtimeData.bpm = data["beat"]

        if data["datatype"] == "fft":
            self.runtimeData.fft = data["fft"]

        if data["datatype"] == "uniform":
            layer = data["layer"]
            uniform = data["uniform"]
            val = data["val"]

            if not layer in self.runtimeData.uniforms:
                self.runtimeData.uniforms[layer] = {}

            self.runtimeData.uniforms[layer][uniform] = val


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

            self.lb.insert(indx, glfw.get_monitor_name(mon).decode() + " @ " + str(mode))

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
