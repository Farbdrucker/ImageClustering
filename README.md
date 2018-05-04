# ImageClustering
Image clustering application based on **spectral clustering** using the **Fiedler vector**.
The eigenvectors will be computed from an approximation of the Graph Laplace Operator.
The operator will be approximated by a rank k approximation using the **adaptive cross approximation** and a QR decomposition of the rank k approximation. The second eigenvector is named Fiedler vector and will seperate the image into two clusters by the sign of the entries of the vector.
Additionally one can label the image. One can label the image by drawing with the left or right mouse key. Left key (green) for the object of interest and right key (blue) for background. The labeling will applied by a **convexity splitting** scheme.

## load
**load** will open a filedialog window to search for images to load.

## mask
**mask** will compute the eigenvectors an instantly applies the mask based on the vectors. One can switch between the computed eigenvectors by recurring pressing the _mask_ button.

## invert mask
**invert mask** since the mask will be applied by the sign of the vector entries, one can invert the mask resp. change the sign.

## supervise
**supervise** if one labeled the image by drawing green and blue on the canvas, the supervise button will perform a convexity splitting scheme to improve the segmentation

## save
**save** if one is satisfied with the mask it can be saved. The button will open a save file dialog

## mouse
with the left mouse key one can draw on the canvas and label the object of interest while the right key labels the background. With the mouse wheel one can adjust the brush size
