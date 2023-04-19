import psutil
import time
import json
from datetime import datetime

UPDATE_DELAY = 10


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
            "host": user.host.replace("::ffff:", "") if user.host != None else "",  # for ipv4 display
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
                    row["connection"] += 1
                    row["download"] += ifDownload
                    row["upload"] += ifUpload
                    row["download_speed"] += ifDownloadSpeed
                    row["upload_speed"] += ifUploadSpeed
                    if host not in row["hosts"].split(", "):
                        row["hosts"] += ", " + host
                    if row["started"] < started:
                        row["started"] = started
                    isExist = True
                    pass
            if not isExist:
                data.append({
                    "user": user,
                    "iface": iface,
                    "connection": 1,
                    "download": ifDownload,
                    "upload": ifUpload,
                    "download_speed": ifDownloadSpeed,
                    "upload_speed": ifUploadSpeed,
                    "hosts": host,
                    "started": started,
                })

    io = io_2

    db = open("db.txt", "r")
    db_data = db.read().replace("\'", "\"")
    if db_data == "":
        db_data = "{}"
    loaded_data = json.loads(db_data)
    db.close()

    db = open("db.txt", "w")
    db_json = {}

    for user in loaded_data.keys():
        user_exist = False
        for j in data:
            if user == j["user"]:
                user_exist = True
                if loaded_data[user]["connected"] != "True":
                    loaded_data[user]["connected"] = "True"
                    loaded_data[user]["back_online"] = "True"
                    loaded_data[user]["last_connection"] = ""
        if not user_exist:
            loaded_data[user]["connected"] = "False"
            loaded_data[user]["last_connection"] = str(datetime.now())
            loaded_data[user]["back_online"] = "False"

    for row in data:
        if row["user"] in loaded_data:
            if loaded_data[row["user"]]["back_online"] == "True":
                loaded_data[row["user"]]["download"] = row["download"] + loaded_data[row["user"]]["download"]
                loaded_data[row["user"]]["upload"] = row["upload"] + loaded_data[row["user"]]["upload"]

                loaded_data[row["user"]]["back_online"] = "False"
            else:
                loaded_data[row["user"]]["download"] = row["download"]
                loaded_data[row["user"]]["upload"] = row["upload"]
        else:
            loaded_data[row["user"]] = {"user": row["user"], "download": row["download"], "upload": row["upload"], "connected": "True", "back_online": "False", "last_connection": ""}

    old_loaded_data = loaded_data
    db.write(str(loaded_data))
    db.close()

