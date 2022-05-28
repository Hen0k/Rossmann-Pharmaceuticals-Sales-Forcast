from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

from sklearn.model_selection import train_test_split

from sklearn.metrics import (accuracy_score,
                             confusion_matrix,
                             mean_squared_error,
                             r2_score,
                             mean_absolute_error,
                             log_loss,
                             precision_score,
                             recall_score)
import dvc.api
import io
import mlflow
import time

from src.cleaning import CleanDataFrame

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns


class TrainingPipeline(Pipeline):
    '''
    Class -> TrainingPipeline, ParentClass -> Sklearn-Pipeline
    Extends from Scikit-Learn Pipeline class. Additional functionality to track 
    model metrics and log model artifacts with mlflow
    params:
    steps: list of tuple (similar to Scikit-Learn Pipeline class)
    '''

    def __init__(self, steps):
        super().__init__(steps)

    def fit(self, X_train, y_train):
        self.__pipeline = super().fit(X_train, y_train)
        return self.__pipeline

    def get_metrics(self, y_true, y_pred):
        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)

        return {
            'mse': round(mse, 2),
            'r2': round(r2, 2),
            'mae': round(mae, 2),

        }

    def get_feature_importance(self, model, x):
        feature_importance = None
        if str(model) == "LogisticRegression()":
            feature_importance = model.coef_[0]
        else:
            feature_importance = model.feature_importances_
        feature_array = {}
        for i, v in enumerate(feature_importance):
            feature_array[x.columns[i]] = round(float(v), 2)
        return feature_array

    def make_model_name(self, experiment_name, run_name):
        clock_time = time.ctime().replace(' ', '-')
        return experiment_name + '_' + run_name + '_' + clock_time

    def log_model(self, model_key, X_test, y_test, experiment_name, run_name, run_params=None):
        model = self.__pipeline.get_params()[model_key]
        y_pred = self.__pipeline.predict(X_test)

        run_metrics = self.get_metrics(y_test, y_pred)
        feature_importance = self.get_feature_importance(
            model, X_test)
        feature_importance_plot = self.plot_feature_importance(
            feature_importance)
        pred_plot = self.plot_preds(y_test, y_pred, experiment_name)
        # cm_plot = self.plot_confusion_matrix(y_test, y_pred)
        print(run_metrics)
        # print(feature_importance)

        mlflow.set_experiment(experiment_name)
        # Commented out because of this: https://lifesaver.codes/answer/runid-not-found-when-executing-mlflow-run-with-remote-tracking-server-608
        mlflow.set_tracking_uri('http://localhost:5000')
        with mlflow.start_run(run_name=run_name):
            if run_params:
                for name in run_params:
                    mlflow.log_param(name, run_params[name])
            print("Run params saved")
            for name in run_metrics:
                mlflow.log_metric(name, run_metrics[name])
            print("Run metrics saved")
            mlflow.log_param("columns", X_test.columns.to_list())
            print("logging figures")
            mlflow.log_figure(pred_plot, "predictions_plot.png")
            # mlflow.log_figure(cm_plot, "confusion_matrix.png")
            mlflow.log_figure(feature_importance_plot,
                              "feature_importance.png")
            print("figures saved with mlflow")
            pred_plot.savefig("../images/predictions_plot.png")
            # cm_plot.savefig("../images/confusion_matrix.png")
            feature_importance_plot.savefig("../images/feature_importance.png")
            print("figures saved")
            mlflow.log_artifact(
                "../images/feature_importance.png", "metrics_plots")
            # print("Saving artifacts")
            mlflow.log_dict(feature_importance, "feature_importance.json")
            print("saving dict")
        model_name = self.make_model_name(experiment_name, run_name)
        mlflow.sklearn.log_model(
            sk_model=self.__pipeline, artifact_path='models', registered_model_name=model_name)
        print('Run - %s is logged to Experiment - %s' %
              (run_name, experiment_name))
        return run_metrics

    def plot_preds(self, y_test, y_preds, model_name):
        fig = plt.figure(figsize=(40, 10))
        sns.lineplot(x=range(len(y_test)), y=y_test)
        sns.lineplot(x=range(len(y_preds)), y=y_preds)
        plt.title(f"{model_name} predictions vs true values", fontsize=30)
        plt.legend(['Predicted', 'True Value'])

        return fig

    def plot_feature_importance(self, feature_importance):
        importance = pd.DataFrame({
            'features': feature_importance.keys(),
            'importance_score': feature_importance.values()
        })
        fig = plt.figure(figsize=[8, 5])
        ax = sns.barplot(x=importance['features'],
                         y=importance['importance_score'])
        ax.set_title("Feature's importance")
        ax.set_xlabel("Features", fontsize=20)
        ax.set_ylabel("Importance", fontsize=20)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

        # figure = ax.get_figure()
        return fig


def label_encoder(df: pd.DataFrame, cat_columns: list[str]) -> pd.DataFrame:
    lb = LabelEncoder()
    for col in cat_columns:
        df[col] = lb.fit_transform(df[col].astype(str))

    return df


def get_pipeline(model, x):
    cat_cols = CleanDataFrame.get_categorical_columns(x)
    num_cols = CleanDataFrame.get_numerical_columns(
        x)   # Remove the target column

    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    numerical_transformer = Pipeline(steps=[
        ('scale', StandardScaler()),
        # ('norm', Normalizer()),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, num_cols),
            # ('cat', categorical_transformer, cat_cols)
        ])
    train_pipeline = TrainingPipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    return train_pipeline


def dvc_get_data(path, version='72d1bf77e90769aaef56e18685215ddc98af3343'):
    repo = "../"
    content = dvc.api.read(path=path,
                           repo=repo,
                           rev=version)
    df = pd.read_csv(io.StringIO(content), sep=",")

    return df


def run_train_pipeline(model, x: pd.DataFrame, experiment_name: str, run_name: str):
    '''
    function which executes the training pipeline
    Args:
        model : an sklearn model object
        x : a dataframe with features and a Sales column
        experiment_name : MLflow experiment name
        run_name : Set run name inside each experiment
    '''
    x = x.sort_values(by="Date", ascending=False)
    x.drop(columns=['Date'], inplace=True)
    # x = label_encoder(x)
    train_pipeline = get_pipeline(model, x.drop(columns=['Sales']))

    train, test = x.iloc[:int(len(x)*.8), :], x.iloc[int(len(x)*.8):, :]
    # print(len(train), len(test))
    X_train = train.drop(columns=['Sales'])
    X_test = test.drop(columns=['Sales'])
    y_train = train['Sales'].values
    y_test = test['Sales'].values

    run_params = model.get_params()

    train_pipeline.fit(X_train, y_train)

    train_pipeline.log_model('model', X_test, y_test,
                             experiment_name, run_name, run_params=run_params)
    return train_pipeline
