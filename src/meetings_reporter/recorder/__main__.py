from .recorder_cli import recorder_parser


def main():
    from .recorder import record

    args = recorder_parser()
    args = args.parse_args()
    args = vars(args)
    record(**args)
