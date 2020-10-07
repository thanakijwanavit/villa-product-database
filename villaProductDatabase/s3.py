# AUTOGENERATED! DO NOT EDIT! File to edit: s3.ipynb (unless otherwise specified).

__all__ = ['DatabaseS3']

# Cell
import os, logging
from s3bz.s3bz import S3

# Cell
try:
  INVENTORY_BUCKET_NAME = os.environ['INVENTORY_BUCKET_NAME']
except Exception as e:
  print(f'missing environment variable {e} in Database s3 NB')
  INVENTORY_BUCKET_NAME = None

# Cell
class DatabaseS3:
  @classmethod
  def loadFromS3(cls, bucketName= INVENTORY_BUCKET_NAME, key = 'allData', **kwargs):
    logging.info(f'loading from {bucketName}')
    logging.info(f'user is {kwargs.get("user")}')
    return S3.load(key=key, bucket = bucketName,  **kwargs)

  @classmethod
  def dumpToS3(cls, bucketName= INVENTORY_BUCKET_NAME, key = 'allData', **kwargs):
    ''' upload changes to s3'''
    allData = cls.loadFromS3(bucketName = bucketName, key = key, **kwargs)
    originalData = allData.copy()

    logging.debug(f'all data is {len(allData)}')
    changeList = list(cls.needsUpdateIndex.query(cls.TRUE))
    logging.debug(f'{len(changeList)} changes to update')

    with cls.batch_write() as batch:
      for dbObject in changeList:
        item = dbObject.data
        # if product doesnt exist, create an empty dict
        if not allData.get(item['iprcode']): allData[item['iprcode']] = {}
        # if cprcode doesnt exist, create an empty dict
        if not allData.get(item['iprcode']).get(item['cprcode']): allData[item['iprcode']][item['cprcode']] = {}
        # update product
        allData[item['iprcode']][item['cprcode']].update(item)
        # set no change to all data after update
        dbObject.setNoUpdate(batch=batch)

    if allData != originalData:
      logging.debug(f'updating')
      logging.debug(S3.save(key = 'allData',
                  objectToSave = allData,
                  bucket = bucketName, **kwargs)
      )
    else:
      logging.debug('no changes to update')

    logging.info(f'alldata is {next(iter(allData.items()))}')
    return f"saved {len(list(allData.keys()))} products"
