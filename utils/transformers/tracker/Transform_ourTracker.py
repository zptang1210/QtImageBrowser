import time
import math
import argparse
import numpy as np
import cv2
import torch
from torchvision import transforms
import torch.nn.functional as F
from collections import defaultdict, OrderedDict
from utils.transformers.Transform_base import Transform_base
from multiprocessing import Process, Queue

from .Transform_trackerBase import Transform_trackerBase
from .models.models import Resnet18, Resnet34, Resnet50, DilResnet18, DilResnet50


def selectROI(queue, frame, flag):
    bbox = cv2.selectROI(frame, flag)
    queue.put(bbox)


######## CONSTANTS ########

pytorch_mean = torch.tensor([0.485, 0.456, 0.406])
pytorch_std = torch.tensor([0.229, 0.224, 0.225])

transform = transforms.Compose(
    [
        transforms.Normalize(mean=pytorch_mean, std=pytorch_std)
    ]
)


######## FUNCTIONS ########

def sign(x):
    if x < 0:
        return -1
    else:
        return 1


def get_new_patch_location(idx_best_embedding_distance, current_patch_coord, search_window, patch_w, patch_h, profiler):
    # start_time = time.perf_counter() # -------------- START --------------- #
    total_size = search_window * 2 + 1
    # end_time = time.perf_counter()
    # profiler["a0"] += end_time - start_time # -------------- STOP --------------- #

    # start_time = time.perf_counter() # -------------- START --------------- #
    dy = idx_best_embedding_distance.item()
    # end_time = time.perf_counter()
    # profiler["a10"] += end_time - start_time # -------------- STOP --------------- #

    # start_time = time.perf_counter() # -------------- START --------------- #
    dy = dy % total_size - search_window
    # end_time = time.perf_counter()
    # profiler["a11"] += end_time - start_time # -------------- STOP --------------- #

    # start_time = time.perf_counter() # -------------- START --------------- #
    dx = idx_best_embedding_distance.item() // total_size - search_window
    # end_time = time.perf_counter()
    # profiler["a2"] += end_time - start_time # -------------- STOP --------------- #

    # start_time = time.perf_counter() # -------------- START --------------- #
    r = [current_patch_coord[0] + dx, current_patch_coord[1] + dy, patch_w, patch_h]
    # end_time = time.perf_counter()
    # profiler["a3"] += end_time - start_time # -------------- STOP --------------- #

    return r

######## OurTracker CLASS ########


