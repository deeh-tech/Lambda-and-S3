import os
import urllib.parse
import boto3

s3 = boto3.client('s3')
sns = boto3.client('sns')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        words = content.split()
        word_count = len(words)

        message = f"The word count in the {key} file is {word_count}"
        print(message)

        if SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="Word Count Result",
                Message=message
            )

        return {
            'statusCode': 200,
            'file': key,
            'word_count': word_count
        }
    except Exception as e:
        print(f"Error processing file {key} from bucket {bucket}: {str(e)}")
        raise e
