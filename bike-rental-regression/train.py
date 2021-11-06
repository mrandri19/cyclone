from argparse import Namespace
import pandas as pd
import mlflow
from sklearn.ensemble import HistGradientBoostingRegressor as Model
from sklearn.metrics import r2_score

import argparse


def time_features(input_df):
    return input_df.assign(
        month=lambda df: df.index.month,
        day=lambda df: df.index.day,
        hour=lambda df: df.index.hour,
    )


def main(params: Namespace):
    with mlflow.start_run():
        dataset = (
            pd.read_csv(params.dataset_path, header=0,  sep=',',
                        parse_dates=['datetime'], index_col='datetime')
            .drop(
                columns=['casual', 'registered']
            ))
        train = dataset.loc[
            lambda df: (df.index.year == params.train_year) & (
                df.index.month == params.train_month)
        ]
        test = dataset.loc[
            lambda df: (df.index.year == params.test_year) & (
                df.index.month == params.test_month)
        ]

        # Instantiate model
        model = Model()
        mlflow.set_tag("model_module", model.__class__.__module__)
        mlflow.set_tag("model_type", model.__class__.__name__)

        # Train model
        model.fit(train.drop(columns='count').pipe(
            time_features), train['count'])

        # Test model
        score = r2_score(test['count'], model.predict(
            test.drop(columns='count').pipe(time_features)))
        mlflow.log_metric('test_r2_score', score)

        # Register trained model
        input_example = train.head(10).pipe(
            time_features).drop(columns='count')
        signature = mlflow.models.signature.infer_signature(
            input_example, model.predict(input_example)
        )
        mlflow.sklearn.log_model(
            model, "model", signature=signature, input_example=input_example)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('train_year', type=int)
    parser.add_argument('train_month', type=int)
    parser.add_argument('test_year', type=int)
    parser.add_argument('test_month', type=int)
    parser.add_argument('dataset_path', type=str)

    args = parser.parse_args()

    main(args)
