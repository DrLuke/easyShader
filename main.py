#!/bin/python3

import glfw
import sys
import tkinter

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import *
from OpenGL.GL import shaders
import OpenGL

class Main:
    def __init__(self, monitor, vidmode, fullscreen):
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
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

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
