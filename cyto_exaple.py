from cytocoarsening.cytocoarsening import cytocoarsening
import numpy as np
import random

cell_data=[[random.random() for i in range(33)] for j in range(4500)]
cell_data=np.array(cell_data)

cell_label = np.array([0] * 1000 + [1] * (3500))
np.random.shuffle(cell_label)

group,edge,diccts=cytocoarsening(cell_data,cell_label,3,5)
