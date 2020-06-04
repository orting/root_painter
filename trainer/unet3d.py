# pylint: disable=C0111, W0221, R0902
"""
U-Net architecture based on:
https://arxiv.org/abs/1505.04597
And modified to use Group Normalization
https://arxiv.org/abs/1803.08494
And then modified to use residual style connections.
With other alterations.

Copyright (C) 2019, 2020 Abraham George Smith

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import torch.nn as nn


class DownBlock(nn.Module):
    def __init__(self, in_channels):
        super().__init__()
        self.pool = nn.MaxPool3d(2)
        self.conv1 = nn.Sequential(
            nn.Conv3d(in_channels, in_channels*2,
                      kernel_size=3, padding=(1, 1, 1)),
            nn.ReLU(),
            nn.GroupNorm(32, in_channels*2)
        )
        self.conv2 = nn.Sequential(
            nn.Conv3d(in_channels*2, in_channels*2,
                      kernel_size=3, padding=(1, 1, 1)),
            nn.ReLU(),
            nn.GroupNorm(32, in_channels*2)
        )
        self.conv1x1 = nn.Sequential(
            # down sample channels again.
            nn.Conv3d(in_channels*2, in_channels,
                      kernel_size=1, stride=1, bias=False)
        )

    def forward(self, x):
        out1 = self.pool(x)
        out2 = self.conv1(out1)
        out3 = self.conv2(out2)
        out4 = self.conv1x1(out3)
        return out4 + out1

class DownBlock2D(nn.Module):
    def __init__(self, in_channels):
        super().__init__()
        self.pool = nn.MaxPool3d(2)
        self.conv1 = nn.Sequential(
            nn.Conv3d(in_channels, in_channels*2,
                      kernel_size=3, padding=(1, 1, 1)),
            nn.ReLU(),
            nn.GroupNorm(32, in_channels*2)
        )
        self.conv2 = nn.Sequential(
            nn.Conv3d(in_channels*2, in_channels*2,
                      kernel_size=3, padding=(1, 1, 1)),
            nn.ReLU(),
            nn.GroupNorm(32, in_channels*2)
        )
        self.conv1x1 = nn.Sequential(
            # down sample channels again.
            nn.Conv3d(in_channels*2, in_channels,
                      kernel_size=1, stride=1, bias=False)
        )

    def forward(self, x):
        out1 = self.pool(x)
        out2 = self.conv1(out1)
        out3 = self.conv2(out2)
        out4 = self.conv1x1(out3)
        return out4 + out1


def crop_tensor(tensor, target):
    """ Crop tensor to target size """
    _, _, tensor_depth, tensor_height, tensor_width = tensor.size()
    _, _, crop_depth, crop_height, crop_width = target.size()
    left = (tensor_width - crop_height) // 2
    top = (tensor_height - crop_width) // 2
    right = left + crop_width
    bottom = top + crop_height

    d_start = (tensor_depth - crop_depth) // 2
    d_end = d_start + crop_depth

    cropped_tensor = tensor[:, :, d_start:d_end, top: bottom, left: right]
    return cropped_tensor


class UpBlock(nn.Module):
    def __init__(self, in_channels):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.ConvTranspose3d(in_channels, in_channels,
                               kernel_size=2, stride=2, padding=1),
            nn.ReLU(),
            nn.GroupNorm(32, in_channels)
        )
        self.conv2 = nn.Sequential(
            nn.Conv3d(in_channels, in_channels,
                      kernel_size=3, padding=1),
            nn.ReLU(),
            nn.GroupNorm(32, in_channels)
        )
        self.conv3 = nn.Sequential(
            nn.Conv3d(in_channels, in_channels,
                      kernel_size=3, padding=1),
            nn.ReLU(),
            nn.GroupNorm(32, in_channels)
        )

    def forward(self, x, down_out):
        out = self.conv1(x)
        cropped = crop_tensor(down_out, out)
        out = cropped + out # residual
        out = self.conv2(out)
        out = self.conv3(out)
        return out



class UNet3D(nn.Module):
    def __init__(self, im_channels=3, out_channels=3):
        super().__init__()
        self.conv_in = nn.Sequential(
            nn.Conv3d(im_channels, 64, kernel_size=3, padding=0),
            nn.ReLU(),
            nn.GroupNorm(32, 64),
            nn.Conv3d(64, 64, kernel_size=3, padding=0),
            nn.ReLU(),
            nn.GroupNorm(32, 64)
            # now at 568 x 568, 64 channels
        )
        self.down1 = DownBlock(64)
        self.down2 = DownBlock(64)
        self.down3 = DownBlock(64)
        self.down4 = DownBlock(64)
        self.up1 = UpBlock(64)
        self.up2 = UpBlock(64)
        self.up3 = UpBlock(64)
        self.up4 = UpBlock(64)
        self.conv_out = nn.Sequential(
            nn.Conv3d(64, out_channels, kernel_size=1, padding=0),
            nn.ReLU()
        )

    def forward(self, x):
        out1 = self.conv_in(x)
        #print('out1 shape', out1.shape) # 
        out2 = self.down1(out1)
        #print('out2 shape', out2.shape) # 
        out3 = self.down2(out2)
        #print('out3 shape', out3.shape) # 
        out4 = self.down3(out3)
        #print('out4 shape', out4.shape) # 1, 64, 3, 31, 31
        out5 = self.down4(out4)
        #print('out5 shape', out5.shape)
        #print('bottleneck')
        out = self.up1(out5, out4)
        #print('after up1')
        out = self.up2(out, out3)
        #print('after up2')
        out = self.up3(out, out2)
        #print('after up3')
        out = self.up4(out, out1)
        #print('after up4')
        out = self.conv_out(out)
        #print('after upout')
        return out