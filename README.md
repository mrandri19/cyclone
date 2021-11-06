## Run a MLflow project

`mlflow run bike-rental-regression -P train_year=2011 -P train_month=1 -P test_year=2011 -P test_month=2 -P dataset_path=train_bike.csv`
`mlflow run bike-rental-regression -P train_year=2011 -P train_month=1 -P test_year=2011 -P test_month=3 -P dataset_path=train_bike.csv`

## Serve one model artifacts produced by running a project

mlflow models serve --model-uri runs:/a76f74e7dba9446f81b719d5b211cf7b/model --port 9999
