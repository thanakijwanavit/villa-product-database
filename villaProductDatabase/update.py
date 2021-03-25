# AUTOGENERATED! DO NOT EDIT! File to edit: Update.ipynb (unless otherwise specified).

__all__ = ['DBHASHLOCATION', 'DBCACHELOCATION', 'DATABASE_TABLE_NAME', 'INVENTORY_BUCKET_NAME', 'INPUT_BUCKET_NAME',
           'REGION', 'ACCESS_KEY_ID', 'SECRET_ACCESS_KEY', 'LINEKEY', 'BRANCH', 'VALUEUPDATESCHEMAURL', 'Updater',
           'updateWithDict', 'ValueUpdate2', 'saveBatchToDynamodb', 'saveBatchToDynamodb2', 'valueUpdate2']

# Cell
from s3bz.s3bz import S3
from nicHelper.wrappers import add_method, add_class_method, add_static_method
from nicHelper.dictUtil import stripDict, printDict, hashDict, saveStringToFile, loadStringFromFile, saveDictToFile, loadDictFromFile
from nicHelper.exception import errorString
from dict_hash import dict_hash, sha256
from base64 import b64encode, b64decode
from dataclasses_json import dataclass_json, Undefined, CatchAll
from dataclasses_jsonschema import JsonSchemaMixin
from dataclasses import dataclass
from jsonschema import validate
from typing import List
from datetime import datetime
from nicHelper.schema import validateUrl
import pandas as pd
import os, logging, json

# Cell
import os
DBHASHLOCATION = '/tmp/database.hash'
DBCACHELOCATION = '/tmp/database.cache'
DATABASE_TABLE_NAME = os.environ.get('DATABASE_TABLE_NAME')
INVENTORY_BUCKET_NAME = os.environ.get('INVENTORY_BUCKET_NAME')
INPUT_BUCKET_NAME = os.environ.get('INPUT_BUCKET_NAME')
REGION = os.environ.get('REGION') or 'ap-southeast-1'
ACCESS_KEY_ID = os.environ.get('USER') or None
SECRET_ACCESS_KEY = os.environ.get('PW') or None
LINEKEY= os.environ.get('LINEKEY')
BRANCH = os.environ.get('BRANCH')
VALUEUPDATESCHEMAURL = f'https://raw.githubusercontent.com/thanakijwanavit/villaMasterSchema/{BRANCH}/product/product.yaml'

try:
  DAX_ENDPOINT = os.environ['DAX_ENDPOINT']
  print(DAX_ENDPOINT)
except KeyError as e:
  print(f'dax endpoint missing {e}')

# Cell
class Updater:
  pass

# Cell
@add_class_method(Updater)
def updateWithDict(cls, originalObject:Updater, inputDict:dict ):
  data = originalObject.data
  data.update(inputDict)
  return cls.fromDict(data)

# Cell
class ValueUpdate2:
   #### divide work into chunks
  @staticmethod
  def chunks(l, n): return [l[x: x+n] for x in range(0, len(l), n)]
  ##### plot time elapsed for debugging
  @staticmethod
  def getTimeElasped(t0): return (datetime.now()-t0).total_seconds() * 1000

  t0 = datetime.now()

  ### validate input
  @staticmethod
  def validateInput(input_):
    return validateUrl(VALUEUPDATESCHEMAURL,
                       input_, format_='yaml')

