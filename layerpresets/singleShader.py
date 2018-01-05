from layer import BaseLayer, FileWatch

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
        self.level = 10

        self.vao = None
        self.vbo = None

        self.fragShader = None
        self.vertShader = None
        self.shaderProg = None

        self.fragCode = None

        self.path = ""

        self.init2()

        self.fw = FileWatch("glsl/testshader.glsl")

    def init2(self):
        pass

    def render(self, runtimeData):
        if self.vao is None or self.vbo is None:
            self.genVAOVBO()

        if self.fragShader is None or self.vertShader is None or self.shaderProg is None:
            self.genShaders(self.fw.content)

        if self.fw.check():
            self.genShaders(self.fw.content)

        glBindFramebuffer(GL_FRAMEBUFFER, runtimeData.fbo)

        glUseProgram(self.shaderProg)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, runtimeData.fbotexture)
        glUniform1i(glGetUniformLocation(self.shaderProg, "texIn"), 0)

        self.u1("time", runtimeData.time)
        self.u1("dt", runtimeData.dt)
        self.u2("res", runtimeData.res)

        self.render2(runtimeData)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

    def render2(self, runtimeData):
        pass

    def getData(self):
        data = {
            "vao": self.vao,
            "vbo": self.vbo,
            "vs": self.vertShader,
            "fs": self.fragShader,
            "sp": self.shaderProg,
            "fc": self.fragCode
        }
        return data

    def setData(self, data):
        self.vao = data["vao"]
        self.vbo = data["vbo"]
        self.vertShader = data["vs"]
        self.fragShader = data["fs"]
        self.shaderProg = data["sp"]
        self.fragCode = data["fc"]

    def genVAOVBO(self):
        vertices = np.array([
            # X     Y     Z    R    G    B    U    V
            [1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0],  # Top right
            [-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0, 1.0],  # Top Left
            [1.0, -1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0],  # Bottom Right
            [-1.0, -1.0, 0.0, 1.0, 1.0, 0.0, 0, 0],  # Bottom Left
            [1.0, -1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0],  # Bottom Right
            [-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0, 1.0]  # Top Left
        ], 'f')

        # Generate vertex buffer object and fill it with vertex data from above
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Generate vertex array object and pass vertex data into it
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # XYZ
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, None)
        glEnableVertexAttribArray(0)

        # RGB
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
        glEnableVertexAttribArray(1)

        # UV
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(6 * vertices.itemsize))
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def genShaders(self, fragCode):
        defaultVertexShaderCode = """
        #version 130
        in vec3 position;
        in vec3 color;
        in vec2 texcoord;
        out vec3 ourColor;
        out vec2 ourTexcoord;
        void main()
        {
            gl_Position = vec4(position.x, position.y, position.z, 1.0);
            ourColor = color;
            ourTexcoord = texcoord;
        }"""

        defaultFragmentShaderCode = """
        #version 130
        in vec3 ourColor;
        in vec2 ourTexcoord;
        out vec4 outColor;
        void main()
        {
            outColor = vec4(ourColor.r, ourColor.g, ourColor.b, 1.0);
        }"""

        if self.fragCode is None:
            self.fragCode = defaultFragmentShaderCode

        try:
            self.fragShader = shaders.compileShader(fragCode, GL_FRAGMENT_SHADER)
            self.fragCode = fragCode
        except:
            print(traceback.print_exc(), file=sys.stderr)
            # recompile OLD shadercode, but throw error aswell
            self.fragShader = shaders.compileShader(self.fragCode, GL_FRAGMENT_SHADER)

        self.vertShader = shaders.compileShader(defaultVertexShaderCode, GL_VERTEX_SHADER)

        self.shaderProg = shaders.compileProgram(self.fragShader, self.vertShader)

    def u1(self, name, v):
        uniformLoc = glGetUniformLocation(self.shaderProg, name)
        if not uniformLoc == -1:
            glUniform1f(uniformLoc, v)

    def u2(self, name, v):
        uniformLoc = glGetUniformLocation(self.shaderProg, name)
        if not uniformLoc == -1:
            glUniform2f(uniformLoc, v[0], v[1])

    def u3(self, name, v):
        uniformLoc = glGetUniformLocation(self.shaderProg, name)
        if not uniformLoc == -1:
            glUniform3f(uniformLoc, v[0], v[1], v[2])

    def u4(self, name, v):
        uniformLoc = glGetUniformLocation(self.shaderProg, name)
        if not uniformLoc == -1:
            glUniform4f(uniformLoc, v[0], v[1], v[2], v[3])

