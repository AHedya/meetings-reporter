from . import transcription_pipeline
from .asr_cli import asr_parser
from .config import asr_config

config = asr_config()
config_keys = config.model_dump().keys()


def main():
    args = asr_parser()
    args = args.parse_args()
    args = vars(args)

    config_args = {k: v for k, v in args.items() if k in config_keys}
    config = asr_config(**config_args)
    args = {k: v for k, v in args.items() if k not in config_keys}
    _ = transcription_pipeline(config=config, **args)
