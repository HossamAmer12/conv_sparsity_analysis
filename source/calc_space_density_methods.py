# This file should contain all equations for calculating the space

# Force floating point division
from __future__ import division
import math

# Import conv layer
from conv_layer import Conv_Layer
from myconstants import conv_methods
import numpy as np

# Calculates the required memory units for the **CPO** method
def getSpaceCPO(layer):
    # Used to caluclate the Compression Ratio
    # we should multiply by Ic here, create seperate functions for this
    if (layer.Kw%layer.Sw) == 0:
        space = layer.In*(layer.Kw/layer.Sw)*(layer.Ow+1)+2*(layer.Ih_padded*layer.Iw_padded*sum(layer.ru_batch)*layer.Ic) 
    elif (layer.Kw%layer.Sw) != 0:
        space = math.ceil(layer.Kw/layer.Sw)*(layer.Ow+1)+2*(layer.Ih_padded*layer.Iw_padded*sum(layer.ru_batch)*layer.Ic)
    return space

def getSpaceCPS(layer):
    # use the assumption of Ic = 1 && In = 1
    if (layer.Kw%layer.Sw) == 0:
        space = layer.In*(layer.Kw/layer.Sw)*(layer.Ow+1)\
                +(layer.Ih_padded*layer.Iw_padded*layer.Ic*sum(layer.ru_batch)) \
                + (layer.patterns_sum)
    elif (layer.Kw%layer.Sw) != 0:
        space = layer.In*math.ceil(layer.Kw/layer.Sw)*(layer.Ow+1)\
                + (layer.Ih_padded*layer.Iw_padded*layer.Ic*sum(layer.ru_batch))\
                + (layer.patterns_sum)
    return space

# Calculates the required memory units for the **MEC**  method
def getSpaceMEC(layer):
    space = layer.Ow*layer.Kw*layer.Ih_padded*layer.In*layer.Ic
    return space

# Calculates the required memory units for the **CSCC** method
def getSpaceCSCC(layer): 
    space = layer.In*(layer.Ow + 1) + ( 2*(layer.Ow * layer.Kw * layer.Ih_padded * layer.Ic * sum(layer.lowering_den_batch)))
    return space

# Calculates the required memory units for the **Im2Col** method
def getSpaceIm2Col(layer):
    space = layer.In*layer.Ow*layer.Oh*layer.Ic*layer.Kw*layer.Kh
    return space

# Calculates the required memory units for the **SparseTensor** method
def getSpaceSparseTensor(layer):
    space = 3*layer.tot_nz_feature
    return space

# Calculates the required density bound for MEC vs CPO
def getDensityBoundMEC(layer):
    if not layer.Kw % layer.Sw:
        density_bound_mec = ((layer.In*layer.Ic*layer.Ow*layer.Kw*layer.Ih_padded) - ((layer.In*layer.Ow*layer.Kw)/layer.Sw )
                            - (layer.In*layer.Kw/layer.Sw))
    else:
        density_bound_mec = ((layer.In*layer.Ic*layer.Ow*layer.Kw*layer.Ih_padded) - ((layer.In*layer.Ow)*math.ceil(layer.Kw/layer.Sw) ) \
                - ((layer.In)*math.ceil(layer.Kw/layer.Sw) ))
    
    density_bound_mec = density_bound_mec / (2*layer.Ih_padded*layer.Iw_padded*layer.Ic)
    return density_bound_mec

# Calculates the required density bound for CSCC vs CPO
def getDensityBoundCSCC(layer):

    if not layer.Kw % layer.Sw:
        density_bound_cscc = layer.Kw*layer.Ow*sum(layer.lowering_den_batch) + layer.In*(layer.Ow+1)/(2*layer.Ih_padded*layer.Ic) \
                - layer.In*layer.Kw*(layer.Ow+1)/(2*layer.Ic*layer.Ih_padded*layer.Sw)
    else:
        density_bound_cscc = layer.Kw*layer.Ow*sum(layer.lowering_den_batch) + layer.In*(layer.Ow+1)/(2*layer.Ih_padded*layer.Ic) \
                - math.ceil(layer.Kw/layer.Sw)*layer.In*(layer.Ow+1)/(2*layer.Ic*layer.Ih_padded)

    density_bound_cscc = density_bound_cscc/layer.Iw_padded
    return density_bound_cscc


def getCR(layer, method_type, Im2col_space = 1):
    if (method_type == conv_methods['CPO']):
        layer.CPO_cmpRatio          = Im2col_space/getSpaceCPO(layer)
    elif (method_type == conv_methods['CPS']):
        layer.CPS_cmpRatio          = Im2col_space/getSpaceCPS(layer)
    elif (method_type == conv_methods['MEC']):
        layer.MEC_cmpRatio          = Im2col_space/getSpaceMEC(layer)
    elif (method_type == conv_methods['CSCC']):
        layer.CSCC_cmpRatio         = Im2col_space/getSpaceCSCC(layer)
    elif (method_type == conv_methods['SparseTensor']):
        layer.SparseTen_cmpRatio    = Im2col_space/getSpaceSparseTensor(layer)
    elif (method_type == conv_methods['Im2Col']):
        return getSpaceIm2Col(layer)

def getDensityBound(layer, method_type):
    if (method_type == conv_methods['MEC']):
        layer.density_bound_mec = getDensityBoundMEC(layer)
    elif (method_type == conv_methods['CSCC']):
        layer.density_bound_cscc = getDensityBoundCSCC(layer)
