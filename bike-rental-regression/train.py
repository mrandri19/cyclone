import argparse
import os
from argparse import Namespace

import mlflow
import pandas as pd
import sqlalchemy
from sklearn.ensemble import HistGradientBoostingRegressor as Model
from sklearn.metrics import r2_score
from sqlalchemy import Column, Integer, JSON, Text, TIMESTAMP
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Prediction(Base):
    __tablename__ = "prediction"
    id = Column(Integer(), primary_key=True)
    input = Column(JSON())
    prediction = Column(JSON())
    model_id = Column(Text())
    label = Column(JSON())
    created_at = Column(TIMESTAMP(timezone=True))


def time_features(input_df):
    return input_df.assign(
        month=lambda df: df.index.month,
        day=lambda df: df.index.day,
        hour=lambda df: df.index.hour,
    )


def main(params: Namespace, db_uri):
    print(db_uri)

    engine = create_engine(db_uri)

    query = f"""
        select *
        from prediction
        order by created_at desc
        limit {params.num_train + params.num_test}
    """

    df = pd.read_sql(query, con=engine)
    df = pd.concat([pd.DataFrame(df['input'].tolist()), df['label']], axis=1)

    test = df.iloc[:params.num_test]
    train = df.iloc[params.num_test:(params.num_test+params.num_train)]

    with mlflow.start_run():
        # Instantiate model
        model = Model()
        mlflow.set_tag("model_module", model.__class__.__module__)
        mlflow.set_tag("model_type", model.__class__.__name__)
        mlflow.log_param("num_train", params.num_train)
        mlflow.log_param("num_test", params.num_test)

        # Train model
        model.fit(train.drop(columns='label'), train['label'])

        # Test model
        score = r2_score(
            test['label'],
            model.predict(test.drop(columns='label'))
        )
        mlflow.log_metric('test_r2_score', score)

        # Register trained model
        input_example = train.head(10).drop(columns='label')
        signature = mlflow.models.signature.infer_signature(
            input_example, model.predict(input_example)
        )
        mlflow.sklearn.log_model(
            model, "model", signature=signature, input_example=input_example)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('num_train', type=int)
    parser.add_argument('num_test', type=int)

    args = parser.parse_args()

    db_uri = sqlalchemy.engine.url.URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        database=os.environ["DB_NAME"]
    )

    main(args, db_uri)
