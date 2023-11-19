from typing import Any


def get_pipeline():
    import torch
    from diffusers import AutoencoderTiny, AutoPipelineForImage2Image

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    pipe = AutoPipelineForImage2Image.from_pretrained(
        "SimianLuo/LCM_Dreamshaper_v7",
        use_safetensors=True,
    )
    pipe.vae = AutoencoderTiny.from_pretrained(
        "madebyollin/taesd",
        torch_dtype=torch_dtype,
        use_safetensors=True,
    )
    pipe = pipe.to(device, dtype=torch_dtype)
    pipe.unet.to(memory_format=torch.channels_last)
    return pipe


def get_test_pipeline():
    from PIL import Image
    from dataclasses import dataclass
    import random
    import time

    @dataclass
    class Images:
        images: list[Image.Image]

    class Pipeline:
        def __call__(self, *args: Any, **kwds: Any) -> Any:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)

            return Images(images=[Image.new("RGB", (512, 512), color=(r, g, b))])

    return Pipeline()
