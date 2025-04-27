from pydantic import BaseModel, Field
from typing import Literal, List


class asr_config(BaseModel):
    model: str = Field("large-v3")
    device: Literal["cuda", "cpu"] = Field("cuda")
    compute_type: str = Field("float16", description="convert to int8 if using cpu")
    batch_size: int = Field(16)
    language: str = Field("ar")
    diarization_provider: Literal["nemo", "pyannote"] = Field("nemo")
    nemo_dairizer_type: Literal["neural", "clustering"] = Field("neural")
    accomulate_chunks: bool = Field(False)
    min_speakers: int = Field(2)
    max_speakers: int = Field(6)
    output_format: str = Field("srt")
    # adding more context to the trasncription
    role_players: List[str] = Field(["Speaker_1", "Speaker_2"])
