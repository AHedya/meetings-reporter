import argparse


def recorder_parser(add_help=True):
    parser = argparse.ArgumentParser(
        description="Real-time recorder CLI", add_help=add_help
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save the recorded audio file. If not set, uses a default location.",
    )

    parser.add_argument(
        "-k",
        "--keep-temp-recording",
        action="store_true",
        help=(
            "Keep temporary recording artifacts (useful for debugging or checking mic volume levels)."
        ),
    )

    parser.add_argument(
        "--mic-amplify",
        type=int,
        default=4,
        help="Amount to amplify mic audio in dB (default is 4 dB, approx 1.5x volume).",
    )

    return parser
