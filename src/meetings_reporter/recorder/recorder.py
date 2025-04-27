import multiprocessing
import time
import signal
from pydub import AudioSegment
import os
from datetime import datetime
from ..my_logger import get_logger, change_logger_level

from .rec_processes import (
    mic_recorder_process_worker,
    system_recorder_process_worker,
)

ROOT = os.path.dirname(__file__)
logger = get_logger(ROOT)


def record(
    output_dir=None,
    keep_temp_recording: bool = False,
    mic_amplify: int = 4,
    **kwargs,
):
    if kwargs.get("debug"):
        change_logger_level(logger)

    default_path = "recs"
    os.makedirs(default_path, exist_ok=True)

    if output_dir is None:
        output_dir = default_path
    elif not os.path.exists(output_dir):
        os.mkdir(output_dir)

    recording_flag = multiprocessing.Value("b", True)

    def handle_interrupt(sig, frame):
        logger.debug("Interrupt received, stopping all recording...")
        logger.info("stopping recording..")
        recording_flag.value = False

    signal.signal(signal.SIGINT, handle_interrupt)

    logger.info("Recording... Press Ctrl+C to stop")

    p1 = multiprocessing.Process(
        target=mic_recorder_process_worker, args=(recording_flag,)
    )

    p2 = multiprocessing.Process(
        target=system_recorder_process_worker, args=(recording_flag,)
    )

    p1.start()
    p2.start()
    try:
        while recording_flag.value:
            time.sleep(0.1)
    except KeyboardInterrupt:
        recording_flag.value = False
        logger.info("Recording stopped by user (KeyboardInterrupt)")

    p1.join(timeout=3)
    p2.join(timeout=3)
    if p1.is_alive():
        logger.info("Force terminating mic process")
        p1.terminate()
    if p2.is_alive():
        logger.info("Force terminating system recording process")
        p2.terminate()

    file_name = export_audio(
        output_dir,
        keep_temp_recording,
        mic_amplify,
    )
    saved_file_path = os.path.join(output_dir, file_name)
    logger.info(f"audio saved at {saved_file_path}")
    return saved_file_path


def export_audio(
    output_dir=None,
    keep_temp_recording: bool = False,
    mic_amplify: int = 4,
):
    """Exporting overlayed recorder audio (from both mic and system)
    Mic amplification might be required if your system has noise cancellation

    Args:
        output_dir (str, optional): _description_. Defaults to None.
        keep_temp_recording (bool, optional): Whether to keep recording artifacts or not(you might need to check for mic volume magnitude). Defaults to False.
        mic_amplify (int, optional): the amount in which mic audio is amplified(in dBs). Defaults to 4 approximate to 1.5x.

    Returns:
        _type_: _description_
    """
    mic_audio = AudioSegment.from_file(os.path.join("recs", "mic_out.wav"))
    system_audio = AudioSegment.from_file(os.path.join("recs", "sys_out.wav"))

    if len(mic_audio) > len(system_audio):
        system_audio = system_audio + AudioSegment.silent(
            duration=len(mic_audio) - len(system_audio)
        )
    else:
        mic_audio = mic_audio + AudioSegment.silent(
            duration=len(system_audio) - len(mic_audio)
        )
    mic_audio += mic_amplify

    mixed_audio = mic_audio.overlay(system_audio)
    if not keep_temp_recording:
        logger.debug("removing artifacts")
        os.remove(os.path.join("recs", "mic_out.wav"))
        os.remove(os.path.join("recs", "sys_out.wav"))

    try:
        now = datetime.now()
        filename = now.strftime("%Y_%m_%d,%H_%M") + ".wav"
        mixed_audio.export(os.path.join(output_dir, filename), format="wav")
        return filename
    except Exception as e:
        logger.error(f"error {e}")
