# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 23:50:19 2021

@author: MMM
"""

import os
import numpy as np
import cv2
from glob import glob
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, CSVLogger, TensorBoard
from data import load_data, tf_dataset
from model import build_model


def iou(y_true, y_pred):
    def f(y_true, y_pred):
        intersection = (y_true * y_pred).sum()
        union = y_true.sum() + y_pred.sum() - intersection
        x = (intersection + 1e-15) / (union + 1e-15)
        x = x.astype(np.float32)
        return x
    return tf.numpy_function(f, [y_true, y_pred], tf.float32)
        
    
if __name__=="__main__":
    path="CVC-ClinicDB"
    (train_x,train_y),(valid_x,valid_y),(test_x,test_y)=load_data(path)
    print(len(train_x),len(valid_x),len(test_x))
    
    batch=8
    lr=1e-4
    epochs=20
    train_dataset=tf_dataset(train_x,train_y,batch=batch)
    valid_dataset=tf_dataset(valid_x,valid_y,batch=batch)
    model=build_model()
    opt=tf.keras.optimizers.Adam()
    metrics=['acc',tf.keras.metrics.Precision(), tf.keras.metrics.Recall(),iou]
    model.compile(optimizer=opt,loss="binary_crossentropy",metrics=metrics)
    callbacks=[ ModelCheckpoint("files/model.h5"), ReduceLROnPlateau(monitor="val_loss",factor=0.1, patience=4),CSVLogger("files/data.csv"), TensorBoard(), EarlyStopping(monitor='val_loss', patience=0.4,restore_best_weights=False) ]
    train_steps=len(train_x) // batch
    valid_steps=len(valid_x) // batch
    if len(train_x) % batch !=0:
        train_steps+=1
    if len(valid_x) % batch !=0:
        valid_steps+=1
    model.fit(train_dataset, epochs=epochs, validation_data=valid_dataset,steps_per_epoch=train_steps,validation_steps=valid_steps,callbacks=callbacks)