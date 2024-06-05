

from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("1090x720")
window.configure(bg="#5F9BC6")


canvas = Canvas(
    window,
    bg = "#5F9BC6",
    height = 720,
    width = 1090,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    545.0,
    27.0,
    image=image_image_1
)

canvas.create_rectangle(
    0.0,
    55.0,
    1090.0,
    66.0,
    fill="#000000",
    outline="")

canvas.create_text(
    59.0,
    9.0,
    anchor="nw",
    text="Welcome To Dice - A Discord Integrated Cryptographic Engine",
    fill="#FFFFFF",
    font=("MontserratRoman ExtraBold", 27 * -1)
)

canvas.create_rectangle(
    13.0,
    159.0,
    320.0,
    162.0,
    fill="#D9D9D9",
    outline="")

canvas.create_rectangle(
    13.0,
    222.0,
    320.0,
    225.0,
    fill="#D9D9D9",
    outline="")

canvas.create_rectangle(
    5.0,
    320.0,
    312.0,
    323.0,
    fill="#D9D9D9",
    outline="")

canvas.create_text(
    18.0,
    124.0,
    anchor="nw",
    text="Select File to Upload",
    fill="#FFFFFF",
    font=("MontserratRoman ExtraBold", 27 * -1)
)

canvas.create_text(
    18.0,
    187.0,
    anchor="nw",
    text="Upload Selected File",
    fill="#FFFFFF",
    font=("MontserratRoman ExtraBold", 27 * -1)
)

canvas.create_text(
    10.0,
    285.0,
    anchor="nw",
    text="Your Uploaded Files :",
    fill="#FFFFFF",
    font=("MontserratRoman ExtraBold", 27 * -1)
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat",
    activebackground="#3678B6",
    activeforeground="#3678B6"

)
button_1.place(
    x=332.0,
    y=125.0,
    width=147.0,
    height=37.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat",
    activebackground="#3678B6",
    activeforeground="#3678B6"
)
button_2.place(
    x=332.0,
    y=188.0,
    width=147.0,
    height=37.0
)


button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_5 clicked"),
    relief="flat",
    activebackground="#3678B6",
    activeforeground="#3678B6"
)
button_5.place(
    x=477.0,
    y=388.0,
    width=148.0,
    height=37.0
)

button_image_8 = PhotoImage(
    file=relative_to_assets("button_8.png"))
button_8 = Button(
    image=button_image_8,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_8 clicked"),
    relief="flat",
    activebackground="#3678B6",
    activeforeground="#3678B6"
)
button_8.place(
    x=315.0,
    y=388.0,
    width=149.0,
    height=37.0
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    33.0,
    23.0,
    image=image_image_2
)

image_image_3 = PhotoImage(
    file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    78.0,
    406.0,
    image=image_image_3
)

canvas.create_text(
    123.0,
    392.0,
    anchor="nw",
    text="File Name.txt",
    fill="#626262",
    font=("MontserratRoman SemiBold", 24 * -1)
)

window.resizable(False, False)
window.mainloop()
