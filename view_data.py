# inspect data json und data/data.json

import json
import pandas as pd

with open('data/data.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
print(df.info())