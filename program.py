import collections
import os
import threading
import time
import tkinter as tk
from tkinter import ttk
import serial


# ThreadedBluetooth is an object which is a thread
# containing the management of Bluetooth, sends it,
# reception, recording of events and event calls
class ThreadedBluetooth(threading.Thread):
    handlers = None

    def __init__(self, p):
        threading.Thread.__init__(self)
        bl = serial.Serial(p, 9600)
        bl.flushInput()
        self.bl = bl
        self.handlers = collections.defaultdict(set)

    # method when thread was started
    def run(self):
        # loop for reading line from bluetooth
        while True:
            data = self.bl.readline()
            val = data.decode()
            if "=" in val:
                new_val = val.replace("\n", "")
                split = new_val.split("=")
                print(new_val)
                if len(split) == 2:
                    self.fire(split[0], split[1])
            time.sleep(0.1)

    # send a message to bluetooth
    def send(self, message):
        print(message)
        self.bl.write(str.encode(str(message)))

    # register an event with prefix message
    # like prefix=value
    def register(self, prefix, callback):
        self.handlers[prefix].add(callback)

    # try to call registered events
    def fire(self, prefix, value):
        for handler in self.handlers.get(prefix, []):
            handler(value)


# generate a basic window for this app
def generate_window():
    window = tk.Tk()

    window.title("Domotique")
    window.geometry("250x600")
    window.minsize(250, 600)
    window.resizable(height=None, width=None)
    photo = tk.PhotoImage(file="icon.png")
    window.iconphoto(False, photo)
    return window


# callback when value was updated from arduino to this
def on_scale_lum_moved(e):
    global bluetooth
    global scale_lum_mode
    value = int(scale_lum_mode.get())
    bluetooth.send(f"l={value}")


# callback when value was updated from arduino to this
def on_scale_temp_moved(e):
    global bluetooth
    global scale_temp_mode
    value = int(scale_temp_mode.get())
    bluetooth.send(f"t={value}")


# callback when value was updated from arduino to this
def on_scale_alarm_moved(e):
    global bluetooth
    global scale_alarm_mode
    value = int(scale_alarm_mode.get())
    bluetooth.send(f"a={value}")


# callback when value was updated from arduino to this
def callback_hum_ext(value):
    global string_var_hum_ext
    string_var_hum_ext.set(str(value))


# callback when value was updated from arduino to this
def callback_lum_ext(value):
    global string_var_lum_ext
    val = str(value)
    string_var_lum_ext.set(f"{val}%")


# callback when value was updated from arduino to this
def callback_temp_ext(value):
    global string_var_temp_ext
    string_var_temp_ext.set(str(value))


# callback when value was updated from arduino to this
def callback_temp_int(value):
    global string_var_temp_int
    string_var_temp_int.set(str(value))


# callback when value was updated from arduino to this
def callback_anenometer(value):
    global string_var_anenometer
    string_var_anenometer.set(str(value))


# callback when value was updated from arduino to this
def callback_hum_int(value):
    global string_var_hum_int
    string_var_hum_int.set(str(value))


# callback when value was updated from arduino to this
def callback_presence_int(value):
    global string_var_presence_int
    string_var_presence_int.set(str(value))


# callback when value was updated from arduino to this
def callback_presence_ext(value):
    global string_var_presence_ext
    string_var_presence_ext.set(str(value))


# callback when value was updated from arduino to this
def callback_gaz(value):
    global string_var_gaz
    string_var_gaz.set(str(value))


