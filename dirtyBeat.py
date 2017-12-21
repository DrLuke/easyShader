import pyaudio
import tkinter
import array
import numpy as np

import math

class AudioReader():
    def __init__(self):
        self.samplerate = 44100
        self.channels = 1
        self.framerate = 60
        self.format = pyaudio.paInt16

        self.framesize = int(self.samplerate/self.framerate)

        self.pa = pyaudio.PyAudio()

        self.stream = self.pa.open(format=self.format,
                     channels=self.channels,
                     rate=self.samplerate,
                     input=True,
                     frames_per_buffer=self.framesize)

    def read(self):
        data = self.stream.read(self.framesize)

        data = array.array("h", data)

        return data

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

class BeatDetect():
    def __init__(self):
        self.samplerate = 44100
        self.framerate = 60
        self.memlen = 20    # Amount of frames to keep in memory

        self.framesamples = int(self.samplerate/self.framerate)

        self.mem = [[0]*self.framesamples] * 20
        self.index = 0
        self.fullmem = np.zeros(self.framesamples * self.memlen)
        self.fft = np.fft.rfft(self.fullmem)
        self.fftfreqs = np.fft.rfftfreq(self.framesamples*self.memlen, 1/self.samplerate)

        self.beatEnergy = 0

    def addFrame(self, data):
        self.mem[self.index] = data
        self.index = (self.index + 1) % self.memlen

        self.fullmem = np.concatenate((self.fullmem[self.framesamples:], np.array(data)))
        self.fft = np.abs(np.fft.rfft(self.fullmem)/len(self.fullmem))

    def detectBeat(self):
        self.lowCutoff = 5
        self.upperCutoff = 20

        self.lci = np.abs(self.fftfreqs - self.lowCutoff).argmin()
        self.uci = np.abs(self.fftfreqs - self.upperCutoff).argmin()

        #print(self.fft)
        self.beatEnergy = np.sum(self.fft[self.lci:self.uci]) * ((self.uci - self.lci)/len(self.fft))


class Gui:
    def __init__(self):
        self.framerate = 60

        self.ar = AudioReader()
        self.bd = BeatDetect()

        self.root = tkinter.Tk()

        self.cw = 100
        self.ch = 300
        self.canvas = tkinter.Canvas(self.root, width=self.cw, height=self.ch, borderwidth=2)
        self.canvas.pack()

        self.cbg = self.canvas.create_rectangle(0,0, 100, 300, fill="white")
        self.clevelbar = self.canvas.create_rectangle(0, 0, self.cw, self.ch, fill="green")

        self.timerCallback()

        self.root.mainloop()

    def timerCallback(self):
        data = self.ar.read()
        self.bd.addFrame(data)
        self.bd.detectBeat()

        self.updateCanvas()

        self.root.after(1, self.timerCallback)

    def updateCanvas(self):
        energyDb = 20*math.log10(self.bd.beatEnergy+0.001)
        scale = energyDb/20. + 1.
        print(energyDb)

        self.canvas.coords(self.clevelbar, 0, 0, self.cw, int(self.ch * scale))

if __name__ == "__main__":
    Gui()

