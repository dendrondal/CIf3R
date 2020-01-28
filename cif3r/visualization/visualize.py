import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path
import seaborn as sb
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3
from PIL import Image
from cif3r.models.train_model import datagen, train_val_split, label_encoding

PARENT_DIR = Path(__file__).resolve().parents[2]
KAGGLE_DATA_PATH = PARENT_DIR / 'data/raw/DATASET/TEST'
MODEL_DIR = PARENT_DIR / 'models'
VIZ_DIR= PARENT_DIR / 'reports/figures'


def prediction_mapping(university:str):
    try:
        clf = tf.keras.models.load_model(MODEL_DIR / f'{university}.h5')
    except OSError:
        raise Exception(f"Unable to find model. Valid  models include {MODEL_DIR.glob('*.h5')}")
    df = datagen(university)
    df = df.sample(n=int(len(df)/10), random_state=42)
    images = ImageDataGenerator().flow_from_dataframe(df, batch_size=64)
    y_hat = list(clf.predict(images))
    df['y_hat'] = y_hat
    return {'df': df, 'labels':images.class_indices}

    
def plot_confusion_matrix(university:str):
    """For kaggle data, prediction class is organized by folder structure, but for scraped data, 
    sql metadata is used."""
    preds = prediction_mapping(university)
    df = preds['df']
    df['y_hat'] = df['y_hat'].map(lambda x: np.where(x == np.amax(x))[0][0])
    df['y_hat'] = df['y_hat'].map(lambda x: list(preds['labels'].keys())[x])
    print(df.head())
    labels = list(preds['labels'].keys())
    con_mat = confusion_matrix(df['class'], df['y_hat'], labels=labels)
    figure = plt.figure(figsize=(8,8))
    con_mat_df = pd.DataFrame(con_mat, index=labels, columns=labels)
    sb.heatmap(con_mat_df, annot=True, cmap=plt.cm.Blues)
    plt.tight_layout()
    plt.xlabel('True label')
    plt.ylabel('Predicted label')
    plt.savefig(VIZ_DIR / f'{university}_confusion_matrix.png')
