# villa inventory database module
> Summary description here.


This file will become your README and also the index of your documentation.

## Install

`pip install villaProductDatabase`

## How to use

in lambda function, simply import and declare in your app.py

```
from villaProductDatabase import database
from awsSchema.apigateway import Response, Event
from s3bz.s3bz import S3
import json
```

```
lambdaDumpToS3 = database.lambdaDumpToS3
lambdaUpdateProduct = database.lambdaUpdateProduct
lambdaUpdateS3 = database.lambdaUpdateS3
lambdaSingleQuery = database.lambdaSingleQuery
lambdaAllQuery = database.lambdaAllQuery
lambdaListQuery = database.lambdaProductsFromList
```

```
# tests
sampleProducts = [{'cprcode': '0171670', 'iprcode': '0171670', 'oprcode': '0171670', 'ordertype': 'Y', 'pr_abb': 'JIRAPAT YOUNG KALE 2', 'pr_active': 'Y', 'pr_cgcode': '05', 'pr_code': '0171670', 'pr_dpcode': '19', 'pr_engname': 'JIRAPAT YOUNG KALE 200 G.', 'pr_ggcode': '057', 'pr_market': 'JIRAPAT ยอดคะน้า 200 G.', 'pr_name': 'JIRAPAT ยอดคะน้า 200 G.', 'pr_puqty': '1', 'pr_sa_method': '1', 'pr_sucode1': 'CM845     ', 'pr_suref3': 'A', 'prtype': 'I', 'psqty': '1', 'pstype': '1'}, {'cprcode': '0235141', 'iprcode': '0235141', 'oprcode': '0235141', 'ordertype': 'Y', 'pr_abb': 'EEBOO-PZCT3-PUZZLE', 'pr_active': 'Y', 'pr_cgcode': '08', 'pr_code': '0235141', 'pr_dpcode': '19', 'pr_engname': 'EEBOO,ANIMAL COUNTING PUZZLE_3ED,PZCT3', 'pr_ggcode': '113', 'pr_market': 'eeboo,PUZZLE-PZCT3', 'pr_name': 'EEBOO-PZCT3-ตัวต่อนับเลข ANIMAL COUNTING_3ED', 'pr_puqty': '1', 'pr_sa_method': '1', 'pr_sucode1': 'CM1979    ', 'pr_suref3': 'A', 'prtype': 'I', 'psqty': '1', 'pstype': '1'}, {'cprcode': '0217153', 'iprcode': '0217153', 'oprcode': '0217153', 'ordertype': 'Y', 'pr_abb': 'COCOA LOCO MILK CHOC', 'pr_active': 'Y', 'pr_cgcode': '98', 'pr_code': '0217153', 'pr_dpcode': '28', 'pr_engname': 'COCOA LOCO MILK CHOCOLATE OWL LOLLY 26G.', 'pr_ggcode': '003', 'pr_market': 'COCOA LOCO MILK CHOCOLATE OWL', 'pr_name': 'COCOA LOCO MILK CHOCOLATE OWL LOLLY 26G.', 'pr_puqty': '24', 'pr_sa_method': '1', 'pr_sucode1': 'F1222     ', 'pr_suref3': 'S', 'prtype': 'I', 'psqty': '1', 'pstype': '1'}, {'cprcode': '0182223', 'iprcode': '0182223', 'oprcode': '0182223', 'ordertype': 'Y', 'pr_abb': 'CIRIO PIZZASSIMO 400', 'pr_active': 'Y', 'pr_cgcode': '06', 'pr_code': '0182223', 'pr_dpcode': '06', 'pr_engname': 'CIRIO PIZZASSIMO 400G.', 'pr_ggcode': '004', 'pr_market': 'CIRIO ซอสทำพิซซ่า 400 G.', 'pr_name': 'CIRIO ซอสทำพิซซ่า 400 G.', 'pr_puqty': '12', 'pr_sa_method': '1', 'pr_sucode1': '2589      ', 'pr_suref3': 'C', 'prtype': 'I', 'psqty': '1', 'pstype': '1'}, {'cprcode': '0124461', 'iprcode': '0124461', 'oprcode': '0124461', 'ordertype': 'Y', 'pr_abb': 'NEW CHOICE LYCHEE', 'pr_active': 'Y', 'pr_cgcode': '02', 'pr_code': '0124461', 'pr_dpcode': '02', 'pr_engname': 'NEW CHOICE LYCHEE', 'pr_ggcode': '003', 'pr_market': 'NEW CHOICE กลิ่นลิ้นจี่', 'pr_name': 'NEW CHOICE กลิ่นลิ้นจี่', 'pr_puqty': '12', 'pr_sa_method': '1', 'pr_sucode1': '695       ', 'pr_suref3': 'A', 'prtype': 'I', 'psqty': '1', 'pstype': '1'}]
```