# Cell
@add_static_method(ValueUpdate2)
def saveBatchToDynamodb(productBatch:list, dbClass:Updater, db:pd.DataFrame, itemsUpdated:dict):
  def checkIfInDb(db:pd.DataFrame, iprcode:int, cprcode:int)->dbClass:
    '''check if product is in the database, if not, create an empty class with the product code'''
    if 'cprcode' in db.columns:
      incumbentDb = db[db['cprcode']==cprcode] ## filter for the cprcode
      if incumbentDb.empty:
        incumbentSeries = pd.Series() ## if empty, create an empty series
      else:
        incumbentSeries = incumbentDb.iloc[0] ## if not empty, pull the series

      #### create object from series or new object if series is empty ####
      if incumbentSeries.any:  incumbentItem = dbClass.fromSeries(incumbentSeries)
      else: incumbentItem = dbClass.fromDict({'iprcode': iprcode, 'cprcode': cprcode})

    #### if cprcode doesnt exist, create empty object ####
    else: incumbentItem = dbClass.fromDict({'iprcode': iprcode, 'cprcode': cprcode})
    return incumbentItem

  ###### main ######
  with dbClass.batch_write() as batch:
    # loop through each product
    for product in productBatch:
      iprcode = product['iprcode']
      cprcode = product['cprcode']
      incumbentItem = checkIfInDb(db, iprcode, cprcode) ### check if product in db or return empty obj

      ##### make a copy of original data
      originalData = incumbentItem.data.copy()
      ###### update data
      updatedData = dbClass.updateWithDict(incumbentItem, product)

      logging.info(f'incumbentBr is {incumbentItem.iprcode}\n, prcode is {iprcode}')

      # check for difference
      try:
        if updatedData.data != originalData:
          logging.info(f'product {iprcode} has changed from \n{originalData} \n{updatedData.data}')
          batch.save(updatedData)
          itemsUpdated['success'] += 1
        else:
          logging.info(f'no change for {iprcode}')
          itemsUpdated['skipped'] += 1
      except Exception as e:
        itemsUpdated['failure'] += 1
        itemsUpdated['failureMessage'].append(e)

    # log time taken
#     itemsUpdated['timetaken(ms)'] = (datetime.now()- t0).total_seconds()*1000

# Cell
@add_static_method(ValueUpdate2)
def saveBatchToDynamodb2(productBatch:list, dbClass:Updater, db:pd.DataFrame, itemsUpdated:dict):
  def checkIfInDb(db:pd.DataFrame, iprcode:int, cprcode:int)->dbClass:
    '''check if product is in the database, if not, create an empty class with the product code'''
    incumbentItem =  next(dbClass.query(hash_key = iprcode, range_key_condition=dbClass.cprcode == cprcode), dbClass(iprcode=iprcode, cprcode=cprcode, data = {}))
    return incumbentItem

  ###### main ######
  with dbClass.batch_write() as batch:
    # loop through each product
    for product in productBatch:
      iprcode = product['iprcode']
      cprcode = product['cprcode']
      incumbentItem = checkIfInDb(db, iprcode, cprcode) ### check if product in db or return empty obj

      ##### make a copy of original data
      originalData = incumbentItem.data.copy()
      ###### update data
      updatedData = dbClass.updateWithDict(incumbentItem, product)

      # check for difference
      try:
        if updatedData.data != originalData:
          logging.info(f'product {iprcode} has changed from \n{originalData} \n{updatedData.data}')
          batch.save(updatedData)
          itemsUpdated['success'] += 1
        else:
          logging.info(f'no change for {iprcode}')
          itemsUpdated['skipped'] += 1

      except Exception as e:
        itemsUpdated['failure'] += 1
        itemsUpdated['failureMessage'].append(e)



# Cell
@add_class_method(Updater)
def valueUpdate2(cls, inputs:List[dict]):
    '''
      check for difference and batch update the changes in product data
    '''
    #### setup #####
    itemsUpdated = {'success':0, 'failure': 0, 'skipped': 0 ,'failureMessage':[], 'timetaken(ms)': 0}
    t0 = datetime.now()

    ##### main #####

    ######validate input ###########
    products = ValueUpdate2.validateInput(inputs).items
    print(f'products are {products[0]}')
    print(f'time taken for validation  {ValueUpdate2.getTimeElasped(t0)} ms')

    ######dividing input into batch of 500###########
    productBatches = ValueUpdate2.chunks(products, 500)
    print(f'divided into chunks {ValueUpdate2.getTimeElasped(t0)} ms')

    ######try to load from cache########
    db = cls.loadFromCache().fillna('none')
    print(f'get all from s3 {ValueUpdate2.getTimeElasped(t0)} ms')

    ###### save to dynamodb ########
    for productBatch in productBatches:
      ValueUpdate2.saveBatchToDynamodb2(productBatch, cls, db, itemsUpdated)
    itemsUpdated['timetaken(ms)'] = (datetime.now()- t0).total_seconds()*1000
    return itemsUpdated
