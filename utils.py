import os
import base64
import requests
import ast
from openai import OpenAI

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def run_dalle(prompt, no_rewrite=False):
    client = OpenAI()
    updated_prompt = 'My prompt has full detail so no need to add more: '+prompt if no_rewrite else prompt

    response = client.images.generate(
      model="dall-e-3",
      prompt=updated_prompt,
      size="1024x1024",
      quality="standard",
      n=1,
    )

    return response.dict()


def craft_prompt(prompt):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Create a Dall-E 3 prompt for me with the following requirements. {prompt}"},
                ],
            }
        ],
        max_tokens=300,
    )
    return response.dict()


def download_image(image_url):
    return requests.get(image_url).content


def create_variation_dalle(name, prompt, no_rewrite=False):
    import base64
    dalle_result = run_dalle(prompt, no_rewrite)
    url = dalle_result['data'][0]['url']
    image_bin = download_image(url)
    return {
        'name': name,
        'dalle': dalle_result,
        'image': base64.b64encode(image_bin).decode('utf8'),
        'image256': base64.b64encode(reduce_size(image_bin, 4)).decode('utf8'),
    }


def create_variation(name, desc, no_rewrite=False):
    import base64
    craft_prompt_result= craft_prompt(desc)
    prompt = craft_prompt_result['choices'][0]['message']['content'].strip()
    dalle_result = run_dalle(prompt, no_rewrite)
    url = dalle_result['data'][0]['url']
    image_bin = download_image(url)
    return {
        'name': name,
        'craft_prompt': craft_prompt_result,
        'dalle': dalle_result,
        'image': base64.b64encode(image_bin).decode('utf8'),
        'image256': base64.b64encode(reduce_size(image_bin, 4)).decode('utf8'),
    }


def reduce_size(image_bin, ratio):
    import numpy as np
    from PIL import Image
    from io import BytesIO
    # Load your image
    img = Image.open(BytesIO(image_bin))
    img_array = np.array(img)
    new_size = tuple(map(lambda x: x // ratio, img.size))
    mid = ratio//2 - 1

    # Initialize an empty array for the reduced image
    reduced_img_array = np.empty((new_size[0], new_size[1], 3), dtype=np.uint8)  # Assuming a 3-channel RGB image

    # Loop over every 2x2 block and take the upper-left pixel
    for i in range(0, img.size[0], ratio):
        for j in range(0, img.size[1], ratio):
            reduced_img_array[i//ratio, j//ratio] = img_array[i + mid, j + mid]

    # Convert the reduced array back to an image
    reduced_img = Image.fromarray(reduced_img_array)

    with BytesIO() as img_bytes:
        # Save the image to the BytesIO object, specifying the format if necessary
        reduced_img.save(img_bytes, format='PNG')  # You can change 'PNG' to your desired format
        
        return img_bytes.getvalue()


def enlarge_size(image_bin, ratio):
    import numpy as np
    from PIL import Image
    from io import BytesIO
    # Load your image
    img = Image.open(BytesIO(image_bin))
    img_array = np.array(img)
    new_size = tuple(map(lambda x: x * ratio, img.size))

    enlarged_img_array = np.empty((new_size[0], new_size[1], 3), dtype=np.uint8)  # Assuming a 3-channel RGB image

    for i in range(0, img.size[0]):
        for j in range(0, img.size[1]):
            for k in range(0, ratio):
                for l in range(0, ratio):
                    enlarged_img_array[i*ratio+k, j*ratio+l] = img_array[i, j]

    enlarged_img = Image.fromarray(enlarged_img_array)

    with BytesIO() as img_bytes:
        # Save the image to the BytesIO object, specifying the format if necessary
        enlarged_img.save(img_bytes, format='PNG')  # You can change 'PNG' to your desired format
        
        return img_bytes.getvalue()