class OurTracker:

    @torch.no_grad()
    def __init__(self,
                 model: str,
                 ground_truths: tuple,
                 min_patch_size: int = 32,
                 search_window: int = 20,
                 embedding_momentum: float = 0,
                 scale_search: int = 0,
                 weights=None,
                 use_pad=False,
                 center_momentum: float = 0,
                 use_optical_flow: bool = False,
                 use_globalAvgPooling=True
                 ):

        """

        :param model:
        :param ground_truths:
        :param min_patch_size:
        :param search_window:
        :param embedding_to_compare:
        :param scale_search:
        :param save_video_freq:
        :param save_videopatch_freq:
        :param save_first_last_frames_freq:
        """

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = model
        self.search_window = search_window
        self.embedding_momentum = embedding_momentum
        self.scale_search = scale_search
        self.pad = use_pad
        self.use_globalAvgPooling = use_globalAvgPooling
        self.center_momentum = center_momentum
        self.use_optical_flow = use_optical_flow

        if self.use_optical_flow and self.center_momentum < 1:
            raise ValueError(f"With use_optical_flow, momentum should be 1, {self.center_momentum} given")

        if self.use_optical_flow:
            import sys
            sys.path.append("../RAFT/core")
            from raft import RAFT
            #parser.add_argument('--model', help="restore checkpoint")
            #parser.add_argument('--path', help="dataset for evaluation")

            from argparse import Namespace

            args = Namespace(small=False, mixed_precision=False, alternate_corr=False)
            print(args.small, args.mixed_precision, args.alternate_corr)
            # parser = argparse.ArgumentParser()
            # parser.add_argument('--model', help="restore checkpoint")
            # parser.add_argument('--path', help="dataset for evaluation")
            # parser.add_argument('--small', action='store_true', help='use small model')
            # parser.add_argument('--mixed_precision', action='store_true', help='use mixed precision')
            # parser.add_argument('--alternate_corr', action='store_true', help='use efficent correlation implementation')
            # args = parser.parse_args()

            self.opticalflow_model = torch.nn.DataParallel(RAFT(args))
            missing_keys, unexpected_keys = self.opticalflow_model.load_state_dict(torch.load("../RAFT/models/raft-things.pth"))

            print("################# OPTICALFLOW MODEL ############################")
            print("####### missing_keys #######")
            print(missing_keys)
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            print("####### unexpected_keys #######")
            print(unexpected_keys)
            print("---------------------------------------------")

            self.opticalflow_model.to(self.device)
            self.opticalflow_model.eval()

        # profiler = {}
        self.profiler = defaultdict(lambda: 0)

        start_time = time.perf_counter()  # -------------- START --------------- #

        if weights is not None:
            self.load_weights(weights)

        self.model.eval()


        self.n_patches = 0

        x, y, w, h = ground_truths

        if w < h:# and min_patch_size > w:
            self.fixed_patch_w = min_patch_size
            self.fixed_patch_h = round((h / w) * min_patch_size)
        elif w >= h:# and min_patch_size > h:
            self.fixed_patch_h = min_patch_size
            self.fixed_patch_w = round((w / h) * min_patch_size)
        # else:
        #     self.fixed_patch_h = h
        #     self.fixed_patch_w = w

        #self.fixed_patch_h = 128
        #self.fixed_patch_w = round(self.fixed_patch_h * w / h)

        # Initial bounding box size
        self.patch_w = w
        self.patch_h = h

        self.current_patch_coord = [int(x), int(y), self.patch_w, self.patch_h]

        if self.pad:
            x += (self.search_window + self.patch_w)
            y += (self.search_window + self.patch_h)

            self.current_patch_coord[0] += (self.search_window + self.patch_w)
            self.current_patch_coord[1] += (self.search_window + self.patch_h)



        self.current_delta = [0., 0.]
        self.target_delta = [0., 0.]


        self.target_embedding = None


        if self.use_optical_flow: # Used for optical flow
            self.previous_frame = None

        end_time = time.perf_counter()
        self.profiler["initialization"] = end_time - start_time  # -------------- STOP --------------- #

    def load_weights(self, weights):
        map_location = {f'cuda:{0}': f'cuda:{0}'}
        state_dict = torch.load(weights, map_location=map_location)["state_dict"]

        new_state_dict = OrderedDict()

        for k, v in state_dict.items():
            if k.startswith("encoder"):
                name = k[len("encoder."):]
            #elif not k.startswith("backbone"):
            #    name = "backbone." + k
            else:
                name = k
            new_state_dict[name] = v

        missing_keys, unexpected_keys = self.model.load_state_dict(new_state_dict, strict=False)

        print("#############################################")
        print("####### missing_keys #######")
        print(missing_keys)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print("####### unexpected_keys #######")
        print(unexpected_keys)
        print("---------------------------------------------")

    def delete_padding(self, coords):
        """

        :param coords:  (x, y, w, h)
        :return: (x-(search_window+patch_w), y-(search_window+patch_h), w, h)
        """
        if self.pad:
            return [coords[0] - (self.search_window+self.patch_w), coords[1] - (self.search_window+self.patch_h), coords[2], coords[3]]
        return coords

    @torch.no_grad()
    def track(self, current_frame):

        current_frame = torch.from_numpy(current_frame) / 255.
        current_frame = current_frame.permute(2, 0, 1)
        print("current_frame", current_frame.shape)
        self.n_patches += 1

        print(f"Tracking frame {self.n_patches}")

        # Update patch location
        current_frame = torch.unsqueeze(current_frame, dim=0)

        # Normalize the current frame
        current_frame = transform(current_frame)

        # For optical flow we need frames that are divisible by 8
        if self.use_optical_flow:
            current_frame = F.pad(current_frame, (
                0,
                math.ceil(current_frame.shape[3]/8)*8-current_frame.shape[3],
                0,
                math.ceil(current_frame.shape[2]/8)*8-current_frame.shape[2]
            ))

        # Update center patch position
        self.target_delta[0] = self.center_momentum * self.target_delta[0] + (1 - self.center_momentum) * self.current_delta[0]
        self.target_delta[1] = self.center_momentum * self.target_delta[1] + (1 - self.center_momentum) * self.current_delta[1]
        self.current_patch_coord[0] += self.target_delta[0]
        self.current_patch_coord[1] += self.target_delta[1]

        self.current_patch_coord[0] = round(self.current_patch_coord[0])
        self.current_patch_coord[1] = round(self.current_patch_coord[1])

        # Update center patch position using optical flow
        if self.use_optical_flow and self.previous_frame is not None:
            flow_low, flow_up = self.opticalflow_model(self.previous_frame, current_frame, iters=20, test_mode=True)
            current_patch_coord_no_pad = self.delete_padding(self.current_patch_coord)
            flow_local = flow_up[
                         0,
                         :,
                         round((current_patch_coord_no_pad[1])+0.25*current_patch_coord_no_pad[3]):round(current_patch_coord_no_pad[1]+0.75*current_patch_coord_no_pad[3]),
                         round(current_patch_coord_no_pad[0]+0.25*current_patch_coord_no_pad[2]):round(current_patch_coord_no_pad[0]+0.75*current_patch_coord_no_pad[2]),
                         ]

            if  not(flow_local.shape[2] == 0 or flow_local.shape[1] == 0):
                self.current_patch_coord[0] += round(flow_local[0].mean().item())
                self.current_patch_coord[1] += round(flow_local[1].mean().item())

        # Pad the frame, it is done that after computing optical flow to not compute the optical flow on the padding
        if self.pad:
            current_frame = F.pad(current_frame, (self.search_window + self.patch_w, self.search_window + self.patch_w, self.search_window + self.patch_h, self.search_window + self.patch_h))

        _, _, frame_height, frame_width = current_frame.shape

        # To compute the momentum
        past_patch_coord = self.current_patch_coord.copy()

        # If the search window around the current patch coords goes outside the frame
        if self.current_patch_coord[0] < self.search_window \
                or self.current_patch_coord[0] + self.patch_w + self.search_window >= frame_width \
                or self.current_patch_coord[1] < self.search_window \
                or self.current_patch_coord[1] + self.patch_h + self.search_window > frame_height:
            print("The search window is outside of the frame.")
            return None

        #current_frame = current_frame / 255.


        #current_frame = torch.unsqueeze(current_frame, dim=0)
        current_frame = current_frame.type(torch.FloatTensor)

        # If it is the first frame
        if self.n_patches == 1:
            # Small patch
            self.current_patch = current_frame[:, :,
                                 self.current_patch_coord[1]:self.current_patch_coord[1] + self.patch_h,
                                 self.current_patch_coord[0]:self.current_patch_coord[0] + self.patch_w
                                 ]
            self.current_patch = F.interpolate(self.current_patch, (self.fixed_patch_h, self.fixed_patch_w)).to(
                self.device, non_blocking=True)

            if self.pad:
                return [
                    self.current_patch_coord[0] - (self.search_window + self.patch_w),
                    self.current_patch_coord[1] - (self.search_window + self.patch_h),
                    self.current_patch_coord[2],
                    self.current_patch_coord[3],
                    ]
            else:
                return self.current_patch_coord

        else:
            # Large patch
            next_patches = current_frame[:, :,
                           self.current_patch_coord[1] - self.search_window
                           :self.current_patch_coord[1] + self.patch_h + self.search_window,
                           self.current_patch_coord[0] - self.search_window
                           :self.current_patch_coord[0] + self.patch_w + self.search_window
                           ]

            # If the search window goes outside the image
            if next_patches.shape[2] != self.patch_h + 2 * self.search_window or \
                    next_patches.shape[3] != self.patch_w + 2 * self.search_window:
                raise Exception(
                    f"Shouldn't be here, next_patches.shape {next_patches.shape}, current_patch_coord {self.current_patch_coord}, frames_width {frame_width}, frames_height {frame_height}")

            # start_time = time.perf_counter() # -------------- START --------------- #
            next_patches = next_patches \
                .unfold(2, self.patch_h, 1) \
                .unfold(3, self.patch_w, 1) \
                .transpose(1, 3) \
                .contiguous() \
                .view(-1, 3, self.patch_h, self.patch_w)

            # print("next_patches before resizing", next_patches.shape)
            # stop_time = time.perf_counter()
            # profiler["patches_processing"] += (stop_time - start_time) # -------------- STOP --------------- #

            # start_time = time.perf_counter() # -------------- START --------------- #
            next_patches = F.interpolate(next_patches, (self.fixed_patch_h, self.fixed_patch_w))
            # print("next_patches after resizing", next_patches.shape)
            # stop_time = time.perf_counter()
            # profiler["interpolate"] += (stop_time - start_time) # -------------- STOP --------------- #

            # start_time = time.perf_counter() # -------------- START --------------- #
            next_patches = next_patches.to(self.device, non_blocking=True)

            # print(self.current_patch)
            # torchvision.utils.save_image(self.current_patch * 255, "current_frame.png")
            # torchvision.utils.save_image(torchvision.utils.make_grid(next_patches * 255, nrow=round(math.sqrt(len(next_patches)))), 'grid_frames.png')

            next_patches = torch.cat((next_patches, self.current_patch))
            # stop_time = time.perf_counter()
            # profiler["patches_to_gpu"] += (stop_time - start_time) # -------------- STOP --------------- #

            # start_time = time.perf_counter() # -------------- START --------------- #
            # Compute all the candidate embeddings
            #print("next_patches.shape", next_patches.shape)


            next_patches_embedding = self.model(next_patches)
            # end_time = time.perf_counter()
            # profiler["inference"] += (end_time - start_time) # -------------- STOP --------------- #
            #print("next_patches_embedding", next_patches_embedding.shape)


            # Get current embedding
            current_patch_embedding = next_patches_embedding[-1:]

            if self.target_embedding is None:
                self.target_embedding = current_patch_embedding.clone()
            else:
                self.target_embedding = self.embedding_momentum * self.target_embedding + (1 - self.embedding_momentum) * current_patch_embedding


            # Get all next embeddings
            next_patches_embedding = next_patches_embedding[:-1]
            if self.use_globalAvgPooling:
                next_patches_embedding = next_patches_embedding.permute(1, 0)

            # start_time = time.perf_counter() # -------------- START --------------- #


            if self.use_globalAvgPooling:
                embedding_distances = torch.mm(self.target_embedding, next_patches_embedding)
            else:
                embedding_distances = F.conv2d(self.target_embedding, next_patches_embedding)
            #print("embedding_distances", embedding_distances.shape)
            #
            # end_time = time.perf_counter()
            # profiler["matrix_multiplication"] += (end_time - start_time) # -------------- STOP --------------- #

            # start_time = time.perf_counter() # -------------- START --------------- #
            # Find closest embedding
            #print(embedding_distances)
            idx_best_embedding_distance = torch.argmax(embedding_distances)
            #print("idx_best_embedding_distance", idx_best_embedding_distance)

            # end_time = time.perf_counter()
            # profiler["argmax"] += (end_time - start_time) # -------------- STOP --------------- #

            # start_time = time.perf_counter() # -------------- START --------------- #
            self.current_patch_coord = get_new_patch_location(idx_best_embedding_distance, self.current_patch_coord,
                                                              self.search_window, self.patch_w, self.patch_h, self.profiler)

            # start_time = time.perf_counter() # -------------- START --------------- #

            # If search different sizes
            if self.scale_search > 0:
                next_patches = []
                scale_range = range(- self.scale_search, self.scale_search + 1)

                # Get all the patches-
                for dsize in scale_range:
                    sized_patch = current_frame[:, :, self.current_patch_coord[1] - dsize
                                                      :self.current_patch_coord[1] + self.patch_h + dsize,
                                  self.current_patch_coord[0] - dsize
                                  :self.current_patch_coord[0] + self.patch_w + dsize
                                  ]

                    if sized_patch.shape[2] != self.patch_h + 2 * dsize or \
                            sized_patch.shape[3] != self.patch_w + 2 * dsize:
                        break
                        # raise Exception(
                        #    f"Shouldn't be here, current_patch_coord: {current_patch_coord} patch_size {patch_size} dsize {dsize}")

                    sized_patch = F.interpolate(sized_patch, (self.fixed_patch_h, self.fixed_patch_w))
                    next_patches.append(sized_patch)

                next_patches = torch.cat(next_patches).to(self.device, non_blocking=True)

                # Patches through the network
                next_patches_embedding = self.model(next_patches)


                if self.use_globalAvgPooling:
                    next_patches_embedding = next_patches_embedding.permute(1, 0)

                # # Get best patch
                if self.use_globalAvgPooling:
                    embedding_distances = torch.mm(self.target_embedding, next_patches_embedding)
                else:
                    embedding_distances = F.conv2d(self.target_embedding, next_patches_embedding)

                idx_best_embedding_distance = torch.argmax(embedding_distances)

                seleted_dsize = scale_range[idx_best_embedding_distance]

                temp_patch_h = self.patch_h + 2 * seleted_dsize
                temp_patch_w = self.patch_w + 2 * seleted_dsize

                # Only udate scale if the patch is not too much

                if temp_patch_h < 8 or temp_patch_w < 8:
                    seleted_dsize = 0
                else:
                    self.patch_h = temp_patch_h
                    self.patch_w = temp_patch_w


                # # If the patch becomes too small we stop the video
                # if self.patch_h < 8 or self.patch_w < 8:
                #     print("The patch became too small.")
                #     return None

                self.current_patch_coord = [self.current_patch_coord[0] - seleted_dsize, self.current_patch_coord[1] - seleted_dsize,
                                            self.patch_w, self.patch_h]


            # end_time = time.perf_counter()
            # profiler["scale_search"] += (end_time - start_time) # -------------- STOP --------------- #

            self.current_patch = next_patches[idx_best_embedding_distance:idx_best_embedding_distance + 1, :, :, :].clone()


            self.current_delta[0] = round(
                (self.current_patch_coord[0] + self.current_patch_coord[2] / 2) - (past_patch_coord[0] + past_patch_coord[2] / 2))
            self.current_delta[1] = round(
                (self.current_patch_coord[1] + self.current_patch_coord[3] / 2) - (past_patch_coord[1] + past_patch_coord[3] / 2))

            if self.use_optical_flow:
                if self.pad:
                    self.previous_frame = torch.clone(current_frame[
                                                      :,
                                                      :,
                                                      self.search_window + self.patch_h:-(self.search_window + self.patch_h),
                                                      self.search_window + self.patch_w:-(self.search_window + self.patch_w)])
                else:
                    self.previous_frame = torch.clone(current_frame)


            if self.pad:
                return [
                    self.current_patch_coord[0] - (self.search_window + self.patch_w),
                    self.current_patch_coord[1] - (self.search_window + self.patch_h),
                    self.current_patch_coord[2],
                    self.current_patch_coord[3]]
            else:
                return self.current_patch_coord



