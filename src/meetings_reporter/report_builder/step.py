from dataclasses import dataclass
from langchain_core.language_models import BaseChatModel
import yaml
import os

from langchain_core.messages import SystemMessage, HumanMessage
from typing import Any

ROOT = os.path.dirname(__file__)


with open(os.path.join(ROOT, "pricing.yaml"), "r", encoding="utf-8") as fp:
    PRICING = yaml.safe_load(fp)


@dataclass
class Step:
    name: str
    system_prompt: str
    model: BaseChatModel
    model_id: str
    config: Any

    def __call__(self, context):
        messages = [SystemMessage(self.system_prompt), HumanMessage(context)]
        response = self.model.invoke(messages, config=self.config)
        in_tokens = response.usage_metadata["input_tokens"]
        out_tokens = response.usage_metadata["output_tokens"]
        analytics = f"""num input tokens: {in_tokens}, num output tokens: {out_tokens}
{calc_cost(in_tokens, out_tokens, self.model_id)}
STEP: {self.name}"""
        return response.text(), analytics


def calc_cost(in_tokens, out_tokens, model_id=None):
    in_price, out_price = PRICING[model_id]
    in_price *= in_tokens / 1_000_000
    out_price *= out_tokens / 1_000_000

    return f"Cost: input: ${in_price:.4f} output: ${out_price:.4f}.\tTotal: ${(in_price + out_price):.3f}"
