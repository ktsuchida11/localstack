# LocalStack DynamoDB Stream to Lambda

An example .python Lambda consuming a DynamoDB Stream. 

Runs in [LocalStack](https://github.com/localstack/localstack) on Docker.

## Usages.

### Lambda関数のデプロイ

Lambda関数をzipに圧縮

圧縮されたファイルを指定のファイル名に変更する


### Create the Local Infrastructure

Start LocalStack and wait for the provisioning to complete.

```sh
docker-compose up
```

#### 1 Lambda関数を登録

```sh
awslocal lambda create-function \
    --function-name local-function \
    --runtime python3.9 \
    --zip-file fileb:///tmp/function.zip \
    --handler LocalDynamoDbStream::LocalDynamoDbStream.Function::FunctionHandler \
    --role arn:aws:iam::000000000000:role/lambda-role
```

利用可能な状態となっているか確認する

```sh
awslocal lambda get-function \
    --function-name local-function 
```

### 2 DynamoDBテーブルを作成

```sh
awslocal dynamodb create-table \
    --table-name local-table \
    --attribute-definitions AttributeName=Id,AttributeType=S \
    --key-schema AttributeName=Id,KeyType=HASH \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=10
```

LatestStreamArnを取得する

```sh
awslocal dynamodb describe-table \
    --table-name local-table
```

### 3 Lambda関数を登録

```sh
awslocal lambda create-event-source-mapping \
    --function-name local-function \
    --event-source arn:aws:dynamodb:us-east-1:000000000000:table/local-table/stream/2024-02-25T00:29:17.436 \
    --batch-size 1 \
    --starting-position TRIM_HORIZON
```

UUIDを取得してイベントソースマッピングされていることを確認する

```sh
awslocal lambda get-event-source-mapping \
--uuid 9ee893a1-7661-45d2-a1b7-0b96299d64ce
```

### 4 動作確認

関数のログが出力されていないことを確認

```sh
awslocal logs filter-log-events \
    --log-group-name /aws/lambda/local-function
```

DynamoDBテーブルにレコードを追加する

```sh
awslocal dynamodb put-item \
    --table-name local-table \
    --item Id={S="key1"},Value={S="value1"}
```

関数が呼び出されログが出力されることを確認する

```sh
awslocal logs filter-log-events \
    --log-group-name /aws/lambda/local-function
```

## 参考
### DynamodbStreamsの状態を確認するためのコマンド

Dynamodb Streamsにあるイベントをコマンドで取得する

```sh
awslocal dynamodbstreams describe-stream \
    --stream-arn arn:aws:dynamodb:us-east-1:000000000000:table/local-table/stream/2024-02-25T00:29:17.436
```
shard-iterator-type TRIM_HORIZON, LATEST
shard-id shardId-00000001708700000000-000000000000 固定

```sh
awslocal dynamodbstreams get-shard-iterator \
    --stream-arn arn:aws:dynamodb:us-east-1:000000000000:table/local-table/stream/2024-02-24T13:10:33.518 \
    --shard-id shardId-00000001708700000000-000000000000 \
    --shard-iterator-type TRIM_HORIZON
```

```sh
awslocal dynamodbstreams get-records \
    --shard-iterator "arn:aws:dynamodb:us-east-1:000000000000:table/local-table/stream/2024-02-24T13:10:33.518|1|AAAAAAAAAAHlvj7RWoptmqYm3yLky9vhCA/i0Gs02sTZe1Pql99ew9Q6bgDra9YXlYemxSE24CePF3nRLEgB3NmNsiLbesJ/RTSNx3EJpd0ALc4eCCgprIkxb1VN6BqGig+MibyatfgqZZerQkZH+406L5yAcYpz1Q8Fy20h/xTUG3ibMeusOFe87xmVNcSTQRq5YEqriZR/I4pJBrbqLLUnX2py2WX7"
```

### CloudWatchLogsの確認のコマンド

```sh
awslocal logs filter-log-events \
    --log-group-name /aws/lambda/local-function
```

### Lambdaでよく使うコマンド

関数の更新

```sh
awslocal lambda update-function-code \
    --function-name local-function \
    --zip-file fileb:///tmp/function.zip
```

関数の単独実行

```sh
awslocal lambda invoke \
    --function-name local-function \
    --payload '{ "name": "Bob" }' \
    response.json
```