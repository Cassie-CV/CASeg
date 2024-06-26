import sys
from collections import OrderedDict
import torch.nn as nn
import torch
import functools

def conv3x3x3(in_planes, out_planes, stride=1):
    """3x3x3 convolution with padding"""
    return nn.Conv3d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


def conv1x1x1(in_planes, out_planes, stride=1):
    """1x1x1 convolution"""
    return nn.Conv3d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)

class FilterLayer(nn.Module):
    def __init__(self, in_planes, out_planes, reduction=16):
        super(FilterLayer, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool3d(1)
        self.fc = nn.Sequential(
            nn.Linear(in_planes, out_planes // reduction),
            nn.ReLU(inplace=True),
            nn.Linear(out_planes // reduction, out_planes),
            nn.Sigmoid()
        )
        self.out_planes = out_planes

    def forward(self, x):
        # print("-------:",x.shape)
        b, c, _, _, _= x.size()
        y = self.avg_pool(x).view(b, c)
        # print("-------:",y.shape)
        y = self.fc(y)
        # print("-------:",y.shape)
        y=y.view(b, self.out_planes, 1, 1,1)
        return y

'''
Feature Separation Part
'''
class FSP(nn.Module):
    def __init__(self, in_planes, out_planes, reduction=16):
        super(FSP, self).__init__()
        self.filter = FilterLayer(2*in_planes, out_planes, reduction)
        # self.filter = FilterLayer(in_planes, out_planes, reduction)

    def forward(self, guidePath, mainPath):
        # print(guidePath.shape,mainPath.shape)
        combined = torch.cat((guidePath, mainPath), dim=1)
        channel_weight = self.filter(combined)
        # print(channel_weight.shape)
        # print("++++++++++++++++++++++")
        out = mainPath + channel_weight * guidePath
        return out

'''
SA-Gate
'''
class SAGate(nn.Module):
    # def __init__(self, in_planes, reduction=16, bn_momentum=0.0003):
    def __init__(self, in_planes):
        self.init__ = super(SAGate, self).__init__()
        self.in_planes = in_planes
        # self.out_planes = in_planes
        # self.bn_momentum = bn_momentum

        # self.fsp_rgb = FSP(self.in_planes, self.out_planes, reduction)
        # self.fsp_hha = FSP(self.in_planes, self.out_planes, reduction)

        self.gate_rgb = nn.Conv3d(self.in_planes*2, 1, kernel_size=1, bias=True)
        self.gate_hha = nn.Conv3d(self.in_planes*2, 1, kernel_size=1, bias=True)

        self.relu1 = nn.ReLU()
        self.relu2 = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, rgb, hha):
        # rgb, hha = x
        # b, c, h, w = rgb.size()

        # rec_rgb = self.fsp_rgb(hha, rgb)
        # rec_hha = self.fsp_hha(rgb, hha)
        rec_rgb=rgb
        rec_hha=hha
        cat_fea = torch.cat([rec_rgb, rec_hha], dim=1)
        # print(rec_rgb.shape,cat_fea.shape)
        attention_vector_l = self.gate_rgb(cat_fea)
        attention_vector_r = self.gate_hha(cat_fea)

        attention_vector = torch.cat([attention_vector_l, attention_vector_r], dim=1)
        attention_vector = self.softmax(attention_vector)
        
        attention_vector_l, attention_vector_r = attention_vector[:, 0:1, :, :,:], attention_vector[:, 1:2, :, :,:]
        # print(rec_rgb.shape,cat_fea.shape,attention_vector.shape,attention_vector_l.shape)
        merge_feature = rgb*attention_vector_l + hha*attention_vector_r
        # merge_feature =  torch.cat([rgb*attention_vector_l, hha*attention_vector_r], dim=1)

        rgb_out = (rgb + merge_feature) / 2
        hha_out = (hha + merge_feature) / 2
        
        
        # rgb_out = self.relu1(rgb_out)
        # hha_out = self.relu2(hha_out)
        merge_feature =  torch.cat([rgb_out, hha*hha_out], dim=1) 

        # return [rgb_out, hha_out], merge_feature
        return merge_feature
        
class SAGate_all(nn.Module):
    def __init__(self, in_planes, reduction=4, bn_momentum=0.0003):
    # def __init__(self, in_planes):
        self.init__ = super(SAGate_all, self).__init__()
        self.in_planes = in_planes
        self.out_planes = in_planes#//2
        self.bn_momentum = bn_momentum

        self.fsp_rgb = FSP(self.in_planes, self.out_planes, reduction)
        self.fsp_hha = FSP(self.in_planes, self.out_planes, reduction)

        self.gate_rgb = nn.Conv3d(self.in_planes*2, 1, kernel_size=1, bias=True)
        self.gate_hha = nn.Conv3d(self.in_planes*2, 1, kernel_size=1, bias=True)

        self.relu1 = nn.ReLU()
        self.relu2 = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, rgb, hha):
        # rgb, hha = x
        # b, c, h, w = rgb.size()

        rec_rgb = self.fsp_rgb(hha, rgb)
        rec_hha = self.fsp_hha(rgb, hha)
        # rec_rgb=rgb
        # rec_hha=hha
        cat_fea = torch.cat([rec_rgb, rec_hha], dim=1)
        # print(rec_rgb.shape,cat_fea.shape)
        attention_vector_l = self.gate_rgb(cat_fea)
        attention_vector_r = self.gate_hha(cat_fea)

        attention_vector = torch.cat([attention_vector_l, attention_vector_r], dim=1)
        attention_vector = self.softmax(attention_vector)
        
        attention_vector_l, attention_vector_r = attention_vector[:, 0:1, :, :,:], attention_vector[:, 1:2, :, :,:]
        # print(rec_rgb.shape,cat_fea.shape,attention_vector.shape,attention_vector_l.shape)
        merge_feature = rgb*attention_vector_l + hha*attention_vector_r
        # merge_feature =  torch.cat([rgb*attention_vector_l, hha*attention_vector_r], dim=1)

        rgb_out = (rgb + merge_feature) / 2
        hha_out = (hha + merge_feature) / 2
        
        
        # rgb_out = self.relu1(rgb_out)
        # hha_out = self.relu2(hha_out)
        merge_feature =  torch.cat([rgb_out, hha*hha_out], dim=1) 

        # return [rgb_out, hha_out], merge_feature
        return merge_feature