# display the controller, and bluetooth interaction
def display_controller():
    print("switch to controller")
    global port
    global window
    global bluetooth

    global scale_lum_mode
    global scale_temp_mode
    global scale_alarm_mode
    global scale_seuil

    global string_var_hum_ext
    global string_var_lum_ext
    global string_var_temp_ext
    global string_var_temp_int
    global string_var_anenometer
    global string_var_hum_int
    global string_var_presence_ext
    global string_var_presence_int
    global string_var_gaz

    # instantiation of ThreadedBluetooth with selected port in constructor
    bluetooth = ThreadedBluetooth(port)
    print("bluetooth connected")

    window = generate_window()
    frame = ttk.Frame(window)
    frame.pack(expand=1)

    # luminosity mode section
    ttk.Label(frame, text="Luminosité mode").pack()
    scale_lum_mode = ttk.Scale(frame, from_=0, to=2, command=on_scale_lum_moved)
    scale_lum_mode.pack()

    # temperature mode section
    ttk.Label(frame, text="Température mode").pack()
    scale_temp_mode = ttk.Scale(frame, from_=0, to=2, command=on_scale_temp_moved)
    scale_temp_mode.pack()

    # alarm mode section
    ttk.Label(frame, text="Alarm mode").pack()
    scale_alarm_mode = ttk.Scale(frame, from_=0, to=1, command=on_scale_alarm_moved)
    scale_alarm_mode.pack()

    # indoor temperature section
    ttk.Label(frame, text="Température intérieur (°C)").pack()
    string_var_temp_int = tk.StringVar()
    string_var_temp_int.set("0")
    ttk.Label(frame, textvariable=string_var_temp_int).pack()
    bluetooth.register("tempi", callback_temp_int)

    # exterior temperature section
    ttk.Label(frame, text="Température extérieur (°C)").pack()
    string_var_temp_ext = tk.StringVar()
    string_var_temp_ext.set("0")
    ttk.Label(frame, textvariable=string_var_temp_ext).pack()
    bluetooth.register("tempe", callback_temp_ext)

    # indoor humidity section
    ttk.Label(frame, text="Humidité intérieur (%)").pack()
    string_var_hum_int = tk.StringVar()
    string_var_hum_int.set("0")
    ttk.Label(frame, textvariable=string_var_hum_int).pack()
    bluetooth.register("humi", callback_hum_int)

    # exterior humidity section
    ttk.Label(frame, text="Humidité extérieur (%)").pack()
    string_var_hum_ext = tk.StringVar()
    string_var_hum_ext.set("0")
    ttk.Label(frame, textvariable=string_var_hum_ext).pack()
    bluetooth.register("hume", callback_hum_ext)

    # indoor presence section
    ttk.Label(frame, text="Présence intérieur").pack()
    string_var_presence_int = tk.StringVar()
    string_var_presence_int.set("0")
    ttk.Label(frame, textvariable=string_var_presence_int).pack()
    bluetooth.register("presi", callback_presence_int)

    # exterior presence section
    ttk.Label(frame, text="Présence extérieur").pack()
    string_var_presence_ext = tk.StringVar()
    string_var_presence_ext.set("0")
    ttk.Label(frame, textvariable=string_var_presence_ext).pack()
    bluetooth.register("prese", callback_presence_ext)

    # exterior luminosity section
    ttk.Label(frame, text="Luminosité extérieur").pack()
    string_var_lum_ext = tk.StringVar()
    string_var_lum_ext.set("0")
    ttk.Label(frame, textvariable=string_var_lum_ext).pack()
    bluetooth.register("lume", callback_lum_ext)

    # anenometer section
    ttk.Label(frame, text="Anénomètre").pack()
    string_var_anenometer = tk.StringVar()
    string_var_anenometer.set("0")
    ttk.Label(frame, textvariable=string_var_anenometer).pack()
    bluetooth.register("ane", callback_anenometer)

    # gaz section
    ttk.Label(frame, text="Gaz").pack()
    string_var_gaz = tk.StringVar()
    string_var_gaz.set("0")
    ttk.Label(frame, textvariable=string_var_gaz).pack()
    bluetooth.register("gazi", callback_gaz)

    # starting thread of ThreadedBluetooth object
    bluetooth.start()
    window.mainloop()


# event when confirm button was clicked
def on_confirm_button_clicked():
    global window
    global combobox
    global port
    # get the value from combobox
    port = combobox.get()
    # destroy window
    window.quit()
    display_controller()


# display the serial selector
def display_serial_selector():
    print("switch to selector serial")
    global window
    global combobox
    window = generate_window()

    serial_port_names = []

    if os.name == "posix" or os.name == "linux" or os.name == "macos":
        # linux / macos / unix...
        for f in os.listdir("/dev/"):
            if f.startswith("tty."):
                serial_port_names.append(f"/dev/{f}")

        for f in serial_port_names:
            print(f)
    else:
        # windows
        pass

    # creation of the frame for selector serials
    frame = ttk.Frame(window)

    # creation of combobox which contains the port series
    combobox = ttk.Combobox(frame, values=serial_port_names)
    combobox.current(0)
    combobox.pack()

    # creation of button for confirm serial port
    confirm_button = ttk.Button(frame, text="Confirm", command=on_confirm_button_clicked)
    confirm_button.pack()
    frame.pack(expand=1)
    window.mainloop()


if __name__ == "__main__":
    display_serial_selector()
