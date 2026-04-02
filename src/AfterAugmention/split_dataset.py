import os
import shutil
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Define dataset directories
data_dir = "D:\\CSETEST\\BD-Freshwater-Fish-Augmentation"
train_dir = "D:\\CSETEST\\aug_train"
val_dir = "D:\\CSETEST\\aug_validation"
test_dir = "D:\\CSETEST\\aug_test"

for folder in [train_dir, val_dir, test_dir]:
    os.makedirs(folder, exist_ok=True)

file_paths = []
labels = []
for class_name in os.listdir(data_dir):
    class_dir = os.path.join(data_dir, class_name)
    for image_name in os.listdir(class_dir):
        file_paths.append(os.path.join(class_dir, image_name))
        labels.append(class_name)

df = pd.DataFrame({"file_path": file_paths, "label": labels})
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  

train_df, temp_df = train_test_split(df, test_size=0.3, stratify=df['label'], random_state=42)  
val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42)  

def copy_images(dataframe, target_dir):
    for _, row in dataframe.iterrows():
        class_folder = os.path.join(target_dir, row["label"])
        os.makedirs(class_folder, exist_ok=True)
        shutil.copy(row["file_path"], class_folder)

copy_images(train_df, train_dir)
copy_images(val_df, val_dir)
copy_images(test_df, test_dir)

# Print summary
print(f"Dataset split complete!")
print(f"Training images: {len(train_df)}")
print(f"Validation images: {len(val_df)}")
print(f"Test images: {len(test_df)}")
print(f"Images saved in:\n{train_dir} (Training)\n{val_dir} (Validation)\n{test_dir} (Test)")
