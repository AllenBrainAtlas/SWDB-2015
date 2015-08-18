"""
Functions for dealing with linear model.
"""
from __future__ import print_function, division
import numpy as np


def convert_to_bilateral(matrix_ipsi, matrix_contra):
    """
    Create a "bilateral" matrix from ipsi and contra matrices.
    :param matrix_ipsi: Matrix of projections to ipsilateral side of brain.
    :param matrix_contra: Matrix of projections to contralateral side of brain.
    :return: Bilateral matrix.
    """

    top = np.concatenate([matrix_ipsi, matrix_contra], axis=1)
    bottom = np.concatenate([matrix_contra, matrix_ipsi], axis=1)

    return np.concatenate([top, bottom], axis=0)
