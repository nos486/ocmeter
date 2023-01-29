import psutil
import time
import os
import pandas as pd
from datetime import datetime

UPDATE_DELAY = 5


def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024


def get_time_string(timestamp):
    if timestamp == 0:
        return "-"
    else:
        return datetime.fromtimestamp(timestamp)


def get_users():
    users = {}
    for user in psutil.users():
        users[user.terminal] = {
            "name": user.name,
            "interface": user.terminal,
            "host": user.host.replace("::ffff:", ""),  # for ipv4 display
            "started": user.started
        }

    return users


io = psutil.net_io_counters(pernic=True)

while True:
    time.sleep(UPDATE_DELAY)
    userList = get_users()

    io_2 = psutil.net_io_counters(pernic=True)
    data = []

    for iface, iface_io in io.items():
        if iface in io_2.keys():
            upload_speed, download_speed = io_2[iface].bytes_sent - iface_io.bytes_sent, io_2[iface].bytes_recv - iface_io.bytes_recv
            if iface in userList.keys():
                user = userList[iface]["name"]
                iface = userList[iface]["interface"]
                ifDownload = io_2[iface].bytes_sent
                ifUpload = io_2[iface].bytes_recv
                ifDownloadSpeed = upload_speed / UPDATE_DELAY
                ifUploadSpeed = download_speed / UPDATE_DELAY
                host = userList[iface]["host"]
                started = userList[iface]["started"]
            else:
                user = "-"
                iface = iface
                ifDownload = io_2[iface].bytes_recv
                ifUpload = io_2[iface].bytes_sent
                ifDownloadSpeed = download_speed / UPDATE_DELAY
                ifUploadSpeed = upload_speed / UPDATE_DELAY
                host = "local"
                started = 0

            isExist = False
            for row in data:
                if row["user"] == user:
                    row["Connection"] += 1
                    row["Download"] += ifDownload
                    row["Upload"] += ifUpload
                    row["Download Speed"] += ifDownloadSpeed
                    row["Upload Speed"] += ifUploadSpeed
                    row["Hosts"] += " " + host
                    if row["Started"] < started:
                        row["Started"] = started

                    isExist = True
                    pass
            if not isExist:
                data.append({
                    "user": user,
                    "iface": iface,
                    "Connection": 1,
                    "Download": ifDownload,
                    "Upload": ifUpload,
                    "Download Speed": ifDownloadSpeed,
                    "Upload Speed": ifUploadSpeed,
                    "Hosts": host,
                    "Started": started
                })

    io = io_2
    df = pd.DataFrame(data)
    df.sort_values("Download Speed", inplace=True, ascending=False)
    df["Download"] = df["Download"].apply(lambda x: get_size(x))
    df["Upload"] = df["Upload"].apply(lambda x: get_size(x))
    df["Download Speed"] = df["Download Speed"].apply(lambda x: get_size(x))
    df["Upload Speed"] = df["Upload Speed"].apply(lambda x: get_size(x))
    df["Started"] = df["Started"].apply(lambda x: get_time_string(x))

    os.system("clear")
    print(df.to_string())
