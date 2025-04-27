import os
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from ..my_logger import get_logger
from .config import llm_config
from .step import Step
from .prompts import (
    REFINER_PROMPTS,
    TRANSLATION_PROMPTS,
    MEETINGS_PROMPTS,
)


logger = get_logger()


steps = [
    {
        "name": "refiner",
        "system_prompt": REFINER_PROMPTS[-1],
        "model_id": "gemini-2.5-flash-preview-04-17",
        "config": llm_config(temperature=0.2).model_dump(),
    },
    {
        "name": "analyst",
        "system_prompt": MEETINGS_PROMPTS[-1],
        "model_id": "gemini-2.5-pro-exp-03-25",
        "config": llm_config(temperature=0.3).model_dump(),
    },
]


def report_pipeline(
    model_feed_file_path: str,
    api_key,
    report_header: str = "",
    reports_directory="reports",
    save_history=False,
    **kwargs,
):
    report_file_name = (
        os.path.splitext(os.path.basename(model_feed_file_path))[0] + ".txt"
    )
    context = load_context(model_feed_file_path)
    logger.info("reporting...")

    response_history = []
    analysis_history = []
    start = time.perf_counter()
    for cfg in steps:
        response_history.append(f"\n\nINPUT:\n{context}")

        step_begin = time.perf_counter()

        step = Step(
            name=cfg["name"],
            system_prompt=cfg["system_prompt"],
            model_id=cfg["model_id"],
            model=get_llm(
                api_key,
                cfg["model_id"],
            ),
            config=cfg["config"],
        )
        response, analytics = step(context)

        # Record histories
        response_history.append(f"\n\OUTPUT:\n{response}")

        context = response
        timing = f"Time lapsed: {(time.perf_counter() - step_begin):.3f} for step: {cfg['name']}"
        logger.info(timing)
        analytics += timing
        analysis_history.append(analytics)

    end = time.perf_counter()

    logger.info(f"Time lapsed: {(end - start):.4f}s")
    analytics = "\n\n".join(analysis_history)

    if report_header:
        analytics += f"\n{report_header}"
    final_report = f"{analytics}\n\n{context}"

    os.makedirs(reports_directory, exist_ok=True)
    final_report_path = os.path.join(reports_directory, "report_" + report_file_name)
    with open(final_report_path, "w", encoding="utf-8") as fp:
        fp.write(final_report)

    if save_history:
        logger.info("saving history")
        with open(
            os.path.join(reports_directory, f"history_{report_file_name}"),
            "w",
            encoding="utf-8",
        ) as fp:
            fp.write(("\n").join(response_history))
    return final_report_path


def load_context(file_path):
    with open(file_path, "r", encoding="utf-8") as fp:
        llm_feed = fp.read().strip()
    return llm_feed


def get_llm(api_key, model_id: str = "gemini-2.0-flash-lite"):
    return ChatGoogleGenerativeAI(model=model_id, google_api_key=api_key)
