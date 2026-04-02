import torch
import torch.nn as nn
from torchvision import models
import torch.nn as nn
import numpy as np
import torch.optim as optim
import torchvision.models as models
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score
from tqdm import tqdm  

class ensemblemodel(nn.Module):
    def __init__(self, models, num_classes):
        super(ensemblemodel, self).__init__()
        self.models = nn.ModuleList(models)
        self.weights = nn.Parameter(torch.ones(len(models), device='cuda'))

    def forward(self, x):
        outputs = torch.stack([model(x) for model in self.models])  
        weights = torch.softmax(self.weights, dim=0).view(-1, 1, 1) 
        return torch.sum(outputs * weights, dim=0) 
    
