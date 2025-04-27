import argparse


def asr_parser(add_help=True):
    parser = argparse.ArgumentParser(
        description="WhisperX + NeMo diarizer pipeline", add_help=add_help
    )
    parser.add_argument(
        "-i", "--audio_file_path", type=str, help="Input audio file path"
    )
    parser.add_argument(
        "-td",
        "--transcription_dir",
        type=str,
        default="transcription",
        help="Pipeline output directory",
    )
    parser.add_argument("--get_num_speakers", action="store_true", help="")

    # override asr_config
    parser.add_argument("--model", type=str, default="large-v3", help="Model name")
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu"],
        default="cuda",
        help="Device to run the model on",
    )
    parser.add_argument(
        "--compute_type",
        type=str,
        default="float16",
        help="Computation type (e.g., float16, int8 for CPU)",
    )
    parser.add_argument(
        "--batch_size", type=int, default=16, help="Batch size for processing"
    )
    parser.add_argument(
        "--language", type=str, default="ar", help="Language for transcription"
    )
    parser.add_argument(
        "--diarization_provider",
        type=str,
        choices=["nemo", "pyannote"],
        default="nemo",
        help="Which diarization system to use",
    )
    parser.add_argument(
        "--nemo_diarizer_type",
        type=str,
        choices=["neural", "clustering"],
        default="neural",
        help="Type of diarization model in NeMo",
    )
    parser.add_argument(
        "--export_diarized_audio",
        action="store_true",
        help="aggregate each speaker sample into audio file, and export them",
    )
    parser.add_argument(
        "--diarized_audio_path",
        type=str,
        help="path of exported audio",
        default="exported_audio",
    )
    parser.add_argument(
        "--min_speakers",
        type=int,
        default=2,
        help="Minimum number of speakers for diarization",
    )
    parser.add_argument(
        "--max_speakers",
        type=int,
        default=6,
        help="Maximum number of speakers for diarization",
    )
    parser.add_argument(
        "--output_format",
        type=str,
        default="srt",
        choices=["srt", "all"],
        help="Output format (e.g., srt, txt)",
    )
    parser.add_argument(
        "--role_players",
        nargs="+",
        type=str,
        default=["Speaker_1", "Speaker_2"],
        help="List of role player names",
    )

    return parser
