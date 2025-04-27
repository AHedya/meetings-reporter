from .main_cli import main_parser

try:
    from .asr_pipeline.config import asr_config
    from .asr_pipeline import transcription_pipeline
except Exception as e:
    print(f"couldn't import asr, looks like you missed installing deps.\n Error{e}")
from .recorder import record
from .report_builder import report_pipeline

config_keys = asr_config().model_dump().keys()


def main():
    args = main_parser()
    args = vars(args)

    config_args = {k: v for k, v in args.items() if k in config_keys}
    config = asr_config(**config_args)
    args = {k: v for k, v in args.items() if k not in config_keys}

    print(args)
    if not args.get("no_record"):
        record_path = record(**args)
        # overwrite audio file path, recording used
        args["audio_file_path"] = record_path

    llm_feed_path, speakers_analysis = transcription_pipeline(config=config, **args)
    if not args.get("no_report"):
        ### meaningful string i.e. from {speaker1:200,speaker2:300} -> "speaker1: 40%, speaker2: 60%"
        total_duration = sum([i for i in speakers_analysis.values()])
        percentages = [
            f"{k}: {v / total_duration * 100:.2f}%"
            for k, v in speakers_analysis.items()
        ]
        speakers_analysis = f"\n{'\t'.join(percentages)}\n"
        ###
        report_path = report_pipeline(
            model_feed_file_path=llm_feed_path, report_header=speakers_analysis, **args
        )
        print(report_path)


if __name__ == "__main__":
    main()
