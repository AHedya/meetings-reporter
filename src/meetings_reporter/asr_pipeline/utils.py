import whisperx
import os
import wget
import string
import json
import pandas as pd
from collections import Counter, defaultdict
from typing import Literal
from omegaconf import OmegaConf
from nemo.collections.asr.models.msdd_models import NeuralDiarizer
from nemo.collections.asr.models import ClusteringDiarizer
from pyannote.core.segment import Segment
from pydub import AudioSegment


ROOT = os.path.dirname(__file__)


def load_audio(file_path):
    return whisperx.load_audio(file_path)


def transcribe(audio, model, device, compute_type, language, batch_size, **kwargs):
    model = whisperx.load_model(
        model, device, compute_type=compute_type, language=language
    )

    return model.transcribe(audio, batch_size=batch_size)


def align(
    result,
    audio,
    device,
):
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"], device=device
    )
    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )
    return result


def handle_diarization(
    audio_file_path,
    device,
    diarization_provider,
    nemo_dairizer_type="neural",
    min_speakers=2,
    max_speakers=6,
    **kwargs,
):
    match diarization_provider:
        case "nemo":
            nemo_diarization(audio_file_path, diarization_type=nemo_dairizer_type)
            diarize_segments = rttm_to_dataframe(
                os.path.join(
                    ROOT,
                    "outputs",
                    "pred_rttms",
                    f"{os.path.basename(audio_file_path).split('.')[0]}.rttm",
                )
            )
            return diarize_segments

        case "pyannote":
            diarize_model = whisperx.DiarizationPipeline(device=device)

            audio = whisperx.load_audio(audio_file_path)
            diarize_segments = diarize_model(audio)
            diarize_segments = diarize_model(
                audio, min_speakers=min_speakers, max_speakers=max_speakers
            )
            return diarize_segments
        case _:
            raise NotImplementedError(
                f"diarization providers are only [pyannote,NeMo] not {diarization_provider}"
            )


def nemo_diarization(
    audio_file_path, diarization_type: Literal["neural", "clustering"] = "neural"
):
    pretrained_vad = "vad_multilingual_marblenet"
    pretrained_speaker_model = "titanet_large"

    meta = {
        "audio_filepath": audio_file_path,
        "offset": 0,
        "duration": None,
        "label": "infer",
        "text": "-",
        "rttm_filepath": None,
        "uem_filepath": None,
    }

    with open(os.path.join(ROOT, "input_manifest.json"), "w", encoding="utf-8") as fp:
        json.dump(meta, fp)
        fp.write("\n")

    domain = "telephonic"
    MODEL_CONFIG = os.path.join(ROOT, f"diar_infer_{domain}.yaml")
    # check if available or download
    if not os.path.exists(MODEL_CONFIG):
        config_url = f"https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/speaker_tasks/diarization/conf/inference/diar_infer_{domain}.yaml"
        MODEL_CONFIG = wget.download(config_url, ROOT)

    config = OmegaConf.load(MODEL_CONFIG)
    config.num_workers = 0  # set to 1 if getting problems
    config.diarizer.manifest_filepath = os.path.join(ROOT, "input_manifest.json")
    config.diarizer.out_dir = os.path.join(ROOT, "outputs")
    config.diarizer.speaker_embeddings.model_path = pretrained_speaker_model
    config.diarizer.oracle_vad = False
    config.diarizer.clustering.parameters.oracle_num_speakers = False
    config.diarizer.vad.model_path = pretrained_vad
    config.diarizer.vad.parameters.onset = 0.8
    config.diarizer.vad.parameters.offset = 0.6
    config.diarizer.vad.parameters.pad_offset = -0.05

    match diarization_type:
        case "neural":
            config.diarizer.msdd_model.model_path = f"diar_msdd_{domain}"

            config.diarizer.msdd_model.parameters.sigmoid_threshold = [0.7, 1.0]
            model = NeuralDiarizer(cfg=config)
        case "clustering":
            model = ClusteringDiarizer(cfg=config)
    model.diarize()


def process_speaker(speaker: str) -> str:
    """match rttm speaker format(NeMo) into dataframe format (PyAnnote)
    example: speaker_1,speaker_2 -> SPEAKER_01,SPEAKER_02

    Args:
        speaker (str): _description_

    Returns:
        speaker (str): _description_
    """
    str_part, int_part = speaker.split("_")
    str_part = str_part.upper()
    int_part = str(int(int_part)).rjust(2, "0")
    return f"{str_part}_{int_part}"


