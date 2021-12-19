import pathlib
import argparse
from rail_label.label_gui import LabelGui


def parse_args(parser: argparse.ArgumentParser):
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
    return parser.parse_args()


def main():
    # Parse arguments from cli
    parser = argparse.ArgumentParser()
    args = parse_args(parser)

    # Path parameters
    data_set_path = pathlib.Path(args.dataset_path)

    # RailLabel main object
    label_gui = LabelGui(data_set_path)
    label_gui.event_loop()


if __name__ == "__main__":
    main()
