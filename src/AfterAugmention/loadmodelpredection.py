import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models, datasets
from customcnnmodel import customcnnmodel
from ensamble import ensemblemodel
import os
import glob
import warnings
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from torchvision.models import ResNet50_Weights, EfficientNet_B0_Weights, MobileNet_V2_Weights, DenseNet121_Weights

warnings.simplefilter('ignore', Image.DecompressionBombWarning)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using Device:", device)

train_path = "D:\\CSETEST\\aug_train"
test_path = "D:\\CSETEST\\aug_test"
val_path = "D:\\CSETEST\\aug_validation"

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

train_dataset = datasets.ImageFolder(root=train_path, transform=transform)
test_dataset = datasets.ImageFolder(root=test_path, transform=transform)
val_dataset = datasets.ImageFolder(root=val_path, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=True)

class_labels = ['Black Rohu', 'Catla', 'Common Carp', 'Freshwater Shark', 'Grass Carp', 
                'Long-whiskered Catfish', 'Mirror Carp', 'Mrigal', 'Nile Tilapia', 
                'Rohu', 'Silver Carp', 'Striped Catfish']
num_classes = len(class_labels)

model_paths = {
    "customcnn": "D:\\CSETEST\\src\\AfterAugmention\\models\\customcnnmodel_best_model.pth",    
    "ResNet50": "D:\\CSETEST\\src\\AfterAugmention\\models\\ResNet_best_model.pth",
    "EfficientNet_B0": "D:\\CSETEST\\src\\AfterAugmention\\models\\EfficientNet_best_model.pth",
    "MobileNetV2": "D:\\CSETEST\\src\\AfterAugmention\\models\\MobileNetV2_best_model.pth",
    "DenseNet121": "D:\\CSETEST\\src\\AfterAugmention\\models\\DenseNet_best_model.pth",
    "ensemblemodel": "D:\\CSETEST\\src\\AfterAugmention\\models\\ensemble_model.pth"
}

models_dict = {}

for model_name, path in model_paths.items():
    try:
        if model_name == "customcnn":
            model = customcnnmodel(num_classes)
        elif model_name == "ResNet50":
            model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif model_name == "EfficientNet_B0":
            model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif model_name == "MobileNetV2":
            model = models.mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif model_name == "DenseNet121":
            model = models.densenet121(weights=DenseNet121_Weights.DEFAULT)
            model.classifier = nn.Linear(model.classifier.in_features, num_classes)
        elif model_name == "ensemblemodel":
            model = ensemblemodel(models=list(models_dict.values()), num_classes=num_classes)
        
        model.load_state_dict(torch.load(path, map_location=device))
        model.to(device)
        model.eval()
        models_dict[model_name] = model
    except Exception as e:
        print(f"Error loading {model_name} from {path}: {e}")

print("All models loaded successfully!")

def predict_image(image_path, models_dict):
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None
    
    image = transform(image).unsqueeze(0).to(device)
    results = {}
    with torch.no_grad():
        for model_name, model in models_dict.items():
            outputs = model(image)
            _, predicted = torch.max(outputs, 1)
            results[model_name] = class_labels[predicted.item()]
    
    return results

def predict_images_from_folder(folder_path, models_dict):
    image_files = glob.glob(os.path.join(folder_path, "**", "*.jpeg"), recursive=True) + \
                  glob.glob(os.path.join(folder_path, "**", "*.jpg"), recursive=True) + \
                  glob.glob(os.path.join(folder_path, "**", "*.png"), recursive=True)
    
    print(f"\nFound {len(image_files)} images in '{folder_path}'. Running predictions...\n")
    
    label_summary = {model_name: {label: {"correct": 0, "total": 0} for label in class_labels} for model_name in models_dict.keys()}
    
    for image_path in image_files:
        actual_label = os.path.basename(os.path.dirname(image_path))
        predictions = predict_image(image_path, models_dict)
        if predictions is None:
            continue
        
        for model_name, pred_class in predictions.items():
            label_summary[model_name][actual_label]["total"] += 1
            if pred_class == actual_label:
                label_summary[model_name][actual_label]["correct"] += 1
    
    # Save prediction summary to CSV
    prediction_summary_data = []
    for model_name, label_data in label_summary.items():
        print(f"\nModel: {model_name}")
        for label, counts in label_data.items():
            if counts["total"] > 0:
                accuracy = (counts["correct"] / counts["total"] * 100)
                print(f"  {label}: {counts['correct']} correct / {counts['total']} total (Accuracy: {accuracy:.2f}%)")
                prediction_summary_data.append({
                    'Model': model_name,
                    'Class': label,
                    'Correct': counts['correct'],
                    'Total': counts['total'],
                    'Accuracy (%)': round(accuracy, 2)
                })
    
    # Create DataFrame and save to CSV
    prediction_df = pd.DataFrame(prediction_summary_data)
    prediction_df.to_csv("D:\\CSETEST\\src\\AfterAugmention\\Logs\\prediction_summary.csv", index=False)
    print("\nPrediction summary saved to D:\\CSETEST\\src\\AfterAugmention\\Logs\\prediction_summary.csv")
    
    return label_summary

def evaluate_model_on_test_set(model, test_loader):
    model.eval()
    all_labels = []
    all_preds = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(predicted.cpu().numpy())

    report = classification_report(all_labels, all_preds, target_names=class_labels, output_dict=True)
    cm = confusion_matrix(all_labels, all_preds)

    with open(f"D:\\CSETEST\\src\\AfterAugmention\\Logs\\{model.__class__.__name__}_test_report.txt", 'w') as f:
        f.write(f"Classification Report for {model.__class__.__name__}:")
        f.write(str(report))

    plt.figure(figsize=(10, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_labels, yticklabels=class_labels)
    plt.title(f'{model.__class__.__name__} Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.savefig(f"D:\\CSETEST\\src\\AfterAugmention\\Figure\\{model.__class__.__name__}_confusion_matrix.png")
    plt.close()

    return report

def evaluate_all_models(models_dict, test_loader):
    model_comparison = {}
    test_set_data = []
    
    for model_name, model in models_dict.items():
        print(f"Evaluating model {model_name} on the test set")
        report = evaluate_model_on_test_set(model, test_loader)
        model_comparison[model_name] = report
        
        print(f"\n{model_name} Test Set Performance:")
        print(f"Accuracy: {report['accuracy']:.2f}")
        for label in class_labels:
            print(f"Class: {label} | Precision: {report[label]['precision']:.2f} | "
                  f"Recall: {report[label]['recall']:.2f} | F1-Score: {report[label]['f1-score']:.2f}")
            test_set_data.append({
                'Model': model_name,
                'Class': label,
                'Accuracy': round(report['accuracy'], 2),
                'Precision': round(report[label]['precision'], 2),
                'Recall': round(report[label]['recall'], 2),
                'F1-Score': round(report[label]['f1-score'], 2)
            })
    
    # Create DataFrame and save to CSV
    test_set_df = pd.DataFrame(test_set_data)
    test_set_df.to_csv("D:\\CSETEST\\src\\AfterAugmention\\Logs\\test_set_performance.csv", index=False)
    print("\nTest set performance saved to D:\\CSETEST\\src\\AfterAugmention\\Logs\\test_set_performance.csv")
    
    return model_comparison

# Run evaluations and predictions
model_comparison = evaluate_all_models(models_dict, test_loader)
predict_images_from_folder(test_path, models_dict)