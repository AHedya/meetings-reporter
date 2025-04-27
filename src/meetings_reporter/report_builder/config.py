from pydantic import BaseModel, Field


class llm_config(BaseModel):
    temperature: float = Field(0.3)
