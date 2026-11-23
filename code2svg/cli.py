import argparse
import pathlib

from dataclasses import dataclass

__all__ = ['Config', 'parse_config']

@dataclass
class Config:
    """
    Represents the configuration of the command-line tool.

    :param output_file: The file the output should be written to.
    :type output_file: pathlib.Path
    :param font_file: The file containing the font.
    :type font_file: pathlib.Path
    :param pretty_output: Indicates whether the output SVG should be
                          formatted.
    :type pretty_output: bool
    """

    output_file: pathlib.Path
    font_file: pathlib.Path
    pretty_output: bool


def _existing_file(value: str) -> pathlib.Path:
    """
    Checks whether the given path exists and whether it is a file.

    :param value: The path.
    :type value: str

    :raises argparse.ArgumentTypeError: If the path does not exist or if it is
                                        not a file.

    :return: The path.
    :rtype: pathlib.Path
    """

    path = pathlib.Path(value)

    if not path.exists():
        raise argparse.ArgumentTypeError(f'{path}: no such file or directory')

    if not path.is_file():
        raise argparse.ArgumentTypeError(f'{path}: expected regular file')

    return path


def _non_existent_or_regular_file(value: str) -> pathlib.Path:
    """
    Checks whether the given path does not exist or whether it is a regular
    file.

    :param value: The path.
    :type value: str

    :raises argparse.ArgumentTypeError: If the path exists and is not a
                                        regular file.

    :return: The path.
    :rtype: pathlib.Path
    """

    path = pathlib.Path(value)

    if path.exists() and not path.is_file():
        raise argparse.ArgumentTypeError(f'{path}: expected regular file')

    return path


def parse_config() -> Config:
    """
    Parses the code2svg configuration from the command-line arguments.

    :return: The configuration.
    :rtype: Config
    """

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        'output',
        type=_non_existent_or_regular_file,
        help='The output file',
    )
    argument_parser.add_argument(
        '-f',
        '--font-file',
        required=True,
        type=_existing_file,
        help='The file of the font to use.',
    )
    argument_parser.add_argument(
        '-p',
        '--pretty',
        action='store_true',
        help=(
            'Format the SVG using line breaks, indentations, and spaces befor'
            'e trailing slashes'
        ),
    )
    args = argument_parser.parse_args()

    return Config(
        output_file=args.output,
        font_file=args.font_file,
        pretty_output=args.pretty,
    )
