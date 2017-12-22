import pyaudio
import tkinter
import array
import numpy as np
import socket
import json
import time

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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.samplerate = 44100
        self.framerate = 60
        self.memlen = 60    # Amount of frames to keep in memory

        self.framesamples = int(self.samplerate/self.framerate)

        self.mem = [[0]*self.framesamples] * self.memlen
        self.index = 0
        self.fullmem = np.zeros(self.framesamples * self.memlen)
        self.fft = np.fft.rfft(self.fullmem)
        self.fftfreqs = np.fft.rfftfreq(self.framesamples*self.memlen, 1/self.samplerate)

        self.beatEnergy = 0
        self.beatEnergyDb = -60

        # Moving Average
        self.meanLen = 10   # In Seconds
        self.meanSamples = [-20] * (self.meanLen * self.framerate)
        self.meanIndex = 0
        self.meanEnergy = 0
        self.minimumMean = -20

        # PT1 with different time constants for when the difference is positive or negative
        self.maxEnergy = 0
        self.aboveMaxT = 0.1
        self.belowMaxT = 15

        # Beat detection state
        self.triggerLevel = 0
        self.resetLevel = -40
        self.trigd = False
        self.bpmmem = []
        self.bpm = 0

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

        self.beatEnergy = np.sum(self.fft[self.lci:self.uci]) * ((self.uci - self.lci)/len(self.fft))
        self.beatEnergyDb = 20*math.log10(self.beatEnergy + 1E-6)

        # Moving Average
        self.meanSamples[self.meanIndex] = max(self.beatEnergyDb, self.minimumMean)
        self.meanIndex = (self.meanIndex + 1) % len(self.meanSamples)

        self.meanEnergy = 0
        for i in range(len(self.meanSamples)):
            self.meanEnergy += self.meanSamples[i]
        self.meanEnergy /= len(self.meanSamples)
        self.meanEnergy = max(self.meanEnergy, self.minimumMean)

        # PT1 for max level
        if self.beatEnergyDb > self.maxEnergy:
            self.maxEnergy += (self.beatEnergyDb - self.maxEnergy)/self.aboveMaxT * (1/self.framerate)
        else:
            self.maxEnergy += (self.beatEnergyDb - self.maxEnergy) / self.belowMaxT * (1/self.framerate)

        # Beat detection algorithm
        #
        # Uses hysteresis to determine a beat. If the signal level raises above 80%
        # of the difference between the max and mean level, a beat is triggered.
        # Before a beat can be triggered again, the level has to fall below 10% first.
        self.triggerLevel = self.meanEnergy + (self.maxEnergy - self.meanEnergy) * 1.0
        self.resetLevel = self.meanEnergy + (self.maxEnergy - self.meanEnergy) * 0.2
        if not self.trigd:
            if self.beatEnergyDb > self.triggerLevel:
                self.trigd = True
                self.bpmmem.append(time.time())
                self.bpmmem = [x for x in self.bpmmem if (time.time()-x < 60)]
                self.bpm = len(self.bpmmem)

                self.sendBeat()
        else:
            if self.beatEnergyDb < self.resetLevel:
                self.trigd = False

        self.sendFFT()

    def sendBeat(self):
        data = {
            "datatype": "beat",
            "beat": self.bpm
        }

        self.sock.sendto(json.dumps(data).encode(), ("127.0.0.1", 31337))

    def sendFFT(self):
        reducedfft = np.interp(np.linspace(0, 10000, 512), self.fftfreqs, self.fft)

        data = {
            "datatype": "fft",
            "fft": list(reducedfft)
        }

        self.sock.sendto(json.dumps(data).encode(), ("127.0.0.1", 31337))


class Gui:
    def __init__(self):
        self.framerate = 60

        self.ar = AudioReader()
        self.bd = BeatDetect()

        self.root = tkinter.Tk()

        # Canvas
        self.cw = 100
        self.ch = 300
        self.canvas = tkinter.Canvas(self.root, width=self.cw, height=self.ch, borderwidth=2)
        self.canvas.pack()

        self.cbg = self.canvas.create_rectangle(0,0, 100, 300, fill="white")
        self.clevelbar = self.canvas.create_rectangle(0, 0, self.cw, self.ch, fill="green")
        self.clevelmem = -40
        self.cleveltconst = 0.05
        self.maxLine = self.canvas.create_line(0,0,0,0, fill="red")
        self.meanLine = self.canvas.create_line(0,0,0,0, fill="black")
        self.threshLine = self.canvas.create_line(0,0,0,0, fill="blue")
        # /Canvas

        # Controls

        # /Control

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

        def dbtopos(db):
            return self.ch - self.ch*(db/20 +1)

        self.clevelmem += (energyDb - self.clevelmem) / self.cleveltconst * (1/self.framerate)
        self.canvas.coords(self.clevelbar, 0, self.ch, self.cw, dbtopos(self.clevelmem))
        self.canvas.coords(self.maxLine, 0, dbtopos(self.bd.maxEnergy), self.cw, dbtopos(self.bd.maxEnergy))
        self.canvas.coords(self.meanLine, 0, dbtopos(self.bd.meanEnergy), self.cw, dbtopos(self.bd.meanEnergy))

        self.canvas.itemconfig(self.cbg, fill="white")
        if self.bd.trigd:
            self.canvas.itemconfig(self.cbg, fill="blue")

if __name__ == "__main__":
    Gui()

