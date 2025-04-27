import threading
import soundcard as sc
import soundfile as sf
import queue
import signal
import os
from ..my_logger import get_logger

ROOT = os.path.dirname(__file__)
logger = get_logger(
    __name__,
)

SAMPLE_RATE = 16_000
CHUNK_DURATION = 0.5
MAX_QUEUE_SIZE = 100


def mic_recorder_process_worker(
    recording_flag,
):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    audio_queue = queue.Queue(MAX_QUEUE_SIZE)
    MIC_OUTPUT_FILE_NAME = os.path.join("recs", "mic_out.wav")
    logger.debug(f"Mic audio will be saved to {MIC_OUTPUT_FILE_NAME}")

    def mic_recorder():
        try:
            with sc.get_microphone(
                id=str(sc.default_microphone().name), include_loopback=True
            ).recorder(samplerate=SAMPLE_RATE) as mic:
                while recording_flag.value:
                    try:
                        chunk = mic.record(numframes=int(SAMPLE_RATE * CHUNK_DURATION))
                        audio_queue.put(chunk[:, 0], True, 1)
                    except queue.Full:
                        logger.critical("Warning: Buffer full, data might be lost")
                    except Exception as e:
                        logger.error(f"Error in recording thread: {e}")
                        break
        finally:
            audio_queue.put(None)
            logger.debug("Recording thread finished")

    def mic_writer():
        with sf.SoundFile(
            MIC_OUTPUT_FILE_NAME,
            mode="w",
            samplerate=SAMPLE_RATE,
            channels=1,
        ) as file:
            while True:
                try:
                    chunk = audio_queue.get(block=True)
                    if chunk is None:
                        recording_flag.value = False
                        break

                    file.write(chunk)
                    audio_queue.task_done()

                except Exception as e:
                    logger.error(f"Error in writing thread: {e}")
                    break

    threads = []
    t1 = threading.Thread(target=mic_recorder)
    threads.append(t1)

    t2 = threading.Thread(target=mic_writer)

    threads.append(t2)

    t1.start()
    t2.start()

    for t in threads:
        t.join()
    logger.debug("mic recording done. Quiting")


def system_recorder_process_worker(
    recording_flag,
):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    audio_queue = queue.Queue(MAX_QUEUE_SIZE)
    SYSTEM_OUTPUT_FILE_NAME = os.path.join("recs", "sys_out.wav")
    logger.debug(f"System audio will be saved to {SYSTEM_OUTPUT_FILE_NAME}")

    def system_recorder():
        try:
            with sc.get_microphone(
                id=str(sc.default_speaker().name), include_loopback=True
            ).recorder(samplerate=SAMPLE_RATE) as sys_recorder:
                while recording_flag.value:
                    try:
                        chunk = sys_recorder.record(
                            numframes=int(SAMPLE_RATE * CHUNK_DURATION)
                        )
                        audio_queue.put(chunk[:, 0], True, 1)
                    except queue.Full:
                        logger.error(
                            "(system audio recording) Warning: Buffer full, data might be lost"
                        )
                    except Exception as e:
                        logger.error(f"Error in system audio recording thread: {e}")
                        break
        finally:
            audio_queue.put(None)
            logger.debug("Recording thread finished")

    def system_audio_writer():
        with sf.SoundFile(
            SYSTEM_OUTPUT_FILE_NAME,
            mode="w",
            samplerate=SAMPLE_RATE,
            channels=1,
        ) as file:
            while True:
                try:
                    chunk = audio_queue.get(block=True)
                    if chunk is None:
                        recording_flag.value = False
                        break
                    file.write(chunk)
                    audio_queue.task_done()

                except Exception as e:
                    logger.error(f"Error in system audio writing thread: {e}")
                    break

    threads = []
    t1 = threading.Thread(target=system_recorder)
    threads.append(t1)

    t2 = threading.Thread(target=system_audio_writer)
    threads.append(t2)

    t1.start()
    t2.start()

    for t in threads:
        t.join()
    logger.debug("system recording done. Quiting")
