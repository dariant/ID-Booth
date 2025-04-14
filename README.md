# ID-Booth: Identity-consistent Face Generation with Diffusion Models

<div align="center">
  Darian Tomašević, Fadi Boutros, Chenhao Lin, Naser Damer, Peter Peer, Vitomir Štruc
  <br>
  <br>
  <a href='https://arxiv.org/abs/2403.11641'><img src='https://img.shields.io/badge/Paper-arXiv-red'></a>
  <a href='https://fg2025.ieee-biometrics.org/'><img src='https://img.shields.io/badge/Accepted_at-FG_2025-blue'></a>
  <br>
  <br>
</div>  
<div align="center">
        
</div>

This is the official implementation of the [ID-Booth framework](https://arxiv.org/abs/2504.07392), which:

&emsp;🔥 generates in-the-wild images of consenting identities captured in a constrained environment <br>
&emsp;🔥 uses a triplet identity loss to fine-tune Stable Diffusion for identity-consistent yet diverse image generation <br>
&emsp;🔥 can augment small-scale datasets to improve their suitability for training face recognition models  <br>

<br>

<div align="center">
  <p>
    <img width="80%" src="./assets/preview_framework.jpg">
  </p>
</div>
<div align="center">
  <p>
    <img width="80%" src="./assets/preview_samples.jpg">
  </p>
</div>


## <div align="center"> Installation </div>

```bash
conda create -n id-booth python=3.10
conda activate id-booth
pip install -r requirements.txt
```

## <div align="center"> Dowload links for pretrained models </div>

To generate images of identities found in the paper, download their fine-tuned [ID-Booth LoRA weights](https://unilj-my.sharepoint.com/:u:/g/personal/darian_tomasevic_fri1_uni-lj_si/EXnMuZvIG49HuNkOomD_2K8BNvba8f8kJcWb6M7hGPCA0w).
To create your own fine-tuned model with ID-Booth, download the pretrained [ArcFace recognition model](https://unilj-my.sharepoint.com/:u:/g/personal/darian_tomasevic_fri1_uni-lj_si/EfSmDfvsVlZEuOBqieDl4zEBJkTJ65aBnUtrC4q5nT2a-g?e=PBYj7o), and place the weights into the [ArcFace_files](https://github.com/dariant/ID-Booth/tree/main/ArcFace_files) directory.



## <div align="center"> Generating identity-specific images </div>

To generate images of a desired identity with [Stable Diffusion 2.1](https://huggingface.co/stabilityai/stable-diffusion-2-1), use the [diffusers](https://huggingface.co/docs/diffusers/index) library to load the corresponding LoRA weights, which were trained with the ID-Booth framework. The following example generates in-the-wild images of ID_1: 

```python
import torch
from diffusers import StableDiffusionPipeline, DDPMScheduler

base_model = "stabilityai/stable-diffusion-2-1-base"
lora_checkpoint =  "Trained_LoRA_Models/ID-Booth/ID_1/checkpoint-31-6400" # Download or train your own

prompt = "face portrait photo of male sks person, city street background"
negative_prompt = "cartoon, render, illustration, painting, drawing, black and white, bad body proportions, landscape"         

pipe = StableDiffusionPipeline.from_pretrained(base_model, torch_dtype=torch.float16).to("cuda:0")      
pipe.scheduler = DDPMScheduler.from_pretrained(base_model, subfolder="scheduler")
pipe.load_lora_weights(lora_checkpoint)
               
image = pipe(prompt=prompt,
              negative_prompt=negative_prompt,
              num_inference_steps=30,
              guidance_scale=5.0).images[0]

image.save(f"ID_1_{prompt}.png")
```
Results in the paper can be reproduced with data generated by the [inference_ID-Booth.py](https://github.com/dariant/ID-Booth/blob/main/inference_ID-Booth.py) script.



## <div align="center"> ID-Booth fine-tuning on new identities </div>

To perform ID-Booth fine-tuning of [Stable Diffusion 2.1](https://huggingface.co/stabilityai/stable-diffusion-2-1) on a new identity, you can follow the [train_ID-Booth.py](https://github.com/dariant/ID-Booth/blob/main/train_ID-Booth.py) script. The training dataset for a desired identity should include a handful of images along with ID embeddings extracted from these images with a pretrained ArcFace recognition model:
```
FACE_DATASET
└─── ID_1
│   └─── images
│   |       sample_0.png
│   |       sample_1.png
│   |       ...
│   └─── ArcFace_embeds
│           sample_0.pt
│           sample_1.pt
│           ...
└─── ID_2
└─── ...
```
The required ID embeddings can be extracted with the [extract_ArcFace_embeds.py](https://github.com/dariant/ID-Booth/blob/main/extract_ArcFace_embeds.py) script. 
Before running [train_ID-Booth.py](https://github.com/dariant/ID-Booth/blob/main/train_ID-Booth.py), specify the path to the source folder with identity images in [config_train_SD21.py](https://github.com/dariant/ID-Booth/blob/main/configs/config_train_SD21.py).


## <div align="center"> Evaluating the synthetic data </div>

For the evaluation of generated synthetic images, we rely on the following repositories:
* [dgm-eval](https://github.com/layer6ai-labs/dgm-eval) to measure quality, fidelity and diversity,
* [CR-FIQA](https://github.com/fdbtrs/CR-FIQA) to determine the face image quality,
* [6DRepNet](https://github.com/thohemp/6DRepNet) to estimate the pitch, yaw and roll of head poses,
* [PyEER](https://github.com/manuelaguadomtz/pyeer) to analyse identity consistency and separability.

Notebooks and scripts for reproducing the results in the paper can be found in the [Evaluation](https://github.com/dariant/ID-Booth/tree/main/Evaluation) directory, while fine-tuned LoRA weights of different approaches can be downloaded [here](https://unilj-my.sharepoint.com/:f:/g/personal/darian_tomasevic_fri1_uni-lj_si/Esv2DimWDExAtkBjx-6SDoMBvP4TiD_N-gBaPhf10ekKrA?e=BCKzQb). 

To also evaluate the utility of the produced data, we also use it to train a deep face recognition model, following the [train_FR.py](https://github.com/dariant/ID-Booth/blob/main/FR_training/train_FR.py) script. The performance of these models is then evaluated on state-of-the-art verification benchmarks with [test_FR.py](https://github.com/dariant/ID-Booth/blob/main/FR_training/test_FR.py).  


## Citation

If you use the code or results from this repository, please cite the ID-Booth paper:

```
@article{tomasevic2025IDBooth,
  title={{ID-Booth}: Identity-consistent Face Generation with Diffusion Models},
  author={Toma{\v{s}}evi{\'c}, Darian and Boutros, Fadi and Lin, Chenhao and Damer, Naser and {\v{S}}truc, Vitomir and Peer, Peter},
  journal={arXiv preprint arXiv:2504.07392},
  year={2025}
}
```

## Acknowledgements

Supported in parts by the Slovenian Research and Innovation Agency (ARIS) through the Research Programmes P2-0250 (B) "Metrology and Biometric Systems" and P2--0214 (A) “Computer Vision”, the ARIS Project J2-50065 "DeepFake DAD" and the ARIS Young Researcher Programme.

<img src="./assets/ARIS_logo_eng_resized.jpg" alt="ARIS_logo_eng_resized" width="400"/>



