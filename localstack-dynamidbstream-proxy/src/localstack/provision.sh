#!/bin/bash
export AWS_ACCESS_KEY_ID=dummy
export AWS_SECRET_ACCESS_KEY=dummy
export AWS_DEFAULT_REGION=us-east-1

function_name="local-function"
runtime="python3.9"
zip_file="fileb:///tmp/function.zip"
handler="localstack.handler"

echo "Creating Lambda function..."
echo $function_name

awslocal lambda create-function \
    --function-name $function_name \
    --runtime $runtime \
    --zip-file $zip_file \
    --handler $handler \
    --role arn:aws:iam::000000000000:role/lambda-role

awslocal lambda get-function \
    --function-name $function_name

echo "Done creating Lambda function"

table_name="local-table"
attribute="AttributeName=Id,AttributeType=S"
key_schema="AttributeName=Id,KeyType=HASH"
stream_specification="StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES"
throughput="ReadCapacityUnits=10,WriteCapacityUnits=10"

echo "Creating DynamoDB table..."
echo $table_name

stream_arn=$(awslocal dynamodb create-table \
    --table-name $table_name \
    --attribute-definitions $attribute \
    --key-schema $key_schema \
    --stream-specification $stream_specification \
    --provisioned-throughput $throughput \
    --query 'TableDescription.LatestStreamArn' \
    --output text)

awslocal dynamodb describe-table \
    --table-name $table_name

echo "Done creating DynamoDB table"
