import gc
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import numpy as np

class Demo:

    def __init__(self, imgs, ft, img_size):
        self.ft = ft # NCHW
        self.imgs = imgs
        self.num_imgs = len(imgs)
        self.img_size = img_size

    def plot_img_pairs(self, fig_size=3, alpha=0.45, scatter_size=70):

        fig, axes = plt.subplots(1, self.num_imgs, figsize=(fig_size*self.num_imgs, fig_size))

        plt.tight_layout()

        for i in range(self.num_imgs):
            axes[i].imshow(self.imgs[i])
            axes[i].axis('off')
            if i == 0:
                axes[i].set_title('source image')
            else:
                axes[i].set_title('target image')

        num_channel = self.ft.size(1)
        cos = nn.CosineSimilarity(dim=1)

        def onclick(event):
            print("clicked")
            if event.inaxes == axes[0]:
                with torch.no_grad():
                    print("inside")
                    #gets x and y coords of the event on the screen. 
                    x, y = int(np.round(event.xdata)), int(np.round(event.ydata))
                    #0 means the first image in the feature space. 
                    print("srcft before squeeze: ", self.ft.shape)
                    #gets one image but resizes it so it still has its outer dimension. 
                    src_ft = self.ft[0].unsqueeze(0)
                    print("srcft after squeeze: ", src_ft.shape)
                    #upsample the feature image into the normal image size. 
                    src_ft = nn.Upsample(size=(self.img_size, self.img_size), mode='bilinear')(src_ft)
                    print("srcft size: ", src_ft.shape)
                    #gets the map AT THE CHOSEN POINT. Gets ALL the channels. 
                    src_vec = src_ft[0, :, y, x].view(1, num_channel, 1, 1)  # 1, C, 1, 1
                    print("srcvec shape: ", src_vec.shape)
                    del src_ft
                    gc.collect()
                    torch.cuda.empty_cache()
                    #does same upsampling on target features. 
                    trg_ft = nn.Upsample(size=(self.img_size, self.img_size), mode='bilinear')(self.ft[1:])
                    print("trg ft size: ", trg_ft.shape)
                    #a cosine distance for each pixel. 
                    #srcvec shape:  torch.Size([1, 320, 1, 1])
                    #trg ft size:  torch.Size([1, 320, 100, 100]
                    #i think broadcasts teh last dimensions of the srcvec to 100, not sure. 
                    #eliminates dim 1 bc cos = nn.CosineSimilarity(dim=1) dim1 is specified. 
                    cos_map = cos(src_vec, trg_ft).cpu().numpy()  # N, H, W
                    print("cos map size: ", cos_map.shape)
                    #cos map is the cosine similarity taken between every "region" of the target image
                    #and the chosen region of the source image. 
                    del trg_ft
                    gc.collect()
                    torch.cuda.empty_cache()
                    print("further after cosine")
                    axes[0].clear()
                    axes[0].imshow(self.imgs[0])
                    axes[0].axis('off')
                    axes[0].scatter(x, y, c='r', s=scatter_size)
                    axes[0].set_title('source image')
                    print("futher")
                    for i in range(1, self.num_imgs):
                        print("i equals: ", i)
                        max_yx = np.unravel_index(cos_map[i-1].argmax(), cos_map[i-1].shape)
                        axes[i].clear()

                        heatmap = cos_map[i-1]
                        heatmap = (heatmap - np.min(heatmap)) / (np.max(heatmap) - np.min(heatmap))  # Normalize to [0, 1]
                        axes[i].imshow(self.imgs[i])
                        axes[i].imshow(255 * heatmap, alpha=alpha, cmap='viridis')
                        axes[i].axis('off')
                        axes[i].scatter(max_yx[1].item(), max_yx[0].item(), c='r', s=scatter_size)
                        axes[i].set_title('target image')

                    del cos_map
                    del heatmap
                    gc.collect()
                    print("done")
        print("got here")
        fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()

        