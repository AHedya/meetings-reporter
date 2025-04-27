import argparse


def report_parser(add_help=True):
    parser = argparse.ArgumentParser(description="Report builder", add_help=add_help)
    parser.add_argument(
        "-llm",
        "--LLM_feed",
        type=str,
        help="Directory to model context",
    )

    parser.add_argument(
        "-rd",
        "--reports_directory",
        default="reports",
        type=str,
        help="Directory to final report",
    )
    parser.add_argument(
        "--save_history",
        action="store_true",
        help="save llm responses history",
    )
    ## model stuff
    parser.add_argument(
        "--temperature",
        type=float,
        help=("LLM temperature"),
    )
    parser.add_argument(
        "--model_provider",
        type=str,
        default="google",
        help=("your LLM provider (currenly google, wait for updates)"),
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help=("your api key"),
    )
    parser.add_argument(
        "--MODEL_ID",
        type=str,
        help=("model id(tag) or your provider"),
    )

    return parser
