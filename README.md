# Accuracy in Precipitation Prediction

This repository contains the tools and pipeline for data analysis to investigate the performance of weather-forecasts the German-Weather-Agency ([DWD](https://www.dwd.de/DE/Home/home_node.html)) is providing. 
We collected forecasts from 36 stations across the state of Baden-Württemberg from the begging of December until the end of January. 

The project contains 3 main building blocks.

1. A dockerized download server to download the forcasts from the [open weather api](https://dwd.api.bund.dev/)
2. Studies we conducted on the data formulated in [Jupyter Notebooks](https://jupyter.org/)
3. A summarizing [report](./docs/report/report.pdf) over the work we conducted. 

The following chapters provide a brief overview how to use the codebase. 

## Installation

We use [poetry](https://python-poetry.org/) for package management in Python. If you didn't already install it you can read up on it [here](https://python-poetry.org/docs/#installation).   
To install the dependencies execute in project root:
```bash
poetry install
```

You can either activate the venv poetry generates, or execute `poetry run python` instead of just `python`. 

For further insights into poetry we can recommend their [documentation](https://python-poetry.org/docs/).

Furthermore, this project uses git lfs, thus please install and activate it to properly clone this repository.

## Download Server

To start the download server you have to install docker. After this call
```bash
docker-compose -f docker/docker-compose.yaml up -d
```
to start the download server. This server will call the DWD API once per day at 00:10 with the specified `station_ids` in the [config file](project/config/crawler.config.yaml) and writes its results in `data/dwd/raw` as json files. The filename is the integer of the timestamp the api was called at.

Note for Developers:  
If you would like to extend this service also to other API feel free to implement your own crawler and add them to the CrawlerManager. 

## Prepare Data

We provide collected forecast data on Git LFS. Therefore you should already have downloaded a bunch of json files from Git-LFS. Nevertheless you also need to do following steps in order to start the analysis.

1. **Covert Json to CSV**: Our analysis script are based on a `DWDDataset` object which is based on csv files. Therefore you have to convert the forecast data from json to csv. To do so please execute:
    ```bash
    python -m project convert-to-csv --input data/dwd/raw --output data/dwd/csv
    ```
    This command will scrape the forecast data and convert it into individual csv files at the specified output directory.
2. **Download historical data**: To asses the quality of a forecast model you have to download the historical data. Because this research project was conducted in Germany we use the historical and recent data from the DWD. To download each dataset respectively execute in project root:
    ```bash
    python -m project get-recent --unpack --station-ids 257 4189 13965 755 757 5688 1197 1214 1224 1255 6258 1584 6259 2074 7331 2575 2814 259 3402 5562 6275 3734 1602 3925 3927 4160 4169 4300 4349 6262 4703 6263 5229 4094 5664 5731 --save-path data/dwd/recent/ --features precipitation  air_temperature
    ```
    This will download the recent data (from the last 6 months) into `data/dwd/recent`.
    Note, that it will ask you whether this should overwrite an existing directory, you want to answer yes.
    This will lead to changes in git (lfs) tracked data.
    If your forecast data is older than 6 months you have to execute the same command but instead of using `get-recent` type `get-historical` (Note: Not tested yet).

## Do Analysis

The analysis is based on calculations done in Jupyter-Notebooks. To start every Notebook incorporated in the final report please start the analysis with.
```bash
python -m project analyse
```

## Further Tooling

To get more insigth what code base is capable of have a look at all commands with
```bash
python -m project --help
```
and into the individual commands with:
```bash
python -m project <command> --help
```

## Code base

The codebase is structured as follows:
```bash
├── data            # data folder
├── docker          # contains compose and Dockerfile
├── docs            # contains code documentation and report files
├── figures         # figures for Readme.md
├── LICENSE       
├── poetry.lock     # poetry lock file
├── project         # main code base
├── pyproject.toml  # poetry project file
├── README.md       
└── studies         # Notebooks, Python code, tooling, ...:  associated with the analysis
```

The content of `project`: 
```bash
.
├── analysis        # Classes to start analysis pipeline
├── config          # config files for analysis and download server
├── convert         # converter to convert api data into csv
├── crawler         # api crawler and crawler manager
├── database        # Not used yet: Tooling to build and load data into and SQL DB
├── __init__.py
├── __main__.py     
├── process         # main process class. Backbone of __main__.py
└── utils           # general tooling used by all components: interaction to filesystem, ...
```

For extensive code documentation please refer either to the embedded docstring or to Doxygen documentation in [PDF](docs/code/latex/refman.pdf) or in [HTML](docs/code/html/index.html).   

## Data

as previously mentioned we collected forecast data from 36 station across the state of Baden-Württemberg. 
![station](./figures/BaWu_stations_map.jpg)

The forecast we received from the `StationOverview` interface is documented at: https://dwd.api.bund.dev/.  
Note: If you try it you self you will experience precipitation and temperature forecast as integers. To successfully use them in comparison to the historical or recent data you have to divide at least those values by 10.  

We highly encourage all readers to conduct their own experiments on the collected data but also verify our results.  
If you have any doubts please add an issue at the corresponding GitHub repository. We will get back to you as soon as possible.

In case you build upon our repository or parts of the codebase we kindly ask to mention us in your work and refer to the original authors of this repository. 

## Acknowledgments

At this point we would like to thank the DWD to provide detailed public weather data but also Prof. Philip Hennig for providing great advice in his lectures and the opportunity to do this Data-Science project.

## Authors

[Leonor Diederichs](https://github.com/lilli288)  
[Samuel Maier](https://github.com/9SMTM6)  
[Mathias Neitzel](https://github.com/mathicantcode)  
[Robin Uhrich](https://github.com/RobinU434)  