class Transform_ourTracker(Transform_trackerBase):
    command = 'ourtracker'

    def __init__(self):
        super().__init__()

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    def getArgParser(self):
        parser = argparse.ArgumentParser(description='Argument parser for tracker')
        parser.add_argument('--bbox', nargs='+', type=int)
        return parser


    def init(self, args):
        print("ourTracker init")
        #### PARAMS ####
        self.backbone = "resnet50"
        self.embedding_momentum = 0.
        self.scale_search = 1
        self.weights = None
        self.pad = True
        self.search_window = 20
        self.center_momentum = 1.
        self.use_optical_flow = False
        self.use_globalAvgPooling = False
        self.normalize = True

        #####

        # Inital bbox
        initial_bbox = tuple(args.bbox)

        # Model to use for the tracking
        if self.backbone == "resnet18":
            model = Resnet18(use_globalAvgPooling=self.use_globalAvgPooling, normalize=self.normalize)
        elif self.backbone == "resnet34":
            model = Resnet34(use_globalAvgPooling=self.use_globalAvgPooling, normalize=self.normalize)
        elif self.backbone == "resnet50":
            model = Resnet50(use_globalAvgPooling=self.use_globalAvgPooling, normalize=self.normalize)
        else:
            raise ValueError(f"Unknown backbone {self.backbone}")

        model = model.to(self.device)
        self.bbox = list(map(int, initial_bbox))
        self.tracker = OurTracker(
            model,
            initial_bbox,
            embedding_momentum=self.embedding_momentum,
            scale_search=self.scale_search,
            weights=self.weights,
            use_pad=self.pad,
            search_window=self.search_window,
            center_momentum=self.center_momentum,
            use_optical_flow=self.use_optical_flow,
            use_globalAvgPooling=self.use_globalAvgPooling)


    def update(self, image):
        bbox = self.tracker.track(image)
        return bbox
