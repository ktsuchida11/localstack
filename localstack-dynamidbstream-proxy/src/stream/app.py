import boto3
import os
import time
import json

# 環境変数よりパラメータ取得
table_name = os.getenv('DYNAMODB_TABLE')
function_name = os.getenv('LAMBDA_FUNCTION')
endpoint_url = os.getenv('DYNAMODB_ENDPOINT')

boto3.setup_default_session(
    aws_access_key_id='dummy',  # ローカルといえども何かを送る必要あるので値は適当
    aws_secret_access_key='dummy',  # 同上
    region_name='us-east-1', # dynamodbは右us-east-1でしか動かない
)

print(table_name)
print(function_name)

resource_dynamo = boto3.resource('dynamodb', endpoint_url=endpoint_url)
client_lambda = boto3.client('lambda', endpoint_url=endpoint_url)


def get_dynamodb_data(resource_dynamo, table_name) :

        item_count = 0
        items = None

        table = resource_dynamo.Table(table_name)
        # 全てのアイテムを取得
        response = table.scan()

        item_count = response['Count']
        items = response['Items']

        return table.table_arn, item_count, items


def invoke_lambda(client_lambda,function_name,payload) :

    # Lambda関数を同期実行
    response = client_lambda.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',  # 同期実行
        Payload=json.dumps(payload),
    )

    # 実行結果の取得
    result = json.loads(response['Payload'].read().decode('utf-8'))

    return result

def create_insert_payload(table_arn) :

    payload = {
        "Records": [
            {
                "eventID": "dummuy_insert_event1",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1581435982,
                    "Keys": {
                        "id": {
                            "S": "0001"
                        }
                    },
                    "NewImage": {
                        "value": {
                            "S": "value1"
                        },
                        "id": {
                            "S": "0001"
                        }
                    },
                    "SequenceNumber": "100000000000000000000001",
                    "SizeBytes": 50,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": table_arn
            }
        ]
    }

    return payload

def create_modify_payload(table_arn) :

    payload = {
        "Records": [
            {
                "eventID": "dummuy_modify_event1",
                "eventName": "MODIFY",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1581436133,
                    "Keys": {
                        "id": {
                            "S": "0001"
                        }
                    },
                    "NewImage": {
                        "value": {
                            "S": "value2"
                        },
                        "id": {
                            "S": "0001"
                        }
                    },
                    "OldImage": {
                        "value": {
                            "S": "value1"
                        },
                        "id": {
                            "S": "0001"
                        }
                    },
                    "SequenceNumber": "10000000000000000000002",
                    "SizeBytes": 100,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": table_arn
            }
        ]
    }

    return payload

def create_remove_payload(table_arn) :

    payload = {
        "Records": [
            {
                "eventID": "dummuy_remove_event1",
                "eventName": "REMOVE",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1581435982,
                    "Keys": {
                        "id": {
                            "S": "0001"
                        }
                    },
                    "NewImage": {
                        "value": {
                            "S": "value1"
                        },
                        "id": {
                            "S": "0001"
                        }
                    },
                    "SequenceNumber": "10000000000000000000003",
                    "SizeBytes": 50,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": table_arn
            }
        ]
    }

    return payload



# ---------------------
# main
# DynamoDBの初期状態を取得
table_arn, before_item_count, before_items = get_dynamodb_data(resource_dynamo,table_name)

# スリープを入れる
time.sleep(3)

# ストリームを無限ループで読む
while True:

    print("start loop")
    result = ""
    payload = ""
    # 現在のDynamoDBのレコードを全部取得
    table_arn, current_item_count, current_items = get_dynamodb_data(resource_dynamo,table_name)

    print(before_items)
    print(before_item_count)
    print(current_items)
    print(current_item_count)
    # レコード数が変わっているかどうかを確認する
    if before_item_count == current_item_count:
        if current_item_count > 0 :
            i = 0
            for item in before_items :
                print(before_items[i])
                print(current_items[i])
                # https://dev.classmethod.jp/articles/dynamodb-local-and-boto3/
                # レコードの中身が更新されているかを確認して変化があった場合変更レスポンスを返す
                if before_items[i].items() - current_items[i].items() :
                    print("modify")
                    payload = create_modify_payload(table_arn)
                    break
                i+=1
    elif before_item_count > current_item_count:
        print("remove")
        payload = create_remove_payload(table_arn)
    elif before_item_count < current_item_count:
        print("insert")
        payload = create_insert_payload(table_arn)
    else :
        break

    if payload != "" :
        print(payload)
        result = invoke_lambda(client_lambda,function_name,payload)
        print(result)

    before_item_count = current_item_count
    before_items = current_items

    # スリープを入れる
    time.sleep(3)