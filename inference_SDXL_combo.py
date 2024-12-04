from diffusers import StableDiffusionPipeline
import torch
import os 
from torchvision.utils import save_image
from diffusers import DPMSolverMultistepScheduler
from diffusers import DDPMScheduler
import random 
from accelerate.utils import  set_seed
from tqdm import tqdm 
import re 
import json 
#from compel import Compel
from diffusers import AutoPipelineForText2Image
from itertools import product 

def atoi(text):
        return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

backgrounds_list = ["", "forest", "city street", "beach", "office", "bus", "laboratory", "factory", "construction site", "hospital", "night club"]
backgrounds_list = [f"busy {b} environment"  if b != "" else "" for b in backgrounds_list]#
#backgrounds = [f"busy {b} environment"  if b != "" else "" for b in backgrounds]#

#expression_list = ["", "happy", "smiling", "crying", "shocked", "disgusted", "scared"]# "sad", "frowning", "surprised", "angry"]
#expression_list = ["", "smiling", "laughing", "screaming","grieving", "crying", "sad expression", "enraged expression", "shocked"]# "" "rage", "sadness", "anger"]# "sad", "frowning", "surprised", "angry"]
#expression_list = ["", "smile", "laugh", "scream","grieve", "cry", "sad", "rage", "shock", "scared"]# "" "rage", "sadness", "anger"]# "sad", "frowning", "surprised", "angry"]

#expression_list = ["", "smiling", "laughing", "crying", "angry"]# "" "rage", "sadness", "anger"]# "sad", "frowning", "surprised", "angry"]
#expression_list = ["", "happy expression", "sad expression", "angry expression"]# "" "rage", "sadness", "anger"]# "sad", "frowning", "surprised", "angry"]
#expression_list = ["", "smiling", "laughing", "frowning", "yelling", "crying", "raised eyebrows"]# "" "rage", "sadness", "anger"]# "sad", "frowning", "surprised", "angry"]
#expression_list = ["happy expression", "smirk expression", "tears expression", "rage expression", "surprised expression"]
#expression_list = ["", "happy", "smiling", "laughing", "sad", "crying", "angry", "yelling", "frowning", "shocked", "scared"]# "sad", "frowning", "surprised", "angry"]
#expression_list = ["neutral", ""]#"surprised", "disgusted", "shocked"]# "happy", "smiling", "laughing", "sad", "crying", "angry", "yelling", "frowning", "shocked", "scared"]# "sad", "frowning", "surprised", "angry"]
# expression_list = ["", "happy", "sad", "angry", "shocked"]
#expression_list = ["", "happy", "crying", "enraged", "scared"]
# expression_list = ["neutral", "happy", "sad", "angry", "surprised", "fearful", "disgusted"]
# expression_list = ["shocked", "smiling", "laughing", "enraged", "contemptous"]
# expression_list = ["smirking", "crying", "ashamed"]
expression_list = ["neutral", "happy", "sad", "angry", "shocked"]# "crying", "ashamed"]

# expression_list = ["neutral", "happiness", "sadness", "anger", "surprise", "fear", "disgust"]
expression_list = [f"{e} expression"  if e != "" else "" for e in expression_list]# "sad", "frowning", "surprised", "angry"]
#expression_list = [""]# "sad", "frowning", "surprised", "angry"]


#expression_list = [f"{e} expression"  if e != "" else "" for e in expression_list]# "sad", "frowning", "surprised", "angry"]
# TODO clean shaven?

# TODO important 
add_gender = False 
# additions_list = expression_list
additions_list = [backgrounds_list, expression_list]

num_samples_per_prompt = 1
num_prompts = 5 #50 #21 #len(additions_list)
device = "cuda:0"

seed = 0 
guidance_scale = 5.0
num_inference_steps = 30 #30

folder_of_models = "OUTPUT_MODELS/12-2024_SDXL_LoRA4"
checkpoint =  "checkpoint-200" # "checkpoint-8-1800"#18-3800" # 8-1800 best so far .... # 12? in between? 

models_to_test = ["No_new_Loss"]#, "DB_SDXL_LoRA_Tufts_10_07_identity_loss_NoIDWeighting", "DB_SDXL_LoRA_Tufts_10_07_triplet_prior_loss_NoIDWeighting"]
# models_to_test = ["DB_SDXL_LoRA_Tufts_10_07_No_new_Loss", "DB_SDXL_LoRA_Tufts_10_07_identity_loss_NoIDWeighting"]
# models_to_test = ["DB_SDXL_LoRA_Tufts_10_07_No_new_Loss"]
architectures = ["stabilityai/stable-diffusion-xl-base-1.0"]
model_architecture = architectures[0]
arch = model_architecture.split("/")[1]

folder_output = "GENERATED_SAMPLES"



face_alterations = ["", "curly hair", "long hair", "short hair", "face tattoos", "sunglasses"]
# face_alterations = [f"with {alter}" if alter != "" else alter for alter in face_alterations]

