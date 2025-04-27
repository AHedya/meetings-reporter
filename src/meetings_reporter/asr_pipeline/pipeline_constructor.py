from .config import asr_config
from .utils import (
    transcribe,
    load_audio,
    align,
    handle_diarization,
    assign_word_speakers,
    write_transcription,
    process_srt,
    extract_speakers_from_rttm,
    calculate_speaker_durations,
)
import os
from ..my_logger import get_logger


import logging

from typing import Dict


# so much logging, so set level to error only
logging.getLogger("nemo_logger").setLevel(logging.ERROR)

config = asr_config()
ROOT = os.path.dirname(__file__)
logger = get_logger(ROOT)


def pipeline(
    audio_file_path,
    config,
    transcription_dir: str = "transcription",
    convert_srt: bool = True,
    export_diarized_audio=False,
    diarized_audio_path="exported_audio",
    get_num_speakers=False,
    **kwargs,
):
    if not isinstance(config, dict):
        config = config.model_dump()
    logger.debug("config loaded")
    audio = load_audio(audio_file_path)
    logger.debug(f"audio loaded: {os.path.basename(audio_file_path)}")

    logger.info("transcribing...")
    result = transcribe(audio, **config)

    logger.info("aligning...")
    result = align(result, audio, config["device"])

    if config.get("diarization_provider"):
        logger.info(
            f"diarizing({config['diarization_provider']}{' - ' + config['nemo_dairizer_type'] if config['diarization_provider'] == 'nemo' else ''})..."
        )
        diarize_segments = handle_diarization(audio_file_path, **config)

        logger.info("assigning words to speakers...")
        result = assign_word_speakers(diarize_segments, result)
    result["language"] = config["language"]

    final_output_file_path = transcription_dir
    srt_file_path = os.path.join(
        transcription_dir,
        os.path.splitext(os.path.basename(audio_file_path))[0] + ".srt",
    )
    os.makedirs(transcription_dir, exist_ok=True)
    logger.info(f"Exporting transcription to path {srt_file_path}")
    write_transcription(
        output_format=config["output_format"],
        output_dir=transcription_dir,
        result=result,
        audio_file_path=audio_file_path,
    )
    if convert_srt:
        logger.info("processing. srt -> LLM_feed")
        final_output_file_path = process_srt(
            srt_file_path,
            output_path=transcription_dir,
            role_players=config["role_players"],
        )

    if export_diarized_audio:
        rttm_file_path = os.path.join(
            ROOT,
            "outputs",
            "pred_rttms",
            f"{os.path.basename(audio_file_path).split('.')[0]}.rttm",
        )
        logger.info("Exporting")
        extract_speakers_from_rttm(
            rttm_file_path, audio_file_path, output_dir=diarized_audio_path
        )

    speakers_duration: Dict[str, float] = {}
    if get_num_speakers:
        logger.info("calculating num speakers...")
        if config["diarization_provider"] != "pyannote":
            logger.info("diarizing (pyannote)...")

            diarize_segments = handle_diarization(
                audio_file_path,
                device=config["device"],
                diarization_provider="pyannote",
            )
        speakers_duration = calculate_speaker_durations(diarize_segments)

    return final_output_file_path, speakers_duration
