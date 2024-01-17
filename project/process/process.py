import datetime
import glob
import os
from os import makedirs
from typing import List

from tqdm import tqdm

import project.crawler as crawler
from project.analysis.pipeline import JupyterPipeline
from project.convert.dwd_converter import DWDJsonConverter
from project.convert.utils import insert_column
from project.crawler.base import BaseCrawler
from project.crawler.manager import CrawlerManager
from project.database.database import Database
from project.process.utils.download_dwd_data import (
    build_recent_url,
    check_station_ids,
    filter_features,
)
from project.process.utils.unpack_zip import unzip
from project.utils.download import get_zips
from project.utils.file_system import load_json, load_yaml


class DataProcess:
    """
    process for data literacy class
    """

    def __init__(self) -> None:
        """_summary_"""

        self._db = Database(
            user_name="root",
            password="example",
            db_name="WeatherData",
            host_ip="172.19.0.4",
            # host_ip="mariadb.data_literacy_network",
            port=3306,
        )

        self._crawler: List[BaseCrawler]

    def _build_crawler(
        self, crawler_config_path: str = "project/config/crawler.config.yaml"
    ):
        self._crawler = []
        for crawler_config in load_yaml(crawler_config_path):
            name = crawler_config.pop("name")
            crawler_class = getattr(crawler, name)
            self._crawler.append(crawler_class(**crawler_config))

    def build_db(self):
        """generate table in SQL data base"""
        self._db.build_tables()

    def start_crawler(
        self, crawler_config_path: str = "project/config/crawler.config.yaml"
    ):
        """
        start crawler to collect weather data from APIs specified in crawler config

        Args:
            crawler_config_path (str): crawler config for individual apis
        """
        self._build_crawler(crawler_config_path)
        crawler_manager = CrawlerManager(self._crawler, "00:10")
        crawler_manager.start()

    def analyse(
        self,
        use_active_venv: bool = False,
    ):
        """start pipeline to analyse data.

        Args:
            use_active_venv (bool, optional): set this flag if you have poetry installed and would like to run the analysis in with the active python env
        """
        jupyter_pipeline = JupyterPipeline(
            use_active_venv=use_active_venv,
            note_book_listing_path="project/config/analysation_scripts.yaml",
        )
        jupyter_pipeline.run()

    def get(self, save: bool = True):
        """send request to every embedded crawler and return pandas data frame heads onto terminal

        Args:
            save (bool, optional): _description_. Defaults to True.
        """
        self._build_crawler()
        for crawler in self._crawler:
            content = crawler.get(save=save)
            print(f"===== {type(crawler).__name__} ====")
            print(content)

    def get_historical(self, station_ids: List[int], save_path: str):
        """get historical (precipitation, pressure, air temperature) data from the dwd database


        Args:
            station_ids (List[int]): _description_
            save_path (str): _description_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    def get_recent(
        self,
        station_ids: List[int],
        save_path: str,
        features: List[str],
        unpack: bool = True,
    ):
        """get recent (precipitation, pressure, air temperature) data from the dwd database

        Args:
            station_ids (List[int]): station ids from DWD
            save_path (str): where you want to store the collected information. It will create this directory if it does not exist already.
            unpack (bool): if set to true we will also unpack the downloaded zips
            features (List[str]): features you want to extract from DWD API
        """

        makedirs(save_path, exist_ok=True)

        features = filter_features(features)

        # convert elements of station ids to ints
        station_ids = list(map(lambda x: int(x), station_ids))

        mask = check_station_ids(station_ids)
        success_counter = 0
        file_names = []
        for station_id, valid in tqdm(zip(station_ids, mask)):
            if not valid:
                continue
            file_name = ""
            for feature in features:
                url = build_recent_url(feature, station_id)
                file_name = get_zips(url, save_path)
                if len(file_name):
                    file_names.append(file_name)

            if len(file_name):
                success_counter += 1

        print(f"({success_counter}/{len(station_ids)}) where successful.")

        if unpack:
            unzip(*file_names)

    def convert_to_csv(self, input: str = "data/dwd/raw", output: str = "data/dwd/csv"):
        """convert the forecast data into csv format

        Args:
            input (str): root folder of all forecast json files. Defaults to "data/dwd/json/raw
            output (str): where to output the csv file structure. Defaults to "data/dwd/raw
        """
        input = input.rstrip("/")
        output = output.rstrip("/") + "/"

        converter = DWDJsonConverter()
        for file_name in tqdm(glob.glob(input + "/*.json"), desc="processing files"):
            call_time_utc = int(file_name.split("/")[-1].split(".")[0])
            data = load_json(file_name)

            dfs = converter.to_df(data)
            dfs = insert_column(
                dfs,
                column_name="call_time",
                value=datetime.datetime.utcfromtimestamp(call_time_utc),
            )
            os.makedirs(output + str(call_time_utc))

            for key, df in filter(lambda x: bool(len(x[1])), dfs.items()):
                df.to_csv(output + str(call_time_utc) + "/" + key + ".csv")
