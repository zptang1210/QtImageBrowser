import torch
from torch.nn import functional as F

from .resnet import BasicBlock, ResNet, Bottleneck


class Resnet18(ResNet):
    def __init__(self, use_globalAvgPooling=False, normalize=True, **kwargs):
        super(Resnet18, self).__init__(
            BasicBlock,
            [2, 2, 2, 2],
            **kwargs
        )
        self.use_globalAvgPooling = use_globalAvgPooling
        self.normalize = normalize

    def _forward_impl(self, x):
        # See note [TorchScript super()]
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        if self.use_globalAvgPooling:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
        if self.normalize:
            x = F.normalize(x, dim=1)
        return x


class Resnet34(ResNet):
    def __init__(self, use_globalAvgPooling=False, normalize=True, **kwargs):
        super(Resnet34, self).__init__(
            BasicBlock,
            [3, 4, 6, 3],
            **kwargs
        )
        self.use_globalAvgPooling = use_globalAvgPooling
        self.normalize = normalize

    def _forward_impl(self, x):
        # See note [TorchScript super()]
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        if self.use_globalAvgPooling:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
        if self.normalize:
            x = F.normalize(x, dim=1)
        return x


class Resnet50(ResNet):
    def __init__(self, use_globalAvgPooling=False, normalize=True, **kwargs):
        super(Resnet50, self).__init__(
            Bottleneck,
            [3, 4, 6, 3],
            **kwargs
        )
        self.use_globalAvgPooling = use_globalAvgPooling
        self.normalize = normalize

    def _forward_impl(self, x):
        # See note [TorchScript super()]
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        #x = F.normalize(x, dim=1)
        if self.use_globalAvgPooling:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
        if self.normalize:
            x = F.normalize(x, dim=1)
        return x

class Resnet50(ResNet):
    def __init__(self, use_globalAvgPooling=False, normalize=True, **kwargs):
        super(Resnet50, self).__init__(
            Bottleneck,
            [3, 4, 6, 3],
            **kwargs
        )
        self.use_globalAvgPooling = use_globalAvgPooling
        self.normalize = normalize

    def _forward_impl(self, x):
        # See note [TorchScript super()]
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        #x = F.normalize(x, dim=1)
        if self.use_globalAvgPooling:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
        if self.normalize:
            x = F.normalize(x, dim=1)
        return x


class DilResnet18(ResNet):
    def __init__(self, use_globalAvgPooling=False, normalize=True, replace_stride_with_dilation=[False, True, True], **kwargs):
        super(DilResnet18, self).__init__(
            BasicBlock,
            [2, 2, 2, 2],
            replace_stride_with_dilation=replace_stride_with_dilation,
            **kwargs
        )
        self.use_globalAvgPooling = use_globalAvgPooling
        self.normalize = normalize

    def _forward_impl(self, x):
        # See note [TorchScript super()]
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        if self.use_globalAvgPooling:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
        if self.normalize:
            x = F.normalize(x, dim=1)
        return x


class DilResnet50(ResNet):
    def __init__(self, use_globalAvgPooling=False, normalize=True, replace_stride_with_dilation=[False, True, True], **kwargs):
        super(DilResnet50, self).__init__(
            Bottleneck,
            [3, 4, 6, 3],
            replace_stride_with_dilation=replace_stride_with_dilation,
            **kwargs
        )
        self.use_globalAvgPooling = use_globalAvgPooling
        self.normalize = normalize

    def _forward_impl(self, x):
        # See note [TorchScript super()]
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        if self.use_globalAvgPooling:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
        if self.normalize:
            x = F.normalize(x, dim=1)
        return x


