import numpy as np
import cv2 as cv


def extract(image: np.ndarray):

    #Convertemos a imagem para um array
    pixels = image.reshape((-1,3))

    # Convertemos os valores dos pixels para np.float32
    pixels = np.float32(pixels)
    
    # Definindo os critérios de parada e rodando o k-means
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.5)
    K = 3 #Dividir a imagem em três grupos
    ret,label,center=cv.kmeans(pixels,K,None,criteria,10,cv.KMEANS_RANDOM_CENTERS)
    #Vamos dar as cores Vermelho, verde e azul para os grupos
    my_centers_colors = np.array([[0, 0, 255], [0, 255, 0], [255, 0, 0]], dtype=np.float32)

    #Reconstruimos a imagem
    res = my_centers_colors[label.flatten()]
    res2 = res.reshape((image.shape))
    return res2

