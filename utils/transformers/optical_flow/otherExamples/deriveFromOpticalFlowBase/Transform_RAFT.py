import sys
sys.path.append('./utils/transformers/optical_flow/thirdparty/RAFT/core')
import argparse
from .thirdparty.RAFT.core.utils.utils import InputPadder
import torch
import numpy as np
from .thirdparty.RAFT.core.utils import flow_viz
from utils.transformers.optical_flow.Transform_opticalFlowBase import Transform_opticalFlowBase
from .thirdparty.RAFT.core.raft import RAFT

class Transform_RAFT(Transform_opticalFlowBase):
    command = 'raft'

    def __init__(self):
        super().__init__()
        self.DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    def load_image(self, img):
        img_ = img.astype(np.uint8)
        img_tensor = torch.from_numpy(img_).permute(2, 0, 1).float()
        return img_tensor[None].to(self.DEVICE)

    def viz(self, flo):
        flo = flo[0].permute(1,2,0).cpu().numpy()
        flo_img = flow_viz.flow_to_image(flo)
        # flo_img = flo_img[:, :, [2, 1, 0]]
        return flo_img

    def getArgParser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--model', default='./utils/transformers/optical_flow/thirdparty/RAFT/models/raft-things.pth', help="restore checkpoint")
        # parser.add_argument('--path', help="dataset for evaluation")
        parser.add_argument('--small', action='store_true', help='use small model')
        parser.add_argument('--mixed_precision', action='store_true', help='use mixed precision')
        parser.add_argument('--alternate_corr', action='store_true', help='use efficent correlation implementation')
        return parser

    def processImageCollection(self, model, args):
        imgCol = model # change a name to avoid confusion

        raftmodel = torch.nn.DataParallel(RAFT(args))
        raftmodel.load_state_dict(torch.load(args.model))

        raftmodel = raftmodel.module
        raftmodel.to(self.DEVICE)
        raftmodel.eval()

        imgNum = imgCol.length()
        assert imgNum >= 2
        with torch.no_grad():
            for i in range(imgNum-1):
                img1, img1_name = imgCol.get(i)
                img2, img2_name = imgCol.get(i+1)
                print(f'- processing {i}/{imgNum-1} - {img1_name} -> {img2_name}')

                img1 = self.load_image(img1)
                img2 = self.load_image(img2)

                padder = InputPadder(img1.shape)
                img1, img2 = padder.pad(img1, img2)

                flow_low, flow_up = raftmodel(img1, img2, iters=20, test_mode=True)
                
                # # use their own tool for visualization
                # flo_img = self.viz(flow_up)

                # use the tool we provide for visualization
                flo = flow_up[0].permute(1,2,0).cpu().numpy()
                flo_img = self.flowToImage(flo)

                yield flo_img, img1_name