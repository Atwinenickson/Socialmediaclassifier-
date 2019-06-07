import pickle
import sqlite3
import numpy as np
import os
from modell import final_transformer
import pandas as pd


def update_model(db_path, model, batch_size=100):
    conn = sqlite3.connect("sample_db.sqlite")
    query = "SELECT * FROM sent;"
    results = pd.read_sql_query(query, conn)
    df = results.drop('Sentiment', axis=1)
    y = results['Sentiment']
    X_train = final_transformer.transform(df)
    clf.fit(X_train, y, sample_weight=None)

    conn.close()
    return None


cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir, 'finall_modell.sav'), 'rb'))
db = os.path.join(cur_dir, 'sample_db.sqlite')
update_model(db_path=db, model=clf, batch_size=100)
