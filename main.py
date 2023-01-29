import psutil
import time
import os
import subprocess
import pandas as pd

UPDATE_DELAY = 10

def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024


io = psutil.net_io_counters(pernic=True)

while True:

    time.sleep(UPDATE_DELAY)
    userList = {}
    for userData in subprocess.check_output("who", shell=True).decode("utf-8").split("\n"):
        if userData != "":
            user = userData.split()[0]
            int = userData.split()[1]
            userList[int] = user

    io_2 = psutil.net_io_counters(pernic=True)
    data = []

    for iface, iface_io in io.items():
        if iface in io_2.keys():
            upload_speed, download_speed = io_2[iface].bytes_sent - iface_io.bytes_sent, io_2[iface].bytes_recv - iface_io.bytes_recv
            if iface in userList.keys():
                ifaceName = userList[iface]
                ifDownload = get_size(io_2[iface].bytes_sent)
                ifUpload = get_size(io_2[iface].bytes_recv)
                ifDownloadSpeed = f"{get_size(upload_speed / UPDATE_DELAY)}/s"
                ifUploadSpeed = f"{get_size(download_speed / UPDATE_DELAY)}/s"
            else:
                ifaceName = iface
                ifDownload = get_size(io_2[iface].bytes_recv)
                ifUpload = get_size(io_2[iface].bytes_sent)
                ifDownloadSpeed = f"{get_size(download_speed / UPDATE_DELAY)}/s"
                ifUploadSpeed = f"{get_size(upload_speed / UPDATE_DELAY)}/s"
            data.append({
                "iface": ifaceName,
                "Download": ifDownload,
                "Upload": ifUpload,
                "Download Speed": ifDownloadSpeed,
                "Upload Speed": ifUploadSpeed,
            })

    io = io_2
    df = pd.DataFrame(data)
    df.sort_values("Download Speed", inplace=True, ascending=False)
    os.system("clear")
    print(df.to_string())
