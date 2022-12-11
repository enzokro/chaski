# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/api/complex_inits.ipynb.

# %% auto 0
__all__ = ['get_complex_inits']

# %% ../nbs/api/complex_inits.ipynb 2
'''
Code for blog post:
    https://enzokro.dev/blog/posts/2022-09-01-rayleigh-init/
''' 

import numpy as np
import torch
import torch.nn as nn
from torch.nn.parameter import Parameter
from numpy.random import default_rng

# %% ../nbs/api/complex_inits.ipynb 4
def _calculate_fan_in_and_fan_out_from_shape(shape):
    """Calculates incoming and outgoing connections for weight initializations.
    
    The shape of PyTorch weight tensors is in the format:
        `[nout, nin, *kernels]`
    
    In the case of linear weights we only need the first two dimensions:
        `[nout, nin]`
        
    In the case of n-D convolutional weights, we gain one kernel per dimension.
    For example in a 2D conv layer with a (3, 3) kernel the weight shape becomes:
        `[nout, nin, 3, 3]`
        
    Finally, note how the output features are listed first. This is the reverse of the module API calls:
        `nn.Linear(nin, nout)`
        `nn.Conv2d(nin, nout)`
    Here we follow the module API format, assuming that input features are before output features.
    """
    if len(shape) < 2:
        raise ValueError("Fan in and fan out can not be computed for tensor with fewer than 2 dimensions")
    
    # parse out the number of input and output features
    num_input_fmaps, num_output_fmaps = shape[:2]
    
    # start with a receptive field size of one
    # if this is a linear layer, each neuron only "sees" itself
    receptive_field_size = 1
    
    # here we handle convolutional kernels
    if len(shape) > 2:       
        # the total receptive field is the product of the kernel sizes
        for s in shape[2:]:
            receptive_field_size *= s
            
    # return the number of input/output features scaled by the receptive field 
    fan_in  = num_input_fmaps  * receptive_field_size
    fan_out = num_output_fmaps * receptive_field_size
    return fan_in, fan_out

# %% ../nbs/api/complex_inits.ipynb 5
def get_complex_inits(shape, seed=None, criterion='he', dtype='float32'):
    """Initializes complex-valued Rayleigh weights with the given `shape`.
    """
    # create the random number generator
    rand = default_rng(seed or torch.initial_seed())
    
    # find the number of input and output connections
    fan_in, fan_out = _calculate_fan_in_and_fan_out_from_shape(shape)
    
    # check for a valid criteria
    criterion = str(criterion).lower()
    assert criterion in ('he', 'glorot'), "Criterion must be a string value in [he, glorot]"
    # compute a sigma that meets this variance criteria
    factor = fan_in if criterion == 'he' else (fan_in + fan_out)
    sigma = 1. / np.sqrt(factor)
    
    # draw the scaled Rayleigh magnitudes
    magnitude = rand.rayleigh(scale=sigma, size=shape)
    # draw the random uniform angles
    phase = rand.uniform(low=-np.pi, high=np.pi, size=magnitude.shape)
    
    # split magnitudes into real and imaginary components
    real = (magnitude * np.cos(phase)).astype(dtype)
    imag = (magnitude * np.sin(phase)).astype(dtype)
    
    # return complex weights as learnable float tensors
    real, imag = map(lambda o: Parameter(torch.from_numpy(o)), [real, imag])
    return real, imag