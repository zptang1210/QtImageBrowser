import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
# from torchvision.models import resnet50
from models.resnet import resnet50, resnet34, resnet18


def NT_XentLoss(z1, z2, temperature=0.5):
    z1 = F.normalize(z1, p=2, dim=-1)  # n x d         # 1 x d
    z2 = F.normalize(z2, p=2, dim=-1)  # n x m x d

    z1 = torch.unsqueeze(z1, dim=1)  # z1: n x 1 x d
    z2 = z2.permute(0, 2, 1)  # z2: n x d x m

    # r = torch.bmm(z1, z2)  # n x 1 x m
    r = torch.matmul(z1, z2)  # n x 1 x m  # Support broadcast
    r = torch.squeeze(r, dim=1)
    return F.cross_entropy(r, torch.zeros(r.shape[0], device=r.device, dtype=torch.int64))


def InfoNCE(q, k, tau=0.07):
    """
    Noise contrastive estimation loss, see MoCo paper https://arxiv.org/abs/1911.05722 eq. (1) for reference
    N: Batch size,
    Z: 1 (positive patch) + number of negative patches
    D: Dimension of the vector

    :param q: anchor pixel tensor of shape N x 1 x D
    :param k: pair tensor of shape N x Z x D, idx 0 positive patches, idx 1:Z negative patches
    :param tau: temperature hyperparameter
    :return:
    """

    q_times_k = torch.bmm(q, k.permute(0, 2, 1)).squeeze(dim=1)  # N x D
    q_times_k_pos = torch.bmm(q, k[:, 0:1, :].permute(0, 2, 1)).squeeze(dim=1)  # N x 1

    return -torch.mean(torch.log(torch.exp(q_times_k_pos / tau) / torch.sum(torch.exp(q_times_k / tau), dim=1)))


def mloss(z, temperature=0.5):
    # z: M x (1+1+L) x D

    z = F.normalize(z, p=2, dim=-1)  # M x (1+1+L) x D

    q = z[:, 0:1, :]
    k = z[:, 1:, :]

    return InfoNCE(q, k)


class projection_MLP(nn.Module):
    def __init__(self, in_dim, out_dim=256):
        super().__init__()
        hidden_dim = in_dim
        self.layer1 = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(inplace=True)
        )
        self.layer2 = nn.Linear(hidden_dim, out_dim)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        return x


def gkern(l=5, sig=1.):
    """\
    creates gaussian kernel with side length l and a sigma of sig
    """

    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    xx, yy = np.meshgrid(ax, ax)

    kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sig))

    return kernel / np.sum(kernel)


class SimCLR(nn.Module):

    def __init__(self, backbone="resnet50", projector=True, include_coords=False, pretrained=False,
                 normalize_embedding=True, tanh=False):
        super().__init__()

        self.include_coords = include_coords

        if backbone == "resnet18":
            self.backbone = resnet18(pretrained=pretrained, include_coords=self.include_coords)
        elif backbone == "resnet34":
            self.backbone = resnet34(pretrained=pretrained, include_coords=self.include_coords)
        elif backbone == "resnet50":
            self.backbone = resnet50(pretrained=pretrained, include_coords=self.include_coords)
        else:
            print(f"Error backbone {backbone}")

        self.d_embedding = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        if projector:
            self.projector = projection_MLP(self.d_embedding)
        else:
            self.projector = nn.Identity()

        if tanh:
            self.backbone.layer4[1].relu = nn.Tanh()
            self.backbone.layer4[2].relu = nn.Tanh()

        self.normalize_embedding = normalize_embedding
        # self.gaussian = gkern(32, 5)
        # self.gaussian = np.pad(self.gaussian, ((16, 16), (0, 0)))
        # self.gaussian = torch.from_numpy(self.gaussian).to(torch.float32).cuda()
        # self.gaussian -= self.gaussian.min()
        # self.gaussian /= self.gaussian.max()
        # self.gaussian = torch.unsqueeze(self.gaussian, dim=0)
        # self.gaussian = torch.unsqueeze(self.gaussian, dim=0)

    def forward(self, x1, train=False):
        # x1: n x d x h x w
        # x2: n x m x d x h x w # Target

        if self.include_coords:
            # print("x1", x1.shape)
            # print("self.gaussian", self.gaussian.shape)
            # gaussian = self.gaussian.repeat(x1.shape[0], 1, 1, 1)
            # x1 = torch.cat([x1, gaussian], dim=1)
            # print(f"x1.shape {x1.shape}")
            if train:
                n, m, d, h, w = x1.shape
            else:
                n, d, h, w = x1.shape

            x = torch.linspace(-1, 1, steps=h, device=x1.device)
            x = torch.unsqueeze(x, dim=1)
            x = x.repeat(1, w)

            x = torch.unsqueeze(x, dim=0)
            x = torch.unsqueeze(x, dim=0)
            if train:
                x = x.repeat(m, 1, 1, 1)
                x = torch.unsqueeze(x, dim=0)
                x = x.repeat(n, 1, 1, 1, 1)
            else:
                x = x.repeat(n, 1, 1, 1)

            y = torch.linspace(-1, 1, steps=w, device=x1.device)
            y = torch.unsqueeze(y, dim=0)
            y = y.repeat(h, 1)

            y = torch.unsqueeze(y, dim=0)
            y = torch.unsqueeze(y, dim=0)
            if train:
                y = y.repeat(m, 1, 1, 1)
                y = torch.unsqueeze(y, dim=0)
                y = y.repeat(n, 1, 1, 1, 1)
                x1 = torch.cat([x1, x, y], dim=2)
            else:
                y = y.repeat(n, 1, 1, 1)
                x1 = torch.cat([x1, x, y], dim=1)

        if train is False:
            h1 = self.backbone(x1)

            if self.normalize_embedding:
                return F.normalize(h1, dim=1)
            else:
                return h1
        else:

            m, l_plus_2, d, h, w = x1.shape  # M x (1+1+L) x D x H x W

            h1 = self.backbone(x1.reshape((-1, d, h, w)))
            h1 = self.projector(h1)
            h1 = h1.reshape((m, l_plus_2, -1))

            loss = mloss(h1)
            return {'loss': loss}
