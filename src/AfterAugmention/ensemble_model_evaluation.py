import torch
import torchvision.models as models
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from customcnnmodel import customcnnmodel  
from tqdm import tqdm
from PIL import Image
import warnings
import pandas as pd

warnings.simplefilter('ignore', Image.DecompressionBombWarning)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using Device", device)

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
test_path = "D:\\CSETEST\\aug_test"

train_dataset = datasets.ImageFolder(root=train_path, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=False)
test_dataset = datasets.ImageFolder(root=test_path, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
val_dataset = datasets.ImageFolder(root=val_path, transform=transform)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

base_models = {
    "customcnn": "D:\\CSETEST\\src\\AfterAugmention\\models\\customcnnmodel_best_model.pth",
    "resnet50": "D:\\CSETEST\\src\\AfterAugmention\\models\\ResNet_best_model.pth",
    "efficientnet_b0": "D:\\CSETEST\\src\\AfterAugmention\\models\\EfficientNet_best_model.pth",
    "mobilenetv2": "D:\\CSETEST\\src\\AfterAugmention\\models\\MobileNetV2_best_model.pth",
    "densenet121": "D:\\CSETEST\\src\\AfterAugmention\\models\\DenseNet_best_model.pth"
}

def load_model(model_name, base_models, num_classes, device):
    if model_name.lower() == "customcnn":
        model = customcnnmodel(num_classes)
    elif model_name.lower() == "resnet50":
        model = models.resnet50(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    elif model_name.lower() == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
    elif model_name.lower() == "mobilenetv2":
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
    elif model_name.lower() == "densenet121":
        model = models.densenet121(weights=None)
        model.classifier = torch.nn.Linear(model.classifier.in_features, num_classes)
    else:
        raise ValueError(f"Model {model_name} not supported.")
    
    checkpoint = torch.load(base_models, map_location=device)
    model.load_state_dict(checkpoint, strict=False)
    model.to(device)
    model.eval()
    return model

models_list = [load_model(name, path, num_classes, device) for name, path in tqdm(base_models.items(), desc="Loading Models")]

def evaluate_model(model, test_loader):
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            
            if outputs.dim() == 2:  
                _, preds = torch.max(outputs, 1)
            elif outputs.dim() == 1:  
                preds = outputs
            else:
                raise ValueError(f"Unexpected output shape: {outputs.shape}")
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    return np.array(all_labels), np.array(all_preds)

def evaluate_and_show_scores(model, test_loader):
    true_labels, predictions = evaluate_model(model, test_loader)
    
    precision = precision_score(true_labels, predictions, average='weighted', zero_division=1)  
    recall = recall_score(true_labels, predictions, average='weighted', zero_division=1)
    f1 = f1_score(true_labels, predictions, average='weighted', zero_division=1)
    accuracy = accuracy_score(true_labels, predictions)
    
    accuracy_percentage = accuracy * 100
    precision_percentage = precision * 100
    recall_percentage = recall * 100
    f1_percentage = f1 * 100
    
    print(f"{model.__class__.__name__} -> Accuracy: {accuracy_percentage:.2f}%, Precision: {precision_percentage:.2f}%, Recall: {recall_percentage:.2f}%, F1 Score: {f1_percentage:.2f}%")
    
    return {
        "Model": model.__class__.__name__,
        "Accuracy (%)": accuracy_percentage,
        "Precision (%)": precision_percentage,
        "Recall (%)": recall_percentage,
        "F1 Score (%)": f1_percentage
    }

class VotingEnsembleModel(torch.nn.Module):
    def __init__(self, models, mode='soft'):
        super(VotingEnsembleModel, self).__init__()
        self.models = models
        self.mode = mode  

    def forward(self, x):
        outputs = [model(x) for model in self.models]
        outputs = torch.stack(outputs, dim=0)
        
        if self.mode == 'hard':
            _, preds = torch.mode(outputs, dim=0)
            return preds
        elif self.mode == 'soft':
            outputs = torch.nn.functional.softmax(outputs, dim=2)
            avg_outputs = torch.mean(outputs, dim=0)
            _, preds = torch.max(avg_outputs, dim=1)
            return preds
        else:
            raise ValueError("Voting mode should be 'hard' or 'soft'.")

class StackingEnsembleModel(torch.nn.Module):
    def __init__(self, base_models, meta_model):
        super(StackingEnsembleModel, self).__init__()
        self.base_models = torch.nn.ModuleList(base_models)
        self.meta_model = meta_model

    def forward(self, x):
        base_model_preds = [base_model(x) for base_model in self.base_models]
        base_model_preds = torch.stack(base_model_preds, dim=1)
        base_model_preds = base_model_preds.view(x.size(0), -1)
        return self.meta_model(base_model_preds)

class BoostingEnsembleModel(torch.nn.Module):
    def __init__(self, base_models, num_classes):
        super(BoostingEnsembleModel, self).__init__()
        self.base_models = torch.nn.ModuleList(base_models)
        self.num_classes = num_classes
    
    def forward(self, x):
        predictions = []
        for model in self.base_models:
            output = model(x)
            predictions.append(output)
        
        final_output = sum(predictions)
        return final_output

class BaggingEnsembleModel(torch.nn.Module):
    def __init__(self, base_model, num_models, num_classes):
        super(BaggingEnsembleModel, self).__init__()
        self.models = torch.nn.ModuleList([base_model(num_classes) for _ in range(num_models)])

    def forward(self, x):
        outputs = [model(x) for model in self.models]
        outputs = torch.stack(outputs, dim=0)
        avg_outputs = torch.mean(outputs, dim=0)
        _, preds = torch.max(avg_outputs, dim=1)
        return preds

meta_model = torch.nn.Sequential(
    torch.nn.Linear(len(models_list) * num_classes, 128),
    torch.nn.ReLU(),
    torch.nn.Linear(128, num_classes)
)

voting_model = VotingEnsembleModel(models=models_list, mode='soft').to(device)
stacking_model = StackingEnsembleModel(base_models=models_list, meta_model=meta_model).to(device)
boosting_model = BoostingEnsembleModel(base_models=models_list, num_classes=num_classes).to(device)
bagging_model = BaggingEnsembleModel(base_model=customcnnmodel, num_models=5, num_classes=num_classes).to(device)

# Evaluate models and collect results
results = []
for model in [voting_model, stacking_model, boosting_model, bagging_model]:
    result = evaluate_and_show_scores(model, test_loader)
    results.append(result)

# Save results to CSV
results_df = pd.DataFrame(results)
output_csv = "D:\\CSETEST\\src\\AfterAugmention\\ensemble_results.csv"
results_df.to_csv(output_csv, index=False)
print(f"\nResults saved to {output_csv}")