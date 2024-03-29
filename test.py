import numpy as np
import PIL
import matplotlib.pyplot as plt

images = np.asarray(PIL.Image.open("1.png"))
# sample_images = np.concatenate([image.reshape(1, image.shape[0], image.shape[1], image.shape[2])
#                                for image in images], axis=0)

plt.figure(1)
for i in range(1):
    plt.subplot(2, 2, i + 1)
    plt.imshow(images[i, ...])
    plt.axis("off")
plt.subplots_adjust(0, 0, 1, 1, 0, 0)

# determine per-pixel variablility, std() over all images
# variability = sample_images.std(axis=0).sum(axis=2)
variability = images

# show image of these variabilities
plt.figure(2)
plt.imshow(variability, cmap=plt.cm.gray,
           interpolation="nearest", origin="lower")

# determine bounding box
thresholds = [255, 255, 255]
colors = ["r", "b", "g"]
for threshold, color in zip(thresholds, colors):  # variability.mean()
    non_empty_columns = np.where(variability.min(axis=0) < threshold)[0]
    non_empty_rows = np.where(variability.min(axis=1) < threshold)[0]
    boundingBox = (min(non_empty_rows), max(non_empty_rows),
                   min(non_empty_columns), max(non_empty_columns))

    # plot and print boundingBox
    bb = boundingBox
    plt.plot([bb[2], bb[3], bb[3], bb[2], bb[2]],
            [bb[0], bb[0], bb[1], bb[1], bb[0]],
            label="threshold %s" % threshold)
    print(boundingBox)

plt.xlim(0, variability.shape[1])
plt.ylim(variability.shape[0], 0)
plt.legend()

plt.show()
