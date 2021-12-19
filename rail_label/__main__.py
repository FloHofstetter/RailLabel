import pathlib
import argparse
from rail_label.label_gui import LabelGui
import yaml


def parse_yaml():
    """
    Parse configuration from YAML.
    :return:
    """
    data = yaml.parse()


def parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """
    Parse CLI arguments.
    :param parser: Argument parser Object.
    :return: CLI Arguments object.
    """
    parser.add_argument(
        "-d",
        "--dataset_path",
        type=str,
        help="Path to the directory containing a dataset.",
        default=".",
    )
    parser.add_argument(
        "-s",
        "--settings_path",
        type=str,
        help="Path to settings YAML-file for RailLabel.",
    )
    return parser.parse_args()


def configure_paths(args: argparse.Namespace) -> dict[str, pathlib.Path]:
    """
    Set up paths.
    :param args: CLI arguments
    :return: Dictionary containing paths
    """
    paths = {}
    # Settings YAML
    if args.settings_path:
        paths["settings"] = pathlib.Path(args.settings_path)
    else:
        paths["settings"] = pathlib.Path("settings.yml")
    # Dataset
    paths["data_set"] = pathlib.Path(args.dataset_path)

    return paths


def main():
    parser = argparse.ArgumentParser()
    args = parse_args(parser)

    paths: dict[str, pathlib.Path]
    paths = configure_paths(args)

    # RailLabel main object
    label_gui = LabelGui(paths["data_set"])
    label_gui.event_loop()


if __name__ == "__main__":
    main()
