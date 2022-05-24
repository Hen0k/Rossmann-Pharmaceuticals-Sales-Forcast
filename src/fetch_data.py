from fileinput import filename
import io
import dvc.api
import pandas as pd
from src.rotating_logs import get_rotating_log


logger = get_rotating_log(filename='data_loader.log')


class DataLoader:
    """This class is a wrapper for getting DVC versioned datasets and normal csvs from file"""
    @staticmethod
    def dvc_get_data(path: str, version: str, repo: str = '../') -> pd.DataFrame:
        """Fetch DVC versioned files. You need to know the path to the file, starting from the root of the repo.
        Args:
            path: str -> file path starting from root of repo
            version: str -> a git tag or a git commit hash where the file exists
            repo: str -> file directory or link for repository containing the versioned dataset

        Returns:
            pd.DataFrame
        """
        try:
            content = dvc.api.read(path=path,
                                   repo=repo,
                                   rev=version)
            df = pd.read_csv(io.StringIO(content), sep=",")
            logger.info(
                f"DVC: CSV file read with path: {path} | version: {version} | from: {repo}")
            return df
        except:
            logger.exception("DVC data getter raised an exception")

    @staticmethod
    def read_csv(path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(path)
            logger.info(f"Pandas: CSV read from: {path}")
            return df
        except:
            logger.exception(f"Pandas failed to read the csv at: {path}")