def alpha_id_generator():
    """Alphabets ID generator

    Yields:
        str: ID
    """
    from itertools import product

    alphabet = string.ascii_uppercase
    for size in range(1, 5):
        for letters in product(alphabet, repeat=size):
            yield "".join(letters)


def rttm_to_dataframe(rttm_file):
    """Intermediate step to integrate NeMo diarizer with whisperX"""
    data = []
    label_generator = alpha_id_generator()

    # Open the RTTM file
    with open(rttm_file, "r") as file:
        for line in file:
            parts = line.strip().split()

            if parts[0] == "SPEAKER":
                start_time = float(parts[3])
                duration = float(parts[4])
                end_time = start_time + duration
                speaker = process_speaker(parts[7])

                segment = Segment(start_time, end_time)
                data.append(
                    [segment, next(label_generator), speaker, start_time, end_time]
                )

    df = pd.DataFrame(data, columns=["segment", "label", "speaker", "start", "end"])

    return df


def assign_word_speakers(diarize_segments, results):
    return whisperx.assign_word_speakers(diarize_segments, results)


def write_transcription(
    *,
    output_format,
    output_dir,
    result,
    audio_file_path,
):
    whisperx.utils.get_writer(output_format, output_dir)(
        result,
        audio_file_path,
        {"max_line_width": None, "max_line_count": None, "highlight_words": None},
    )


def process_srt(file_path, output_path=None, role_players=["Speaker1", "Speaker2"]):
    """Add more context to srt by changing (most frequent speaker) -> Speaker1
    While (rest speakers) -> Speaker2"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    speakers = Counter()

    speech_lines = []
    for i in range(2, len(lines), 4):
        line = lines[i].strip()
        if not line.startswith("[SPEAKER_"):
            continue
        speakers[line.split(":")[0]] += 1
        speech_lines.append(line)

    main_speaker = speakers.most_common(1)[0][
        0
    ]  # could be interviewer, instructor, teacher ...etc

    for idx in range(len(speech_lines)):
        parts = speech_lines[idx].split(":")
        if parts[0] == main_speaker:
            parts[0] = role_players[0]
        else:
            parts[0] = role_players[1]
        speech_lines[idx] = f"{parts[0]}: {parts[1].strip()}"

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "LLM_feed")
        if not os.path.exists(output_path):
            os.mkdir(output_path)
    audio_file = os.path.basename(file_path.split(".")[0])
    output_path = os.path.join(output_path, f"{audio_file}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        for line in speech_lines:
            f.write(line + "\n")
    return output_path


def extract_speakers_from_rttm(rttm_file, audio_file, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(
            ROOT,
            "exported_audio",
        )
    os.makedirs(output_dir, exist_ok=True)

    audio_filename = os.path.basename(audio_file)
    audio_name = os.path.splitext(audio_filename)[0]

    output_dir = os.path.join(output_dir, audio_name)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    try:
        audio = AudioSegment.from_file(audio_file)
    except Exception as e:
        raise FileNotFoundError(f"Looks like file: {rttm_file}") from e

    speaker_segments = defaultdict(list)

    try:
        with open(rttm_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 9 or parts[0] != "SPEAKER":
                    continue

                # file_id = parts[1]
                start_time = float(parts[3])  # in seconds
                duration = float(parts[4])  # in seconds
                speaker_id = parts[7]

                start_ms = int(start_time * 1000)
                duration_ms = int(duration * 1000)

                speaker_segments[speaker_id].append((start_ms, duration_ms))
    except Exception as e:
        raise ValueError("couldn't parse rttm file") from e

    output_files = {}

    for speaker_id, segments in speaker_segments.items():
        print(f"Processing speaker: {speaker_id} with {len(segments)} segments")
        segments.sort(key=lambda x: x[0])
        concatenated_audio = AudioSegment.empty()
        for start_ms, duration_ms in segments:
            if start_ms + duration_ms > len(audio):
                actual_duration = max(0, len(audio) - start_ms)
                if actual_duration > 0:
                    segment = audio[start_ms : start_ms + actual_duration]
                    concatenated_audio += segment
            else:
                segment = audio[start_ms : start_ms + duration_ms]
                concatenated_audio += segment

        output_filename = f"{audio_name}_{speaker_id}.wav"
        output_path = os.path.join(output_dir, output_filename)

        concatenated_audio.export(output_path, format="wav")
        print(f"Exported {output_path} ({len(concatenated_audio) / 1000:.2f}s)")
        output_files[speaker_id] = output_path

    return output_files


def calculate_speaker_durations(df):
    df["duration"] = df["end"] - df["start"]
    speaker_durations = df.groupby("speaker")["duration"].sum()

    return speaker_durations.to_dict()
