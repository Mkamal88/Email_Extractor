import os
import time
import threading
from tkinter import *
from tkinter import Button, Tk, HORIZONTAL
from tkinter.ttk import Progressbar
from tkinter import messagebox
from PIL import ImageTk, Image
from Email_Extractor import *

emails = "URL,Emails" + "\n"


# refer to image inside of Pyinstaller exe
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def percentageCalculator(x, y, case=1):
    if case == 1:
        r = x / 100 * y
        return r
    elif case == 2:
        r = x / y * 100
        return r
    elif case == 3:
        r = (y - x) / x * 100
        return r
    else:
        raise Exception("Only case 1,2 and 3 are available!")


def processEntry(entries):
    infoDict = {}
    for entry in entries:
        field = entry[0]
        text = entry[1].get()
        infoDict[field] = text
    return infoDict


def runActions(progress, status, emails):
    urls = list(dict.fromkeys(txt.get('1.0', END).splitlines()))
    if len("".join(urls)) == 0:
        messagebox.showerror("Warning", "Please insert at least one URL!!")
        resetValues()
    else:
        alist = range(len(urls))
        # log = open("log.txt", "a")
        try:
            p = 0
            for i in alist:
                p += 1
                unit = percentageCalculator(p, len(alist), case=2)
                step = "Working on {}".format(urls[i])
                emails += hunting(urls[i])
                progress['value'] = unit
                percent['text'] = "{}%".format(int(unit))
                status['text'] = "{}".format(step)
                window.update()

            # print(emails)
            f = open(os.path.join("Result" + ".csv"), "w+")
            f.write(emails)
            f.close()
            messagebox.showinfo('Info', "Process completed!")
            resetValues()
            # sys.exit()
        except Exception as e:
            messagebox.showinfo('Info', "ERROR: {}".format(e))
            sys.exit()


def resetValues():
    progress['value'] = 0
    percent['text'] = ""
    status['text'] = "Click button to start process.."


def endProgram():
    sys.exit()


window = Tk()
window.title("Emails Hunter")
window.geometry("600x500")
window.resizable(0, 0)

# background_image = PhotoImage(resource_path("spiders-web.jpg"))
# background_label = Label(window, image=background_image)
# background_label.place(x=0, y=0, relwidth=1, relheight=1)
# background_label.pack()

top_frame = Frame(window).pack()

# create a Frame for the Text and Scrollbar
txt_frm = Frame(window, width=600, height=200)
txt_frm.pack(fill="both", expand=False)

# ensure a consistent GUI size
txt_frm.grid_propagate(False)
# implement stretchability
txt_frm.grid_rowconfigure(0, weight=1)
txt_frm.grid_columnconfigure(0, weight=1)

# create a Text widget
txt = Text(txt_frm, borderwidth=3, relief="sunken")
txt.config(font=("consolas", 12), undo=True, wrap='word')
txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)


# create a Scrollbar and associate it with txt
scrollb = Scrollbar(txt_frm, command=txt.yview)
scrollb.grid(row=0, column=1, sticky='nsew')
txt['yscrollcommand'] = scrollb.set

runButton = Button(window, text='Start Hunting', command=lambda: runActions(progress, status, emails))
percent = Label(window, text="", anchor=S)
progress = Progressbar(window, length=500, mode='determinate')
status = Label(window, text="Click button to start process..", relief=SUNKEN, anchor=W, bd=2)
runButton.pack(pady=15)
percent.pack()
progress.pack()
status.pack(side=BOTTOM, fill=X)
window.iconbitmap(resource_path("spider.ico"))
window.mainloop()
