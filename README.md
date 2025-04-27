# meetings-reporter
## Table of Contents

- Overview
- Getting Started
- Interfaces
  - Recorder
  - ASR (Automatic Speech Recognition)
  - Pipeline (All-in-One)
- Troubleshooting
- Contributing
- License
- Acknowledgments
- Development Tasks

**meetings-reporter** is an all-in-one solution for recording meetings, transcribing audio, diarizing speakers, and generating meeting reports.
The project is modular, consisting of three packages, each can be used independently or together as a complete pipeline.
![ProjectArchitecture](https://github.com/user-attachments/assets/a087b176-a1d9-42b6-a53b-0abb04b0482a)

## Overview
`meetings-reporter` is an all-in-one tool for recording, transcribing, and generating reports from meetings. It consists of three independent packages:
- **Recorder**: Captures audio from microphone and system.
- **ASR**: Transcribes audio, aligns text, and performs speaker diarization.
- **Pipeline**: Combines recording, transcription, and report generation.

The tool is particularly effective for Arabic audio when using the NeMo diarizer, thanks to its training on diverse datasets, including Arabic speech.

## Getting Started

To set up the project, follow these steps:

1. **Install** `uv`: `uv` is a Python project management tool, similar to `poetry` or `pipenv`. Install it with `pip install uv` (uv documentation).

2. **Create a virtual environment**:

   ```bash
   uv venv --python 3.12
   ```

3. **Activate the virtual environment**:

   ```bash
   .venv\Scripts\activate
   ```

4. **Install dependencies**:

   - For the audio recorder only:

     ```bash
     uv sync
     ```

     This installs the core dependencies listed in `pyproject.toml`.

   - For the full project (including transcription and reporting):

     ```bash
     uv sync --all-extras
     ```

     This installs all optional dependencies.

## Interfaces

### Recorder

The Recorder captures audio from your microphone and system. Run it with:

```bash
uv run recorder [options]
```

**Options**:

| Option | Description |
| --- | --- |
| `-o, --output-dir` | Directory to save recordings (default: `recs`). |
| `-k, --keep-temp-recording` | Keep temporary recording files. |
| `--mic-amplify` | Microphone amplification in dB (default: 4 dB). |

### ASR (Automatic Speech Recognition)

The ASR module transcribes audio, aligns text, and performs speaker diarization. It supports Arabic audio effectively with the NeMo diarizer. Run it with:

```bash
uv run asr [options]
```

**Options**:

| Option | Description |
| --- | --- |
| `-i, --audio_file_path` | Path to the input audio file. |
| `-td, --transcription_dir` | Directory to save transcription output. |
| `--get_num_speakers` | Automatically detect the number of speakers. |
| `--model` | Transcription model (default: Whisper large-v3). |
| `--device` | Device to use (e.g., `cuda`, `cpu`). |
| `--language` | Language of the audio (e.g., `en`, `ar`). |
| `--diarization_provider` | Diarization method (e.g., `nemo`, `pyannote`). |
| `--nemo_diarizer_type` | NeMo diarizer type (`neural`, `clustering`). |
| `--export_diarized_audio` | Export diarized audio segments. |
| `--diarized_audio_path` | Path to save diarized audio. |
| `--min_speakers` | Minimum number of speakers. |
| `--max_speakers` | Maximum number of speakers. |
| `--output_format` | Output format (e.g., `srt`, `all`). |
| `--role_players` | Assign roles to speakers (e.g., "Manager", "Team Member"). |

For more details on Whisper, see Whisper documentation. For diarization, see NeMo documentation and pyannote documentation.

### Pipeline (All-in-One)

The Pipeline combines recording, transcription, and report generation. Run it with:

```bash
uv run pipeline --api_key YOUR_API_KEY [options]
```

**Options**:

| Option | Description |
| --- | --- |
| `--temperature` | Model temperature for report generation. |
| `--model_provider` | Model provider (currently Google). |
| `--api_key` | API key for Google Cloud services (Google Cloud Console). |
| `--MODEL_ID` | Model ID for report generation. |
| `--no_report` | Skip report generation. |
| `--no_record` | Skip recording. |


## Contributing

We welcome contributions to improve `meetings-reporter`! To contribute:

- Fork the repository: Fork on GitHub
- Create a feature branch: `git checkout -b feature-branch`
- Commit your changes: `git commit -m "Add feature"`
- Push to your fork: `git push origin feature-branch`
- Create a pull request: Open a PR
- Report issues: Create an issue


## Troubleshooting
 Currently tested only on Windows with Python 3.12, 3.13. Contributions for other platforms are welcome!
<details>
<summary> AttributeError: module 'signal' has no attribute 'SIGKILL'. Did you mean: 'SIGILL'? </summary>
Go to error line, modify 'SIGKILL' to 'SIGILL'.
</details>

<details>
<summary> Could not locate cudnn_ops_infer64_8.dll. Please make sure it is in your library path! </summary>
  
  1- Download cuDNN v8.9.7 for cuda 12.x https://developer.nvidia.com/rdp/cudnn-archive
  
  2. Open the folder location of ctranslate2 which has a file "cudnn64_8.dll" in it
`pip show ctranslate2`

  3. From the cuDNN zip file, open bin/ and copy all files into the ctranslate2 folder, replace if needed

  shoutout (https://github.com/mlallan1307)
</details>

<details>
<summary> getting pickle error </summary>
change num workers from 0 to 1
</details>

## Acknowledgments
- Special thanks to mlallan1307 for solving cuDNN issue.

## Development Tasks

- [ ] Refactor into an object-oriented programming (OOP) structure.

- [ ] Add support for more large language models (LLMs) in `report_builder`.

- [ ] Expand platform support (e.g., Linux, macOS).
