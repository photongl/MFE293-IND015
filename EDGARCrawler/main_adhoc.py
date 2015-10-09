'''
Created on Jul 14, 2015

@author: akshaym
'''
import numpy as np
import os
from matplotlib import pyplot as plt
from scipy import ndimage
from matplotlib.image import imsave

COMPRESSED_FILING_FEATURES_PATH = "E:\\Books and Papers\\Citi_Seniority_Recovery\\R Code\\Final\\"
TARGET_FILING_FEATURES_PATH = "E:\\Books and Papers\\Citi_Seniority_Recovery\\R Code\\Final\\"

N = 9000
i = 0
for file in os.listdir(COMPRESSED_FILING_FEATURES_PATH):
    if file.endswith(".npz"):
        i = i + 1
        if (i > N):
            break
        print("Uncompressing {}...".format(file))
        a = np.load(COMPRESSED_FILING_FEATURES_PATH + file)
        #plt.imshow(a["arr_0"])
        imsave(TARGET_FILING_FEATURES_PATH + "{}.png".format(file[0:-4]), a["arr_0"])
        #np.savetxt(TARGET_FILING_FEATURES_PATH + file[0:-4], a["arr_0"])
        