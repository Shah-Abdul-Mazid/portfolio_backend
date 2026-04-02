import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms,models
from torch.utils.data import DataLoader
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from customcnnmodel import customcnnmodel
from tqdm import tqdm  
import seaborn as sns
import warnings
import os
import gc

warnings.simplefilter('ignore', Image.DecompressionBombWarning)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using Device",device)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

class_labels = ['Black Rohu', 'Catla', 'Common Carp', 'Freshwater Shark', 'Grass Carp', 'Long-whiskered Catfish', 
                'Mirror Carp', 'Mrigal', 'Nile Tilapia', 'Rohu','Silver Carp', 'Striped Catfish']

num_classes = len(class_labels)

train_path = "D:\\CSETEST\\aug_train"
test_path = "D:\\CSETEST\\aug_test"
val_path = "D:\\CSETEST\\aug_validation"

train_dataset = datasets.ImageFolder(root=train_path, transform=transform)
test_dataset= datasets.ImageFolder(root=test_path,transform=transform)
val_dataset = datasets.ImageFolder(root=val_path, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset,batch_size=32,shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=True)

def get_model(model_name, num_classes):
    if "customcnn" in model_name:
        model = customcnnmodel(num_classes=12).to(device)
        return model
    model = getattr(models, model_name)(pretrained=True)
    if 'resnet' in model_name:
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif 'efficientnet' in model_name or'mobilenet' in model_name:
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif 'densenet' in model_name:
        model.classifier = nn.Linear(model.classifier.in_features, num_classes)
     
    return model.to(device)

model_names = ['customcnn','resnet50', 'efficientnet_b0','mobilenet_v2','densenet121', ]
models_dict = {name: get_model(name, num_classes) for name in model_names}

def prepare_optimizer(model, learning_rate=0.001):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    return criterion, optimizer

def validate_model(model, val_loader, criterion):
    model.eval()  
    val_loss = 0.0
    correct_preds = 0
    total_preds = 0
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            
            _, predicted = torch.max(outputs, 1)
            correct_preds += (predicted == labels).sum().item()
            total_preds += labels.size(0)
    
    avg_val_loss = val_loss / len(val_loader)
    val_accuracy = correct_preds / total_preds
    return avg_val_loss, val_accuracy

def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=100, early_stopping_patience=15):
    train_losses = []
    val_losses = []
    val_accuracies = []
    best_val_acc = 0
    patience_counter = 0
    
    log_file_path = f"D:\\CSETEST\\src\\AfterAugmention\\Logs\\{model.__class__.__name__}_training_log.txt"
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        correct_preds = 0
        total_preds = 0
        
        for inputs, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}", leave=False):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            correct_preds += (predicted == labels).sum().item()
            total_preds += labels.size(0)
        
        epoch_loss = running_loss / len(train_loader)
        epoch_accuracy = correct_preds / total_preds
        val_loss, val_accuracy = validate_model(model, val_loader, criterion)

        train_losses.append(epoch_loss)
        val_losses.append(val_loss)
        val_accuracies.append(val_accuracy)
        
        log_message = f"Epoch [{epoch+1}/{num_epochs}], Train Loss: {epoch_loss:.4f}, Train Accuracy: {epoch_accuracy*100:.2f}%, Val Loss: {val_loss:.4f}, Val Accuracy: {val_accuracy*100:.2f}%"
        print(log_message)
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_message + '\n')
        
        if val_accuracy > best_val_acc:
            best_val_acc = val_accuracy
            patience_counter = 0
            print(best_val_acc)
            torch.save(model.state_dict(), f"D:\\CSETEST\\src\\AfterAugmention\\models\\{model.__class__.__name__}_best_model.pth")
        else:
            patience_counter += 1 
        
        print(f"Patience Counter: {patience_counter}/{early_stopping_patience}")  
        
        if patience_counter >= early_stopping_patience:
            print(f"Early stopping triggered at epoch {epoch+1}")
            break

    return train_losses, val_losses, val_accuracies

num_epochs = 100
for model_name, model in models_dict.items():
    print(f"Training model: {model_name}")
    criterion, optimizer = prepare_optimizer(model)
    train_losses, val_losses, val_accuracies = train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs)
    
    epochs_range = range(len(train_losses))  

    plt.figure(figsize=(10, 6))
    plt.plot(epochs_range, train_losses, label='Train Loss')
    plt.plot(epochs_range, val_losses, label='Validation Loss')
    plt.title(f'{model_name} - Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(f"D:\\CSETEST\\src\\AfterAugmention\\Figure\\{model_name}_loss_curve.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(epochs_range, val_accuracies, label='Validation Accuracy', color='green')
    plt.title(f'{model_name} - Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig(f"D:\\CSETEST\\src\\AfterAugmention\\Figure\\{model_name}_val_accuracy_curve.png")
    plt.close()
    
    del model, criterion, optimizer
    torch.cuda.empty_cache()
    gc.collect()

    print(f"{model_name} trained and saved successfully!")