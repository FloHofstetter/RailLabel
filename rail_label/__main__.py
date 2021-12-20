import pathlib
import argparse
from rail_label.label_gui import LabelGui
import yaml


def parse_yaml(yaml_path: pathlib.Path) -> dict:
    """
    Parse configuration from YAML.
    :param yaml_path: Path to settings file
    :return:
    """
    with open(yaml_path) as file_pointer:
        yaml_args = yaml.load(file_pointer, yaml.Loader)
    return yaml_args


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
    if cli_args["settings_path"]:
        yaml_path = cli_args["settings_path"]
    else:
        yaml_path = pathlib.Path("settings.yml")

    yaml_args = parse_yaml(yaml_path)

    settings = {**yaml_args, **cli_args}

    return settings


def main():
    settings = parse_settings()

    label_gui = LabelGui(settings)
    label_gui.event_loop()


if __name__ == "__main__":
    main()
