from layer import BaseLayer

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import *
from OpenGL.GL import shaders
import OpenGL

import time
import math

import numpy as np
import traceback, sys

class Layer(BaseLayer):
    def init(self):
        self.level = 0

    def render(self, runtimeData):
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)