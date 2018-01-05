import tkinter
import socket
import json
import sys



class Crudeinput():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.root = tkinter.Tk()

        self.layertv = tkinter.StringVar()
        self.layertv.trace_add("write", self.sendData)
        self.layerentry = tkinter.Entry(self.root, textvariable=self.layertv)
        self.layerentry.pack()

        self.uniformtv = tkinter.StringVar()
        self.uniformtv.trace_add("write", self.sendData)
        self.uniformentry = tkinter.Entry(self.root, textvariable=self.uniformtv)
        self.uniformentry.pack()

        self.scale = tkinter.Scale(self.root, from_=-100, length=300, to=100, orient=tkinter.HORIZONTAL, command=self.sendData)
        self.scale.pack()

        if len(sys.argv) == 3:
            self.layertv.set(sys.argv[1])
            self.uniformtv.set(sys.argv[2])

        self.root.mainloop()

    def sendData(self, *args):
        data = {
            "datatype": "uniform",
            "uniform": self.uniformtv.get(),
            "layer": self.layertv.get(),
            "val": self.scale.get()
        }

        self.root.title(self.layertv.get() + " " + self.uniformtv.get())

        if data["uniform"] and data["layer"] and data["val"]:
            self.sock.sendto(json.dumps(data).encode(), ("127.0.0.1", 31337))


if __name__ == "__main__":
    Crudeinput()
