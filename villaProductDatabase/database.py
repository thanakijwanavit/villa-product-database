# AUTOGENERATED! DO NOT EDIT! File to edit: database.ipynb (unless otherwise specified).

__all__ = ['createIndex', 'ProductDatabase', 'lambdaDumpToS3', 'lambdaUpdateProduct', 'lambdaUpdateS3',
           'lambdaSingleQuery', 'lambdaAllQuery']

# Cell
from .helper import DatabaseHelper
from .s3 import DatabaseS3
from .query import Querier
from .update import Updater
from .schema import Event, Response
import pandas as pd
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, JSONAttribute, BooleanAttribute, BinaryAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from botocore.config import Config
from s3bz.s3bz import S3
from pprint import pprint

import pickle, json, boto3, bz2, requests, validators, os, logging

# Cell
try:
  DATABASE_TABLE_NAME = os.environ['DATABASE_TABLE_NAME']
  INVENTORY_BUCKET_NAME = os.environ['INVENTORY_BUCKET_NAME']
  INPUT_BUCKET_NAME = os.environ['INPUT_BUCKET_NAME']
  REGION = os.environ['REGION']
  ACCESS_KEY_ID = os.environ.get('USER')
  SECRET_ACCESS_KEY = os.environ.get('PW')
except Exception as e:
  print(f'error, missing environment variables \n{e}')
  ACCESS_KEY_ID = None
  SECRET_ACCESS_KEY = None
  DATABASE_TABLE_NAME = None
  INVENTORY_BUCKET_NAME = None
  INPUT_BUCKET_NAME = None
  REGION = 'ap-southeast-1'
try:
  DAX_ENDPOINT = os.environ['DAX_ENDPOINT']
except KeyError as e:
  DAX_ENDPOINT = None
  print(f'dax endpoint missing {e}')


# Cell
def createIndex(name, rangeKeyName= None, HashKeyType = UnicodeAttribute, RangeKeyType = UnicodeAttribute):
  class ReturnSecondaryIndex(GlobalSecondaryIndex):
    class Meta:
      index_name = name
      projection = AllProjection()
      read_capacity_units = 1
      write_capacity_units = 1
  setattr(ReturnSecondaryIndex, name, HashKeyType(hash_key = True))
  if rangeKeyName:
    setattr(ReturnSecondaryIndex, rangeKeyName, RangeKeyType(range_key = True))
  return ReturnSecondaryIndex()

# Cell
# dont forget to import dependent classes from the relevant notebooks
class ProductDatabase(Model, DatabaseS3, Updater, Querier, DatabaseHelper):
  class Meta:
    aws_access_key_id = ACCESS_KEY_ID
    aws_secret_access_key = SECRET_ACCESS_KEY
    table_name = DATABASE_TABLE_NAME
    region = REGION
    billing_mode='PAY_PER_REQUEST'
    dax_read_endpoints = DAX_ENDPOINT
    dax_write_endpoints = DAX_ENDPOINT

  iprcode = UnicodeAttribute(hash_key=True, default = '')
  cprcode = UnicodeAttribute(default = 'none', range_key = True)
  oprcode = UnicodeAttribute(default = 'none')
  pr_dpcode = UnicodeAttribute(default = 'none')
  pr_barcode = UnicodeAttribute(default = 'none')
  pr_barcode2 = UnicodeAttribute(default = 'none')
  pr_sucode1 = UnicodeAttribute(default = 'none')
  pr_suref3 = UnicodeAttribute(default= 'none')
  pr_sa_method = UnicodeAttribute(default= 'none')
  sellingPrice = NumberAttribute(default = 0)
  lastUpdate = NumberAttribute( default = 0)
  needsUpdate = UnicodeAttribute(default = 'Y')
  data = JSONAttribute()

  # indexes
  needsUpdateIndex = createIndex('needsUpdate','sellingPrice')
  cprcodeIndex = createIndex('cprcode', 'sellingPrice')
  oprcodeIndex = createIndex('oprcode', 'sellingPrice')
  pr_dpcodeIndex = createIndex('pr_dpcode', 'sellingPrice')
  pr_barcodeIndex = createIndex('pr_barcode', 'sellingPrice')
  pr_barcode2Index = createIndex('pr_barcode2', 'sellingPrice')
  pr_suref3Index = createIndex('pr_suref3', 'sellingPrice')
  pr_sa_methodIndex = createIndex('pr_sa_method', 'sellingPrice')


  TRUE = 'Y'
  FALSE = 'N'


  def __repr__(self):
    return self.returnKW(self.data)

  def setNoUpdate(self, batch = None):
    self.needsUpdate = self.FALSE
    if batch:
      return batch.save(self)
    else:
      return self.save()
  def setUpdate(self):
    self.needsUpdate = self.TRUE
    return self.save()

  @staticmethod
  def returnKW(inputDict):
    outputStr = 'ProductDatabase Object\n'
    for k,v in inputDict.items():
      outputStr += f'{k} {v}\n'
    return outputStr

  @classmethod
  def fromDict(cls, dictInput):
    logging.debug(dictInput)
    dictInput = cls.Helper.stripDict(dictInput)
    filteredInput = {k:v for k,v in dictInput.items() if k in dir(cls)}
    filteredInput['data'] = dictInput
    logging.debug(filteredInput)
    return cls(**filteredInput)


# Cell
def lambdaDumpToS3(event, _):
  result = ProductDatabase.dumpToS3(user=ACCESS_KEY_ID, pw = SECRET_ACCESS_KEY)
  return Response.getReturn(body = {'result': result})

# Cell
def lambdaUpdateProduct (event, _):
  products = Event.from_dict(event).getProducts().to_dict()['products']
  result = ProductDatabase.updateLambdaInput(products)
  return Response.getReturn(body = result)

# Cell
def lambdaUpdateS3(event, _):
  inputKeyName = Event.from_dict(event).key()
  updateResult = ProductDatabase.updateS3Input(
    inputBucketName=INPUT_BUCKET_NAME, key= inputKeyName,
    user = ACCESS_KEY_ID, pw = SECRET_ACCESS_KEY)
  return Response.getReturn(body = updateResult)

# Cell
def lambdaSingleQuery(event, _):
  key, value = Event.from_dict(event).firstKey()
  result = ProductDatabase.singleProductQuery({key:value}).data
  return Response.getReturn(body = result)

# Cell
def lambdaAllQuery(event, _):
  url = ProductDatabase.allQuery(bucket = INVENTORY_BUCKET_NAME, user=ACCESS_KEY_ID, pw=SECRET_ACCESS_KEY)
  return Response.getReturn(body = {'url': url})