## dump to s3

```
# test dump to s3
result = Response.fromDict(lambdaDumpToS3('','')).body['result']
print(result)
```

    saved 5 products


## update standard

```
# test saving products
event = {'body': json.dumps({ 'products': sampleProducts })}
result = Response.fromDict(lambdaUpdateProduct(event ,'')).body
print(result)
```

    {'success': 0, 'failure': 0, 'skipped': 5, 'failureMessage': [], 'timetaken': 191.805}


## update s3

```
# test saving using s3
inputKeyName = 'input-data-name'
saveResult = S3.save(key=inputKeyName, 
                     objectToSave = sampleProducts , 
                     bucket = os.environ['INPUT_BUCKET_NAME'],
                     user = os.environ['USER'],
                     pw = os.environ['PW'],
                     accelerate = True)
event = {'body': json.dumps({'key': inputKeyName})}
lambdaUpdateS3(event, '')
```




    {'body': '{"success": 0, "failure": 0, "skipped": 5, "failureMessage": [], "timetaken": 187.84}',
     'statusCode': 200,
     'header': {}}



## single query

```
sampleQueryInput = { 'iprcode': '0171670' } 
event = Event(body = json.dumps(sampleQueryInput)).to_dict()
lambdaSingleQuery(event,'')
```




    {'body': '{"cprcode": "0171670", "iprcode": "0171670", "oprcode": "0171670", "ordertype": "Y", "pr_abb": "JIRAPAT YOUNG KALE 2", "pr_active": "Y", "pr_cgcode": "05", "pr_code": "0171670", "pr_dpcode": "19", "pr_engname": "JIRAPAT YOUNG KALE 200 G.", "pr_ggcode": "057", "pr_market": "JIRAPAT \\u0e22\\u0e2d\\u0e14\\u0e04\\u0e30\\u0e19\\u0e49\\u0e32 200 G.", "pr_name": "JIRAPAT \\u0e22\\u0e2d\\u0e14\\u0e04\\u0e30\\u0e19\\u0e49\\u0e32 200 G.", "pr_puqty": "1", "pr_sa_method": "1", "pr_sucode1": "CM845", "pr_suref3": "A", "prtype": "I", "psqty": "1", "pstype": "1"}',
     'statusCode': 200,
     'header': {}}



## All Query

```
from s3bz.s3bz import Requests

url = Response.fromDict(lambdaAllQuery('', '')).body['url']
result = Requests.getContentFromUrl(url)
print(f'received {len(list(result.keys()))} results, the first one is {next(iter(result.items()))}')
```

    received 5 results, the first one is ('0217153', {'0217153': {'cprcode': '0217153', 'iprcode': '0217153', 'oprcode': '0217153', 'ordertype': 'Y', 'pr_abb': 'COCOA LOCO MILK CHOC', 'pr_active': 'Y', 'pr_cgcode': '98', 'pr_code': '0217153', 'pr_dpcode': '28', 'pr_engname': 'COCOA LOCO MILK CHOCOLATE OWL LOLLY 26G.', 'pr_ggcode': '003', 'pr_market': 'COCOA LOCO MILK CHOCOLATE OWL', 'pr_name': 'COCOA LOCO MILK CHOCOLATE OWL LOLLY 26G.', 'pr_puqty': '24', 'pr_sa_method': '1', 'pr_sucode1': 'F1222', 'pr_suref3': 'S', 'prtype': 'I', 'psqty': '1', 'pstype': '1'}})

