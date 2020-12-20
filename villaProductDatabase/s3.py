# AUTOGENERATED! DO NOT EDIT! File to edit: S3.ipynb (unless otherwise specified).

__all__ = ['DBHASHLOCATION', 'DBCACHELOCATION', 'DATABASE_TABLE_NAME', 'INVENTORY_BUCKET_NAME', 'INPUT_BUCKET_NAME',
           'REGION', 'ACCESS_KEY_ID', 'SECRET_ACCESS_KEY', 'LINEKEY', 'S3Cache', 'saveHash', 'loadHash', 'loadFromS3',
           'saveAllS3']

# Cell
from s3bz.s3bz import S3
from nicHelper.wrappers import add_method, add_class_method, add_static_method
from nicHelper.dictUtil import stripDict, printDict, hashDict, saveStringToFile, loadStringFromFile, saveDictToFile, loadDictFromFile
from nicHelper.exception import errorString
from dict_hash import dict_hash, sha256
from base64 import b64encode, b64decode
import os, logging

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

try:
  DAX_ENDPOINT = os.environ['DAX_ENDPOINT']
  print(DAX_ENDPOINT)
except KeyError as e:
  print(f'dax endpoint missing {e}')


# Cell
class S3Cache:
  pass

# Cell
@add_class_method(S3Cache)
def saveHash(cls , data:dict, key='allData', bucket=INVENTORY_BUCKET_NAME,
             cachePath=DBCACHELOCATION, hashPath = DBHASHLOCATION):
  hashKey = f'{key}-hash'
  hashString = hashDict(data)
  dictToSave= {'hash': hashString }
  print(f'hashKey is {hashKey}')
  print(f'saving cache file')
  saveDictToFile(data, path = cachePath)
  print(f'saving hash file')
  saveStringToFile(hashString, path=hashPath)
  print('saving hash to s3')
  S3.save(key=hashKey,objectToSave=dictToSave, bucket=bucket)
  print(f'saved hash {hashString}')
@add_class_method(S3Cache)
def loadHash(cls,key='allData', bucket=INVENTORY_BUCKET_NAME):
  hashKey = f'{key}-hash'
  print(f'loading hashkey {hashKey}')
  loadedHash= S3.load(hashKey,bucket=bucket).get('hash')
  print(f'loaded hash is{loadedHash}')
  return loadedHash

# Cell
@add_class_method(S3Cache)
def loadFromS3(cls, bucketName= INVENTORY_BUCKET_NAME, key = 'allData',
               hashPath=DBHASHLOCATION, cachePath = DBCACHELOCATION,**kwargs):
  '''
  this is not a real time function, there may be a delay of sync between
  the main dynamodb database and the cache
  '''

  if os.path.exists(hashPath) and os.path.exists(cachePath):
    print('cache exist')
    if cls.loadHash(key=key) == loadStringFromFile(hashPath):
      db = loadDictFromFile(cachePath)
      print('found a valid cache, using cache')
      return db
    else:
      print('cache has different hash than s3')
  print('cache doesnt exist')
  logging.info(f'loading from {bucketName}')
  logging.info(f'user is {kwargs.get("user")}')
  database =  S3.loadPklZl(key=f'{key}-pklzl', bucket = bucketName,  **kwargs)
#   database =  S3.load(key=f'{key}', bucket = bucketName,  **kwargs)
  print(database)
  cls.saveHash(database)
  return database

# Cell
@add_class_method(S3Cache)
def saveAllS3(cls, objectToSave:dict, bucketName= INVENTORY_BUCKET_NAME, key = 'allData',
              hashPath = DBHASHLOCATION, cachePath = DBCACHELOCATION, **kwargs):
  if os.path.exists(cachePath) and os.path.exists(hashPath):
    if loadStringFromFile(hashPath) == cls.loadHash(key=key, bucket=bucketName):
      print('the object did not change, skip saving')
      return
  S3.save(key=key, bucket=bucketName, objectToSave=objectToSave)
  S3.savePklZl(key=f'{key}-pklzl',bucket=bucketName, objectToSave=objectToSave)
  S3.saveZl(key=f'{key}-zl',bucket=bucketName, objectToSave=objectToSave)
  print(f'saving hash with key {key}')
  cls.saveHash(objectToSave, key=key)
