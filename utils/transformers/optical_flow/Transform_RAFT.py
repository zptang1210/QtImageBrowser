import sys
sys.path.append('./utils/transformers/optical_flow/thirdparty/RAFT/core')
import numpy as np
import torch
from .thirdparty.RAFT.core.utils.utils import InputPadder
from .thirdparty.RAFT.core.raft import RAFT
from utils.transformers.optical_flow.Transform_opticalFlowFramework import Transform_opticalFlowFramework

class Transform_RAFT(Transform_opticalFlowFramework):
    command = 'raft'

    def __init__(self):
        super().__init__()
        self.DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    def load_image(self, img):
        img_ = img.astype(np.uint8)
        img_tensor = torch.from_numpy(img_).permute(2, 0, 1).float()
        return img_tensor[None].to(self.DEVICE)

    def getArgParser(self):
        parser = super().getArgParser()
        parser.add_argument('--model', default='./utils/transformers/optical_flow/thirdparty/RAFT/models/raft-things.pth', help="restore checkpoint")
        # parser.add_argument('--path', help="dataset for evaluation")
        parser.add_argument('--small', action='store_true', help='use small model')
        parser.add_argument('--mixed_precision', action='store_true', help='use mixed precision')
        parser.add_argument('--alternate_corr', action='store_true', help='use efficent correlation implementation')
        return parser

    def initOpticalFlowAlgorithm(self, model, args):
        raftmodel = torch.nn.DataParallel(RAFT(args))
        raftmodel.load_state_dict(torch.load(args.model))

        self.raftmodel = raftmodel.module
        self.raftmodel.to(self.DEVICE)
        self.raftmodel.eval()

    def computeOpticalFlow(self, img1, img2):
        img1 = self.load_image(img1)
        img2 = self.load_image(img2)

        padder = InputPadder(img1.shape)
        img1, img2 = padder.pad(img1, img2)

        flow_low, flow_up = self.raftmodel(img1, img2, iters=20, test_mode=True)

        flo = flow_up[0].permute(1,2,0).cpu().numpy()

        return flo
