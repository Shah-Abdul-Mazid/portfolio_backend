import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras.preprocessing.image import save_img
import random
import shutil

input_folder = 'D:\\CSETEST\\BD-Freshwater-Fish'
output_folder = 'D:\\CSETEST\\BD-Freshwater-Fish-Augmentation'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def get_class_distribution(folder):
    class_counts = {}
    for folder_name in os.listdir(folder):
        class_folder = os.path.join(folder, folder_name)
        if os.path.isdir(class_folder):  
            num_images = len([f for f in os.listdir(class_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
            if num_images > 0:
                class_counts[class_folder] = num_images
    return class_counts

datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

class_distribution = get_class_distribution(input_folder)
print("Class distribution:", class_distribution)

target_class_size = 600
print(f"Target class size: {target_class_size}")

for class_folder in os.listdir(input_folder):
    class_folder_path = os.path.join(input_folder, class_folder)
    
    if os.path.isdir(class_folder_path):
        label_output_folder = os.path.join(output_folder, class_folder)
        if not os.path.exists(label_output_folder):
            os.makedirs(label_output_folder)

        image_files = [f for f in os.listdir(class_folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
        num_images = len(image_files)
        
        if num_images < target_class_size:
            print(f"Applying augmentation to class: {class_folder}")
            
            for image_name in image_files:
                image_path = os.path.join(class_folder_path, image_name)
                
                img = load_img(image_path)
                img_array = img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)  

                i = 0
                for batch in datagen.flow(img_array, batch_size=1, save_to_dir=label_output_folder, save_prefix=f'aug_{class_folder}_', save_format='jpeg'):
                    i += 1
                    if num_images + i >= target_class_size: 
                        break
                if num_images + i >= target_class_size:
                    break 

        elif num_images > target_class_size:
            print(f"Downsampling class: {class_folder}")
            random.shuffle(image_files)
            images_to_remove = image_files[target_class_size:]
            for image_name in images_to_remove:
                image_path = os.path.join(class_folder_path, image_name)
                os.remove(image_path)  

        for image_name in image_files[:target_class_size]:
            source_image_path = os.path.join(class_folder_path, image_name)
            dest_image_path = os.path.join(label_output_folder, image_name)
            shutil.copy(source_image_path, dest_image_path)
print("Dataset balancing completed.")
