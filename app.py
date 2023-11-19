import threading
from collections import deque
from dataclasses import dataclass
from typing import Optional

import gradio as gr
from PIL import Image

from constants import DESCRIPTION, LOGO
from gradio_examples import EXAMPLES
from model import get_pipeline
from utils import replace_background

MAX_QUEUE_SIZE = 4

pipeline = get_pipeline()


@dataclass
class GenerationState:
    prompts: deque
    generations: deque


def get_initial_state() -> GenerationState:
    return GenerationState(
        prompts=deque(maxlen=MAX_QUEUE_SIZE),
        generations=deque(maxlen=MAX_QUEUE_SIZE),
    )


def load_initial_state(request: gr.Request) -> GenerationState:
    print("Loading initial state for", request.client.host)
    print("Total number of active threads", threading.active_count())

    return get_initial_state()


async def put_to_queue(
    image: Optional[Image.Image],
    prompt: str,
    seed: int,
    strength: float,
    state: GenerationState,
):
    prompts_queue = state.prompts

    if prompt and image is not None:
        prompts_queue.append((image, prompt, seed, strength))

    return state


def inference(state: GenerationState) -> Image.Image:
    prompts_queue = state.prompts
    generations_queue = state.generations

    if len(prompts_queue) == 0:
        return state

    image, prompt, seed, strength = prompts_queue.popleft()

    original_image_size = image.size
    image = replace_background(image.resize((512, 512)))

    result = pipeline(
        prompt=prompt,
        image=image,
        strength=strength,
        seed=seed,
        guidance_scale=1,
        num_inference_steps=4,
    )

    output_image = result.images[0].resize(original_image_size)

    generations_queue.append(output_image)

    return state


def update_output_image(state: GenerationState):
    image_update = gr.update()

    generations_queue = state.generations

    if len(generations_queue) > 0:
        generated_image = generations_queue.popleft()
        image_update = gr.update(value=generated_image)

    return image_update, state


with gr.Blocks(css="style.css", title=f"Realtime Latent Consistency Model") as demo:
    generation_state = gr.State(get_initial_state())

    gr.HTML(f'<div style="width: 70px;">{LOGO}</div>')
    gr.Markdown(DESCRIPTION)
    with gr.Row(variant="default"):
        input_image = gr.Image(
            # tool="color-sketch",
            source="canvas",
            label="Initial Image",
            type="pil",
            height=512,
            width=512,
            brush_radius=40.0,
        )

        output_image = gr.Image(
            label="Generated Image",
            type="pil",
            interactive=False,
            elem_id="output_image",
        )
    with gr.Row():
        with gr.Column():
            prompt_box = gr.Textbox(label="Prompt", value=EXAMPLES[0])

    with gr.Accordion(label="Advanced Options", open=False):
        with gr.Row():
            with gr.Column():
                strength = gr.Slider(
                    label="Strength",
                    minimum=0.1,
                    maximum=1.0,
                    step=0.05,
                    value=0.8,
                    info="""
                    Strength of the initial image that will be applied during inference.
                    """,
                )
            with gr.Column():
                seed = gr.Slider(
                    label="Seed",
                    minimum=0,
                    maximum=2**31 - 1,
                    step=1,
                    randomize=True,
                    info="""
                    Seed for the random number generator.
                    """,
                )

    demo.load(
        load_initial_state,
        outputs=[generation_state],
    )
    demo.load(
        inference,
        inputs=[generation_state],
        outputs=[generation_state],
        every=0.1,
    )
    demo.load(
        update_output_image,
        inputs=[generation_state],
        outputs=[output_image, generation_state],
        every=0.1,
    )
    for event in [input_image.change, prompt_box.change, strength.change, seed.change]:
        event(
            put_to_queue,
            [input_image, prompt_box, seed, strength, generation_state],
            [generation_state],
            show_progress=False,
            queue=True,
        )

    gr.Markdown("## Example Prompts")
    gr.Examples(examples=EXAMPLES, inputs=[prompt_box], label="Examples")


if __name__ == "__main__":
    demo.queue(concurrency_count=20, api_open=False).launch(max_threads=1024, share=True)
