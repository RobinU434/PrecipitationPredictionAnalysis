from argparse import ArgumentParser
from project.process.process import DataProcess
from project.utils.parser import setup_parser


def execute(args: dict) -> bool:
    module = DataProcess()
    match args["command"]:

        case "start-crawler":

            module.start_crawler(
                output_dir=args["output_dir"],
                crawler_config_path=args["crawler_config_path"],
                query_time=args["query_time"],
            )

        case "analyse":

            module.analyse(use_active_venv=args["use_active_venv"])

        case "get":

            module.get(save=args["save"])

        case "get-historical":

            module.get_historical(
                station_ids=args["station_ids"], save_path=args["save_path"]
            )

        case "get-recent":

            module.get_recent(
                station_ids=args["station_ids"],
                save_path=args["save_path"],
                features=args["features"],
                unpack=args["unpack"],
                force=args["force"],
            )

        case "convert-to-csv":

            module.convert_to_csv(
                input_dir=args["input_dir"],
                output_dir=args["output_dir"],
                force=args["force"],
            )

        case _:

            return False

    return True


def create_parser() -> ArgumentParser:

    parser = ArgumentParser(description="process for data literacy class")

    parser = setup_parser(parser)

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()
    args_dict = vars(args)
    if not execute(args_dict):
        parser.print_usage()


if __name__ == "__main__":

    main()