#clothing = ["", "turtleneck", "sweater", "t-shirt", "shirt", "suit", "hat and sunglasses", "glasses"]
#clothing = [f"wearing a {cloth}" if cloth != "" else cloth for cloth in clothing]
# does it need "wearing a"
# TODO ... do we even need clothing (it changes randomly does it not?)

#backgrounds = ["", "forest", "brick wall", "busy street", "beach", "office", "shopping mall"]

ages = ["", "20", "30", "40", "50", "60"]
ages = [f"{a} years old" for a in ages]

set_seed(seed)


width, height = 1024, 1024

ids = os.listdir(os.path.join(folder_of_models, models_to_test[0]))
ids = [i for i in ids if ".json" not in i]
ids.sort(key=natural_keys)
#ids = ids[3:15]
#ids = ids[0:1]

#ids = ["ID_1", "ID_2", "ID_3"]
print(ids)
# with open("tufts_512_poses_1-7_all_imgs_jpg_per_ID/gender_dict.json", "r") as fp:
#     gender_dict = json.load(fp)
gender_dict = dict()
# ids = ids[:1]

negative_prompt = "cartoon, cgi, render, illustration, painting, drawing, black and white, bad body proportions, landscape" # "cartoon, cgi, render, illustration, painting, drawing, black and white, bad body proportions" #"blurry, fake skin, plastic skin, cartoon, grayscale, painting, monochrome"
# original_prompt =  "photo of sks person"#, aligned close-up portrait""#,  50 years old, sunglasses, forest"#, face tattoos"#, 10 years old"
original_prompt = f"photo of sks person, close-up portrait"

# generate seeds for each prompt number 
num_seeds = len(ids) 

all_prompt_combinations = list(product(backgrounds_list, expression_list))

prompt = ""
for id_number, which_id in enumerate(ids):
    print("\n", which_id) 

    if add_gender: 
        gender = gender_dict[which_id]
        if gender == "M": gender = "male"
        elif gender == "F": gender = "female"
    

    # all_prompts_for_id = [[random.choice(additions_list[0]), random.choice(additions_list[1])] for i in range(num_prompts)]
    all_prompts_for_id = random.sample(all_prompt_combinations, num_prompts)
    #print(all_prompts_for_id)
    #exit()

    comparison_image_list = [] 
    for model_name in models_to_test:
        full_model_path = os.path.join(folder_of_models, model_name, which_id, checkpoint)

        output_dir = os.path.join(folder_output, model_name)#"GENERATED_SAMPLES/FINAL_No_ID_loss_TEST"
        print("Load:", full_model_path)
        
        
        pipe = AutoPipelineForText2Image.from_pretrained(model_architecture, torch_dtype=torch.float16).to(device)
        
        #print("original scheduler:", pipe.scheduler.config)
        pipe.scheduler = DDPMScheduler.from_pretrained(model_architecture, subfolder="scheduler")
        #print("New scheduler:", pipe.scheduler.config)
        pipe.load_lora_weights(full_model_path)
        pipe.set_progress_bar_config(disable=True)

        #compel_proc = Compel(tokenizer=pipe.tokenizer, text_encoder=pipe.text_encoder)
        #prompt_embeds = compel_proc(f"{prompt}.and()")
        
        os.makedirs(output_dir, exist_ok=True)
        generator = torch.Generator(device=device).manual_seed(id_number) 

        for i, num_prompt in enumerate(tqdm(range(num_prompts))):     
            
            #prompt_additions = [additions_list[i]]
            #prompt_additions = [random.choice(additions_list[0]), random.choice(additions_list[1])]
            prompt_additions = all_prompts_for_id[i]
            prompt = original_prompt
            
            if add_gender: prompt = prompt.replace(" sks person", f" {gender} sks person")
            if len(prompt_additions) != 0:
                for addition in prompt_additions:
                    if addition != "":
                        prompt += f", {addition}"

            #print(prompt)
            # generate samples
            for j in range(num_samples_per_prompt):
                
                output = pipe(prompt=prompt, negative_prompt=negative_prompt,  output_type="np", generator=generator, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale, width=width, height=height)
                output = torch.Tensor(output.images)
                comparison_image_list.append(output)
                output = torch.permute(output, (0, 3, 1, 2))
                path_to_output = f"{output_dir}/{which_id}_{checkpoint}_{arch}"
                os.makedirs(path_to_output, exist_ok=True)
                save_image(output, fp=f"{path_to_output}/{i}_{j}_{prompt}.png")
        
    images = torch.cat(comparison_image_list)
    images = torch.permute(images, (0, 3, 1, 2)) # permute dimensions to be (x, 3, 512, 512)
    #print(images.shape)
    #exit()
    print("Saving comparison image") 
    comparison_folder = os.path.join(folder_output, "COMPARISON_IMAGES_SDXL")
    os.makedirs(comparison_folder, exist_ok=True)
    save_path = f"{comparison_folder}/{which_id}_{checkpoint}_{arch}_{guidance_scale}.jpg"
    print(save_path)
    save_image(images, fp=save_path, nrow=num_prompts*num_samples_per_prompt, padding=10)
    #break
