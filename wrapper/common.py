#!/usr/bin/env python

'''
A simple Python wrapper for the bh_tsne binary that makes it easier to use it
for TSV files in a pipeline without any shell script trickery.

Note: The script does some minimal sanity checking of the input, but don't
    expect it to cover all cases. After all, it is a just a wrapper.

Example:

    > echo -e '1.0\t0.0\n0.0\t1.0' | ./bhtsne.py -d 2 -p 0.1
    -2458.83181442  -6525.87718385
    2458.83181442   6525.87718385

The output will not be normalised, maybe the below one-liner is of interest?:

    python -c 'import numpy;  from sys import stdin, stdout;
        d = numpy.loadtxt(stdin); d -= d.min(axis=0); d /= d.max(axis=0);
        numpy.savetxt(stdout, d, fmt="%.8f", delimiter="\t")'

Authors:     Pontus Stenetorp    <pontus stenetorp se>
             Philippe Remy       <github: philipperemy>
Version:    2016-03-08
'''

# Copyright (c) 2013, Pontus Stenetorp <pontus stenetorp se>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from argparse import ArgumentParser, FileType
from os.path import abspath, dirname, isfile, join as path_join
from shutil import rmtree
from struct import calcsize, pack, unpack
from subprocess import Popen
from sys import stderr, stdin, stdout
from tempfile import mkdtemp
from platform import system
from os import devnull
import numpy as np
import os, sys
import io

# Default hyper-parameter values from van der Maaten (2014)
# https://lvdmaaten.github.io/publications/papers/JMLR_2014.pdf (Experimental Setup, page 13)
DEFAULT_NO_DIMS = 2
INITIAL_DIMENSIONS = 50
DEFAULT_PERPLEXITY = 50
DEFAULT_THETA = 0.5
EMPTY_SEED = -1
DEFAULT_USE_PCA = True
DEFAULT_MAX_ITERATIONS = 1000

###

def argparse():
    argparse = ArgumentParser('bh_tsne Python wrapper')
    argparse.add_argument('-d', '--no_dims', type=int,
                          default=DEFAULT_NO_DIMS)
    argparse.add_argument('-p', '--perplexity', type=float,
            default=DEFAULT_PERPLEXITY)
    # 0.0 for theta is equivalent to vanilla t-SNE
    argparse.add_argument('-t', '--theta', type=float, default=DEFAULT_THETA)
    argparse.add_argument('-r', '--randseed', type=int, default=EMPTY_SEED)
    argparse.add_argument('-n', '--initial_dims', type=int, default=INITIAL_DIMENSIONS)
    argparse.add_argument('-v', '--verbose', action='store_true')
    argparse.add_argument('-i', '--input', type=FileType('r'), default=stdin)
    argparse.add_argument('-o', '--output', type=FileType('w'),
            default=stdout)
    argparse.add_argument('--use_pca', action='store_true')
    argparse.add_argument('--no_pca', dest='use_pca', action='store_false')
    argparse.set_defaults(use_pca=DEFAULT_USE_PCA)
    argparse.add_argument('-m', '--max_iter', type=int, default=DEFAULT_MAX_ITERATIONS)
    return argparse


def _read_unpack(fmt, fh):
    return unpack(fmt, fh.read(calcsize(fmt)))


def _is_filelike_object(f):
    try:
        return isinstance(f, (file, io.IOBase))
    except NameError:
        # 'file' is not a class in python3
        return isinstance(f, io.IOBase)


def init_bh_tsne(samples, workdir, no_dims=DEFAULT_NO_DIMS, initial_dims=INITIAL_DIMENSIONS, perplexity=DEFAULT_PERPLEXITY,
            theta=DEFAULT_THETA, randseed=EMPTY_SEED, verbose=False, use_pca=DEFAULT_USE_PCA, max_iter=DEFAULT_MAX_ITERATIONS):

    if use_pca:
        samples = samples - np.mean(samples, axis=0)
        cov_x = np.dot(np.transpose(samples), samples)
        [eig_val, eig_vec] = np.linalg.eig(cov_x)

        # sorting the eigen-values in the descending order
        eig_vec = eig_vec[:, eig_val.argsort()[::-1]]

        if initial_dims > len(eig_vec):
            initial_dims = len(eig_vec)

        # truncating the eigen-vectors matrix to keep the most important vectors
        eig_vec = np.real(eig_vec[:, :initial_dims])
        samples = np.dot(samples, eig_vec)

    # Assume that the dimensionality of the first sample is representative for
    #   the whole batch
    sample_dim = len(samples[0])
    sample_count = len(samples)

    # Note: The binary format used by bh_tsne is roughly the same as for
    #   vanilla tsne
    with open(path_join(workdir, 'data.dat'), 'wb') as data_file:
        # Write the bh_tsne header
        data_file.write(pack('iiddii', sample_count, sample_dim, theta, perplexity, no_dims, max_iter))
        # Then write the data
        for sample in samples:
            data_file.write(pack('{}d'.format(len(sample)), *sample))
        # Write random seed if specified
        if randseed != EMPTY_SEED:
            data_file.write(pack('i', randseed))

def load_data(input_file):
    # Read the data, using numpy's good judgement
    return np.loadtxt(input_file)


