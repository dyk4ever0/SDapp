import torch
from diffusers import StableDiffusionPipeline
from torch import autocast
import streamlit as st
from PIL import Image, ImageEnhance
import pandas as pd
import numpy as np


class StableDiffusionLoader:
    """
    Stable Diffusion loader and generator class.

    Utilises the stable diffusion models from the `Hugging Face`(https://huggingface.co/spaces/stabilityai/stable-diffusion) library

    Attributes
    ----------
    prompt : str
        a text prompt to use to generate an associated image
    pretrain_pipe : str
        a pretrained image diffusion pipeline i.e. CompVis/stable-diffusion-v1-4

    """

    def __init__(self,
                 prompt: str,
                 pretrain_pipe: str = 'CompVis/stable-diffusion-v1-4'):
        """
        Constructs all the necessary attributes for the diffusion class.

        Parameters
        ----------
            prompt : str
                the prompt to generate the model
            pretrain_pipe : str
                the name of the pretrained pipeline
        """
        self.prompt = prompt
        self.pretrain_pipe = pretrain_pipe
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if self.device == 'cpu':
            raise MemoryError('GPU need for inference')

        assert isinstance(self.prompt, str), 'Please enter a string into the prompt field'
        assert isinstance(self.pretrain_pipe,
                          str), 'Please use value such as `CompVis/stable-diffusion-v1-4` for pretrained pipeline'

    def generate_image_from_prompt(self, save_location='prompt.jpg', use_token=False,
                                   verbose=False):
        """
        Class method to generate images based on the prompt

        Parameters
        ----------
            save_location : str - defaults to prompt.jpg
                the location where to save the image generated by the Diffusion Model
            use_token : bool
                boolean to see if Hugging Face token should be used
            verbose : bool
                boolean that defaults to False, otherwise message printed
        """

        pipe = StableDiffusionPipeline.from_pretrained(
            self.pretrain_pipe,
            revision="fp16", torch_dtype=torch.float16,
            use_auth_token=use_token
        )
        pipe = pipe.to(self.device)
        with autocast(self.device):
            image = pipe(self.prompt)[0][0]
        image.save(save_location)
        if verbose:
            print(f'[INFO] saving image to {save_location}')
        return image

    def __str__(self) -> str:
        return f'[INFO] Generating image for prompt: {self.prompt}'

    def __len__(self):
        return len(self.prompt)


if __name__ == '__main__':

    SAVE_LOCATION = 'prompt.jpg'
    # Create the page title
    st.set_page_config(page_title='Diffusion Model generator', page_icon='fig/favicon.ico')
    # Create page layout
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    st.title('Image generator - Stable Diffusion')
    st.caption('An app to generate images based on text prompts with a :blue[_Stable Diffusion_] model')
    # Create a sidebar with text examples
    with st.sidebar:
        # Selectbox
        st.image('fig/hf.png')
        add_selectbox = st.sidebar.selectbox(
            "Prompt examples",
            (
                "Style 1",
                "Style 2",
            ), index=0)
        st.markdown('Use the above drop down box to generate _prompt_ examples')
        st.text('SD Streamlit app ver1')

    # Create text prompt
    prompt = st.text_input('Input the prompt desired')
    if add_selectbox != 'None' or prompt is None:
        prompt = add_selectbox

    # Handle if the text box does not have any content in
    if len(prompt) > 0:
        st.markdown(f"""
        This will show an image using **stable diffusion** of the desired {prompt} entered:
        """)
        print(prompt)
        # Create a spinner to show the image is being generated
        with st.spinner('Generating image based on prompt'):
            sd = StableDiffusionLoader(prompt)
            sd.generate_image_from_prompt(save_location=SAVE_LOCATION)
            st.success('Generated stable diffusion model')

        #  Open and display the image on the site
        image = Image.open(SAVE_LOCATION)
        st.image(image)
