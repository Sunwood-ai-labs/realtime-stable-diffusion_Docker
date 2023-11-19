import json
from collections import deque
from dataclasses import dataclass
import threading
from typing import Optional

import gradio as gr
import websockets
from gradio.processing_utils import decode_base64_to_image, encode_pil_to_base64
from PIL import Image
from websockets.sync.client import connect

from constants import DESCRIPTION, WS_ADDRESS, LOGO
from utils import replace_background

from gradio_examples import EXAMPLES

MAX_QUEUE_SIZE = 4


@dataclass
class GenerationState:
    prompts: deque
    responses: deque


def get_initial_state() -> GenerationState:
    return GenerationState(
        prompts=deque(maxlen=MAX_QUEUE_SIZE),
        responses=deque(maxlen=MAX_QUEUE_SIZE),
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


def send_inference_request(state: GenerationState) -> Image.Image:
    prompts_queue = state.prompts
    response_queue = state.responses

    if len(prompts_queue) == 0:
        return state

    image, prompt, seed, strength = prompts_queue.popleft()
    original_image_size = image.size
    image = replace_background(image.resize((512, 512)))

    arguments = {
        "prompt": prompt,
        "image_url": encode_pil_to_base64(image),
        "strength": strength,
        "negative_prompt": "cartoon, illustration, animation. face. male, female",
        "seed": seed,
        "guidance_scale": 1,
        "num_inference_steps": 4,
        "sync_mode": 1,
        "num_images": 1,
    }

    connection = connect(WS_ADDRESS)
    connection.send(json.dumps(arguments))

    try:
        response = json.loads(connection.recv())
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed, reconnecting...")
        # TODO: This is a hacky way to reconnect, but it works for now
        #      Ideally, we should be able to reconnect to the same connection
        #      and not have to create a new one
        connection = connect(WS_ADDRESS)
        try:
            response = json.loads(connection.recv())
        except websockets.exceptions.ConnectionClosedOK:
            print("Connection closed again, aborting...")
            return state

    # TODO: If a new connection is created, the response do not contain the images.
    if "images" in response:
        response_queue.append((response, original_image_size))

    return state


def update_output_image(state: GenerationState):
    image_update = gr.update()
    inference_time_update = gr.update()

    response_queue = state.responses

    if len(response_queue) > 0:
        response, original_image_size = response_queue.popleft()
        generated_image = decode_base64_to_image(response["images"][0]["url"])
        inference_time = response["timings"]["inference"]

        image_update = gr.update(value=generated_image.resize(original_image_size))
        inference_time_update = gr.update(value=round(inference_time, 4))

    return image_update, inference_time_update, state


with gr.Blocks(css="style.css", title=f"Realtime Latent Consistency Model") as demo:
    generation_state = gr.State(get_initial_state())

    gr.HTML(f'<div style="width: 70px;">{LOGO}</div>')
    gr.Markdown(DESCRIPTION)
    with gr.Row(variant="default"):
        input_image = gr.Image(
            tool="color-sketch",
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
        with gr.Column(scale=23):
            prompt_box = gr.Textbox(label="Prompt", value=EXAMPLES[0])
        with gr.Column(scale=1):
            inference_time_box = gr.Number(
                label="Inference Time (s)", interactive=False
            )

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
        send_inference_request,
        inputs=[generation_state],
        outputs=[generation_state],
        every=0.1,
    )
    demo.load(
        update_output_image,
        inputs=[generation_state],
        outputs=[output_image, inference_time_box, generation_state],
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
    demo.queue(concurrency_count=20, api_open=False).launch(max_threads=4096)
