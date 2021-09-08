import time
import _thread

from tkinter import Tk
from tkinter import Button
from tkinter import Label
from tkinter import StringVar

from PIL import ImageGrab
from PIL import ImageChops
from datetime import datetime

g_text = None
g_exit = None
g_button = None

# detect the wechat window
# copied from https://blog.csdn.net/fujliny/article/details/109411343
def captureWCWindow():
    img = ImageGrab.grab()
    width = img.size[0]
    height = img.size[1]
    imgData = img.getdata()

    upPixIndex = -1
    downPixIndex = -1

    scanLineCount = 6
    for i in range(scanLineCount):
        for j in range(height):
            pixIndex = j * width + i * int(width / (scanLineCount + 1))
            try:
                if upPixIndex < 0 and imgData[pixIndex] == (231, 231, 231):
                    if imgData[pixIndex - width] == (245, 245, 245) and imgData[pixIndex + width] == (245, 245, 245):
                        for long in range(1, 21):
                            if imgData[pixIndex + long] != (231, 231, 231):
                                break
                        else:
                            upPixIndex = pixIndex

                elif downPixIndex < 0 and imgData[pixIndex] == (236, 236, 236):
                    if imgData[pixIndex - width] == (245, 245, 245) and imgData[pixIndex + width] in ((245, 245, 245), (255, 255, 255)):
                        for long in range(1, 21):
                            if imgData[pixIndex + long] != (236, 236, 236):
                                break
                        else:
                            downPixIndex = pixIndex

            except IndexError:
                return None

    if upPixIndex < 0 or downPixIndex < 0:
        return None

    upPixStartIndex   = upPixIndex
    upPixEndIndex     = upPixIndex

    while imgData[upPixStartIndex - 1] == (231, 231, 231):
        upPixStartIndex = upPixStartIndex - 1

    while imgData[upPixEndIndex + 1] == (231, 231, 231):
        upPixEndIndex = upPixEndIndex + 1

    downPixStartIndex = downPixIndex
    downPixEndIndex   = downPixIndex

    while imgData[downPixStartIndex - 1] == (231, 231, 231):
        downPixStartIndex = downPixStartIndex - 1

    while imgData[downPixEndIndex + 1] == (236, 236, 236):
        downPixEndIndex = downPixEndIndex + 1

    return img.crop((upPixStartIndex % width, upPixStartIndex // width, downPixEndIndex % width, downPixEndIndex // width))


def captureLoop():
    global g_text
    global g_exit
    global g_button

    lastImg = None
    currImg = None

    g_exit = False
    g_button.config(text='stop')

    while not g_exit:
        try:
            currImg = captureWCWindow()
            if lastImg is None or currImg is None:
                # didn't get anything
                g_text.set("No wc window detected")
            else:
                diff = ImageChops.difference(lastImg, currImg)
                if diff.getbbox():
                    labelValue = datetime.now().strftime("wcspy.%d.%m.%Y.%H.%M.%S.%f.jpg")
                    g_text.set('Saved: ' + labelValue)
                    currImg.save(labelValue)
                else:
                    g_text.set("Window content not changed")

        except:
            # mute any error
            # don't stop the program anyway
            pass

        lastImg = currImg
        time.sleep(0.1)

    g_exit = None
    g_text.set("inactive")
    g_button.config(text='start')


def buttonCallback():
    global g_text
    global g_exit
    global g_button

    if g_exit is None or g_exit is True:
        g_exit = False
        _thread.start_new_thread(captureLoop, ())
    else:
        g_exit = True


def main():
    global g_text
    global g_exit
    global g_button

    top = Tk()
    top.geometry("400x100")

    g_text = StringVar()
    g_text.set("inactive")

    g_button = Button(top, text="start", command=buttonCallback)
    g_button.place(x=0, y=0)

    label = Label(top, textvariable=g_text)
    label.pack()

    top.mainloop()


if __name__ == '__main__':
    main()