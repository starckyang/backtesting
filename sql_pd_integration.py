from sqlalchemy import create_engine, Table, Column, Integer, String, DATETIME, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select, delete
import pandas as pd

engine = create_engine("sqlite:///C:\\Users\\Starck\\PycharmProjects\\trading_class"
                       "\\Machine-Learning-for-Algorithmic-Trading-Bots-with-Python"
                       "\\Eclipse Projects\\stock.db", echo=True)
metadata = MetaData()
trial = Table("trial", metadata,
              Column("attempts", Integer, primary_key=True))
metadata.create_all(engine)
conn = engine.connect()
delete_query = delete(trial)
conn.execute(delete_query)
conn.commit()

df = pd.read_sql("SELECT * FROM trial", engine)
additional_data = [i for i in range(30)]
df2 = pd.DataFrame(additional_data, columns=["attempts"])
new_df = pd.concat([df, df2])
df2.to_sql("trial",  engine, index=False, if_exists="append")

select_query = select(trial).where(trial.c.attempts <= 100)
for rows in conn.execute(select_query):
    print(rows)