import argparse
from .asr_pipeline.asr_cli import asr_parser
from .recorder.recorder_cli import recorder_parser
from .report_builder.report_cli import report_parser


def main_parser():
    parser = argparse.ArgumentParser(
        description="Main pipeline parser",
        parents=[
            recorder_parser(False),
            asr_parser(False),
            report_parser(False),
        ],
    )

    parser.add_argument(
        "--no_report",
        action="store_true",
        help=("perform both recording + asr without writing report"),
    )
    parser.add_argument(
        "--no_record",
        action="store_true",
        help=(
            "perform both asr + reporting  without writing recording on a given audio file"
        ),
    )
    args = parser.parse_args()

    return args
