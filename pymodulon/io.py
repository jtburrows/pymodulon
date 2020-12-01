import gzip
import json
from typing import Union, TextIO

import pandas as pd

from pymodulon.core import IcaData

"""
Functions for reading and writing model into files.
"""


def save_to_json(model: IcaData, fname: str, compress: bool = False):
    """

    Save model to the json file
    Parameters
    ----------
    model: IcaData
       ICA model to be saved to json file
    fname: string
       path to json file where the model will be saved
    compress: bool
        indicates if the JSON file should be compressed into a gzip archive
    """

    if model.A is None or model.M is None:
        raise ValueError('The model must include the M and the A matrix.')

    # only keeps params that are used to initialize the model
    load_params = IcaData.__init__.__code__.co_varnames
    param_dict = {key: getattr(model, key) for key in vars(IcaData) if key in
                  load_params}

    # serialize pandas DataFrames and change sets to lists
    for key, val in param_dict.items():
        if isinstance(val, pd.DataFrame) or isinstance(val, pd.Series):
            param_dict.update({key: val.to_json()})
        elif isinstance(val, set):
            param_dict.update({key: list(val)})

    if not fname.endswith('.json'):
        fname += '.json'

    if compress:
        fname += '.gz'
        with gzip.open(fname, 'wt', encoding="ascii") as zipfile:
            json.dump(param_dict, zipfile)
    else:
        with open(fname, 'w') as fp:
            json.dump(param_dict, fp)


def load_json_model(filename: Union[str, TextIO]) -> IcaData:
    """
    Load a ICA model from a file in JSON format.
    Parameters
    ----------
    filename : str or file-like
        File path or descriptor that contains the JSON document describing the
        ICA model.
    Returns
    -------
    IcaData
        The ICA model as represented in the JSON document.

    """
    if isinstance(filename, str):
        if filename.endswith('.gz'):
            with gzip.GzipFile(filename, 'r') as zipfile:
                serial_data = json.loads(zipfile.read().decode('utf-8'))
        else:
            with open(filename, "r") as file_handle:
                serial_data = json.load(file_handle)
    else:
        serial_data = json.load(filename)
        
    return IcaData(**serial_data)
