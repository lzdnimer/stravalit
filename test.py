import polars as pl
from datetime import datetime

print(datetime.now())


df = pl.DataFrame({"a": [1,2,3,4,5,6]})

print(df.with_columns(b=datetime.now()))