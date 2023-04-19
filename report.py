import json
import pandas as pd


def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024


db = open("db.txt", "r")
db_data = db.read().replace("\'", "\"")
if db_data == "":
    db_data = "{}"
loaded_data = json.loads(db_data)
db.close()

data = []
for user in loaded_data.keys():
    d = loaded_data[user]
    data.append(d)

df = pd.DataFrame(data)
df["download"] = df["download"].apply(lambda x: get_size(x))
df["upload"] = df["upload"].apply(lambda x: get_size(x))


print(df.to_string(index=False))
