import traceback
import pickle
# import mlflow
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# from src.fetch_data import DataLoader
from src.processing import FeatureEngineering
from src.cleaning import CleanDataFrame
from src.exploration import Analysis
from src.rotating_logs import get_rotating_log
from io import BytesIO, StringIO
import dvc.api as dvc


#logger = get_rotating_log("dashboard_helper.log", 'DashboardHelper')

# dataloader = DataLoader()
feature_engineering = FeatureEngineering()
cleaner = CleanDataFrame()
analyzer = Analysis()

# store_df = dataloader.dvc_get_data(
#     "data/raw/store.csv", 'stores_missing_filled_v2', '.')


def merge_with_store(df: pd.DataFrame) -> pd.DataFrame:
    try:
        content = dvc.api.read(path="data/raw/store.csv",
                               repo='.',
                               rev='stores_missing_filled_v2')
        store_df = pd.read_csv(StringIO(content))
        df = df.merge(store_df, on='Store', how='left')
        #logger.info("Dataframe now merged")
    except:
        pass
        #logger.error("Unable to merge dataframe with store.csv")
        #logger.error(traceback.print_exc())

    return df


def add_train_columns(df: pd.DataFrame) -> pd.DataFrame:
    try:

        df = feature_engineering.transform(df)
        #logger.info("Date related training features added to test data")
    except:
        pass
        #logger.error("Unable to add training features to testing data")
        #logger.error(traceback.print_exc())

    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    count, cols = analyzer.get_missing_entries_count(df)
    df = cleaner.replace_missing(df, cols, 'median')

    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df['Date'] = pd.to_datetime(df['Date'])
    df = clean(df)
    df = merge_with_store(df)
    df = add_train_columns(df)
    df = clean(df)

    return df


def plot_predictions(date, sales):
    fig = plt.figure(figsize=(20, 7))
    ax = sns.lineplot(x=date, y=sales)
    ax.set_title("Predicted Sales", fontsize=24)
    ax.set_xlabel("Row index", fontsize=18)
    ax.set_ylabel("Sales", fontsize=18)

    return fig


def load_model(model_path: str = None):
    # model_file = dataloader.dvc_get_data("models/model.pkl", 'rf-reg-v1', '.')
    with dvc.open("models/model.pkl", "github.com/Hen0k/Rossmann-Pharmaceuticals-Sales-Forcast", "rf-reg-v1", mode='rb') as model_file:
        # print(type(model_file))
        # model_file = BytesIO(model_file)
        # with open(model_path, 'rb') as f:
        model = pickle.load(model_file)
        # model = pickle.load(BytesIO(model_file))

    return model
