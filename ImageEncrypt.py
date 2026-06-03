import numpy as np
import os
import cv2
import timeit
import random
import hashlib
import math
import matplotlib.pyplot as plt
from SCD import *

#initialize Keys
def generateKey():
    x_min = np.zeros(80, dtype=int)  # All zeros
    x_max = np.full(80, 255, dtype=int)  # All 255s
    x_initial_scd = 0.5 #chi_square_stat  # Given initial value which is chi square value
    accuracy = 1  # Desired accuracy for stopping condition
    m = 80  # Number of coordinates
    max_steps = 3 * m  # Maximum number of steps
    # Run Segmented Coordinate Descent with floored values
    x_optimized, y_optimized = SCD(x_min, x_max, x_initial_scd, accuracy, max_steps)
    return x_optimized, y_optimized

#scramble Block
def scramble(k, length_of_k):
    start = 0
    end = 1
    c = 0
    v1 = 0
    v2 = 0
    while start < length_of_k - 1:
        v1 += k[start] ^ k[end]
        start = end
        end += 1
        if end == 32:
            end = 0
        v2 += k[start] ^ k[end]
        start += 1
        end += 1
    c = (v1 % 127) + (v2 % 128)
    ki = []
    for i in range(0, length_of_k):
        ki.append((k[i] + c) % 256)
    return ki

#propose encryption function
def proposeEncryption(filename):
    img = cv2.imread(filename) #read image
    w, h, channel = img.shape
    I0 = img.ravel() #3 dimensional image to one dimension
    l = len(I0)#get length of one dimension vector
    for i in range(0, 10): #add 10 random pixels to form NI0
        random_pixels = random.randint(np.min(I0), np.max(I0))
        if i == 0:
            NI0 = np.append(I0, random_pixels)
        else:
            NI0 = np.append(NI0, random_pixels)
    x_optimized, y_optimized = generateKey() #get keys
    NI0 = NI0.tobytes()
    #execute SEA and FI-PWLCM sequence generation and 
    k = hashlib.sha256(NI0).digest() #get 32 bytes hash value
    temp = []
    for i in range(len(k)):
        temp.append(k[i])
    k = np.asarray(temp)    
    k = np.minimum(k, x_optimized)#convert K high dimension to SCD low dimension
    length_of_k = len(k)
    ki = scramble(k, length_of_k)#block scramble
    K = []
    i=0
    start = 1
    while i < l:
        A = ki[1:start] #get A and B values
        B = ki[start+1:length_of_k]
        i += 1
        C = 0
        start += 1
        if start == 32:
            start = 1
        for j in range(0, (min(len(A), len(B)))):#apply XOR or A and B values to generate C sequences
            C += A[j] ^ B[j]
        K.append(C) #add C sequences to K to form image encryption key 
    encrypted = []
    for i in range(0, len(I0)):
        encrypted.append(I0[i] ^ K[i])
    encrypted = np.asarray(encrypted)
    encrypted = np.reshape(encrypted, (w, h, channel))
    cv2.imwrite(filename, encrypted)
    keys = [K, encrypted, w, h, channel]
    keys = np.asarray(keys, dtype=object)
    # Save keys to the keys directory
    keys_filename = "static/keys/"+os.path.basename(filename)
    np.save(keys_filename, keys)

#funtion to decrypt image
def proposeDecryption(filename):    
    keys = np.load("static/keys/"+filename+".npy", allow_pickle=True)
    K, encrypted, w, h, channel = keys[0], keys[1], keys[2], keys[3], keys[4]
    encrypted_image = cv2.imread("static/files/"+filename)
    I0 = encrypted.ravel()
    decrypted = []
    for i in range(0, len(I0)):
        decrypted.append(I0[i] ^ K[i])
    decrypted = np.reshape(decrypted, (w, h, channel))
    return decrypted/255
'''
proposeEncryption("queryImages/132.jpg")
img = proposeDecryption("132.jpg")
cv2.imshow("aa", img)
cv2.waitKey(0)
'''
    



