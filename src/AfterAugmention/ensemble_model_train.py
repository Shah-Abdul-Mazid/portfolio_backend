import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
import numpy as np
from ensamble import ensemblemodel
from customcnnmodel import customcnnmodel
from PIL import Image
from tqdm import tqdm
from sklearn.metrics import precision_score, recall_score, f1_score
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import warnings

warnings.simplefilter('ignore', Image.DecompressionBombWarning)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using Device",device)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

class_labels = ['Black Rohu', 'Catla', 'Common Carp', 'Freshwater Shark', 'Grass Carp', 
                'Long-whiskered Catfish', 'Mirror Carp', 'Mrigal', 'Nile Tilapia', 'Rohu', 
                'Silver Carp', 'Striped Catfish']
num_classes = len(class_labels)

train_path = "D:\\CSETEST\\aug_train"
val_path = "D:\\CSETEST\\aug_validation"

train_dataset = datasets.ImageFolder(root=train_path, transform=transform)
val_dataset = datasets.ImageFolder(root=val_path, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

model_paths = {
    "customcnn": "D:\\CSETEST\\src\\AfterAugmention\\models\\customcnnmodel_best_model.pth",
    "resnet50": "D:\\CSETEST\\src\\AfterAugmention\\models\\ResNet_best_model.pth",
    "efficientnet_b0": "D:\\CSETEST\\src\\AfterAugmention\\models\\EfficientNet_best_model.pth",
    "mobilenetv2": "D:\\CSETEST\\src\\AfterAugmention\\models\\MobileNetV2_best_model.pth",
    "densenet121": "D:\\CSETEST\\src\\AfterAugmention\\models\\DenseNet_best_model.pth"
}

def load_model(model_name, model_path, num_classes, device):
        if model_name.lower() == "customcnn":
            model = customcnnmodel(num_classes)  
        elif model_name.lower() == "resnet50":
            model = models.resnet50(weights=None) 
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif model_name.lower() == "efficientnet_b0":
            model = models.efficientnet_b0(weights=None)  
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif model_name.lower() == "mobilenetv2":
            model = models.mobilenet_v2(weights=None)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif model_name.lower() == "densenet121":
            model = models.densenet121(weights=None)  
            model.classifier = nn.Linear(model.classifier.in_features, num_classes)
        else:
            raise ValueError(f"Model {model_name} not supported.")
    
        checkpoint = torch.load(model_path, map_location=device)
        model.load_state_dict(checkpoint, strict=False)
        model.to(device)
        model.eval()  
        return model
    
models_list = [load_model(name, path, num_classes, device) for name, path in tqdm(model_paths.items(), desc="Loading Models")]

ensemble_model = ensemblemodel(models=models_list, num_classes=num_classes).to(device)

criterion = nn.CrossEntropyLoss()

def train_ensemble_weights(ensemble_model, loader, max_epochs=100, patience=15):
    optimizer = optim.Adam([ensemble_model.weights], lr=1e-3)
    best_val_loss = float('inf')
    patience_counter = 0
    best_state = None

    for epoch in range(max_epochs):
        ensemble_model.train()
        total_loss = 0.0

        train_loader_tqdm = tqdm(loader, desc=f"Training Epoch {epoch+1}/{max_epochs}", leave=False)

        for images, labels in train_loader_tqdm:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = ensemble_model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * images.size(0)
            train_loader_tqdm.set_postfix(loss=loss.item())

        train_loss = total_loss / len(loader.dataset)

        ensemble_model.eval()
        val_loss = 0.0
        val_loader_tqdm = tqdm(loader, desc="Validating", leave=False)

        with torch.no_grad():
            for images, labels in val_loader_tqdm:
                images, labels = images.to(device), labels.to(device)
                outputs = ensemble_model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                val_loader_tqdm.set_postfix(val_loss=loss.item())

        val_loss /= len(loader.dataset)
        print(f"Epoch {epoch+1}/{max_epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_state = ensemble_model.weights.detach().clone()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered at epoch {epoch+1}")
                ensemble_model.weights.data.copy_(best_state)
                break

train_ensemble_weights(ensemble_model, val_loader, max_epochs=100, patience=15)

def evaluate_model(model, loader):
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return np.array(all_labels), np.array(all_preds)
for model in models_list:
    true_labels, predictions = evaluate_model(model, val_loader)
    precision = precision_score(true_labels, predictions, average='weighted')
    recall = recall_score(true_labels, predictions, average='weighted')
    f1 = f1_score(true_labels, predictions, average='weighted')
    print(f"{model.__class__.__name__} -> Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}")

true_labels, predictions = evaluate_model(ensemble_model, val_loader)
precision = precision_score(true_labels, predictions, average='weighted')
recall = recall_score(true_labels, predictions, average='weighted')
f1 = f1_score(true_labels, predictions, average='weighted')
print(f"EnsembleModel -> Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}")

ensemble_model_path = "D:\\CSETEST\\src\\AfterAugmention\\models\\ensemble_model.pth"
torch.save(ensemble_model.state_dict(), ensemble_model_path)
print(f"Ensemble model saved to {ensemble_model_path}")
