# AUTOGENERATED! DO NOT EDIT! File to edit: query.ipynb (unless otherwise specified).

__all__ = ['Querier']

# Cell
import pandas as pd
from datetime import datetime
from s3bz.s3bz import S3
import pickle, json , boto3, zlib, os

# Cell
try:
  INVENTORY_BUCKET_NAME = os.environ['INVENTORY_BUCKET_NAME']
except Exception as e:
  print(f'missing environment variable {e} in query NB')
  INVENTORY_BUCKET_NAME = None

# Cell
class Querier:
  @classmethod
  def singleProductQuery(cls, input):
    if not cls.validateInputQuery(['ib_prcode'] , input): return f"error input {input}"
    return next(cls.query(input.get('ib_prcode')),{})

  @classmethod
  def branchQuery(cls, branchId:str, bucket = INVENTORY_BUCKET_NAME, **kwargs):
    key = branchId
    result = S3.presign(key, bucket = bucket, **kwargs)
    return result
  @classmethod
  def allQuery(cls, key = 'allData', bucket = INVENTORY_BUCKET_NAME, **kwargs):
    result = S3.presign(key, bucket = bucket, **kwargs)
    return result

  @staticmethod
  def validateInputQuery(keys: list, input:dict):
    '''
      check if input query contains the valid key
      data should have the following structure
      key is a list of keys to check

      ib_prcode: String?
      ib_brcode: String?

      option, one of or both of the ib_procde must be present
    '''
    for key in keys:
      if key not in input.keys():
        raise ValueError(f"key {key} is missing from the input")
      if not input.get(key).isdigit():
        raise ValueError(f'key is not convertable to in {input.get(key)}')
    return True