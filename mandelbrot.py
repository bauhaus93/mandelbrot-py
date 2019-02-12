import colorsys
import math
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
from multiprocessing import Pool

class Mandelbrot:

    def __init__(self, center, width, height, step, check_depth = 20):
        self.center = center
        self.width = width
        self.height = height
        self.half_width = int(self.width / 2)
        self.half_height = int(self.height / 2)
        self.step = step
        self.check_depth = check_depth
        self.pool = Pool(processes = 2)

    def print_info(self):
        print("center = {}, step = {}, check_depth = {}".format(self.center, self.step, self.check_depth))

    def move_center(self, offset):
        self.center += offset

    def mod_step(self, factor):
        self.step *= factor

    def update_check_depth(self):
        self.check_depth = max(20, int(math.log(1. / self.step, 2) * 4))

    def create_pixel_array(self):
        complex_list = list()
        for y in range(-self.half_height, self.half_height):
            for x in range(-self.half_width, self.half_width):
                c = complex(self.center.real + x * self.step,
                            self.center.imag + y * self.step)
                complex_list.append((c, self.check_depth))
        results = self.pool.map_async(get_color, complex_list)
        pixels = results.get()
        expanded_pixels = np.empty(shape = (3 * len(pixels),), dtype = np.uint8)
        for (i, pixel) in enumerate(pixels):
            expanded_pixels[3 * i:3 * (i + 1)] = pixel
        return expanded_pixels

    def create_image(self):
        pix_array = self.create_pixel_array()
        return Image.frombytes(mode = 'RGB', size = (self.width, self.height), data = pix_array)

def get_color(cn):
    res = check_mandelbrot(cn[0], cn[1])
    if res < 0:
        return np.zeros((1, 3), dtype = np.uint8)
    else:
        rgb = colorsys.hsv_to_rgb(h = res / cn[1], s = .8, v = .8)
        rgb = [int(0xFF * c) for c in rgb]
        rgb = np.array(rgb, dtype = np.uint8)
        return rgb

def check_mandelbrot(c, n):
    z = 0
    for i in range(n):
        z = z**2 + c
        if abs(z) >= 2:
            return i
    return -1

class Application(tk.Frame):
    def __init__(self, mandelbrot, master = None):
        super().__init__(master)
        self.mandelbrot = mandelbrot
        self.master = master
        self.pack()
        self.canvas = tk.Canvas(self, width = 800, height = 600)
        self.canvas.pack()
        self.canvas

    def update_image(self):
        self.image = ImageTk.PhotoImage(self.mandelbrot.create_image())
        self.canvas.create_image(800 / 2, 600 / 2, image = self.image)
        self.mandelbrot.print_info()
        self.mandelbrot.mod_step(0.7)
        self.mandelbrot.update_check_depth()
        self.master.after(100, self.update_image)

#mb = Mandelbrot(complex(0., 0.), 1366, 768, 0.003, 50)
#img = mb.create_image()
#img.save("mandelbrot.png")
mb = Mandelbrot(complex(-0.77568377, 0.13646737), 100, 100, 0.05)
root = tk.Tk()
app = Application(mb, root)
app.update_image()
app.mainloop()
