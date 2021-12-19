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


def parse_cli() -> dict:
    """
    Parse CLI arguments.
    :param parser: Argument parser Object.
    :return: CLI Arguments object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--settings_path",
        type=str,
        help="Path to settings YAML-file for RailLabel.",
    )
    parser.add_argument(
        "-d",
        "--dataset_path",
        type=str,
        help="Path to the directory containing a dataset.",
        default=".",
    )
    return vars(parser.parse_args())


def parse_settings() -> dict[str, pathlib.Path]:
    """
    Get configuration for label tool. Standard configuration is in YAML file.
    These are overwritten by CLI arguments.
    :return: Dictionary containing paths
    """
    # Parse CLI arguments
    cli_args = parse_cli()
    yaml_path = (
        cli_args["settings_path"]
        if cli_args["settings_path"]
        else pathlib.Path("settings.yml")
    )

    # Parse YAML arguments
    with open(yaml_path) as file_pointer:
        yaml_args = yaml.load(file_pointer, yaml.Loader)
    settings = {**yaml_args, **cli_args}

    return settings


def main():
    settings = parse_settings()

    label_gui = LabelGui(settings)
    label_gui.event_loop()


if __name__ == "__main__":
    main()
