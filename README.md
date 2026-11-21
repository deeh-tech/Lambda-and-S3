# Event-Driven Text Word Counter Using Amazon S3, AWS Lambda, and Amazon SNS

An event-driven serverless application built on AWS that automatically counts the number of words in `.txt` files uploaded to an Amazon S3 bucket (`jbettybucket1`) using an AWS Lambda function (`Wordcountfunction`) and sends the result via email through **Amazon SNS** (`Wordcount`).

---

## Architecture Overview

### How It Works
1. **File Upload:** A user uploads a plain-text file (`.txt`) into the designated Amazon S3 input bucket (`jbettybucket1`).
2. **Event Trigger:** Amazon S3 detects the `s3:ObjectCreated:*` event and automatically invokes the AWS Lambda function (`Wordcountfunction`).
3. **Word Count Processing:** The Lambda function retrieves the uploaded file from S3, reads its content, and calculates the total word count.
4. **Notification & Logging:** The Lambda function publishes the word count summary to the **Amazon SNS** topic (`Wordcount`), which delivers an email notification to subscribed recipients, while logging execution details in **Amazon CloudWatch**.

---

## Repository Structure

```text
Lambda-and-S3/
├── images/
│   ├── Screenshot 2026-10-21 131621.png
│   ├── Screenshot 2026-10-21 131821.png
│   ├── Screenshot 2026-10-21 132158.png
│   ├── Screenshot 2026-10-21 133217.png
│   ├── Screenshot 2026-10-21 133651.png
│   ├── Screenshot 2026-10-21 133728.png
│   └── Screenshot 2026-10-21 133834.png
├── lambda_function.py
└── README.md
```

---

## AWS Services Used

| Service | Resource Name | Purpose |
| :--- | :--- | :--- |
| **Amazon S3** | `jbettybucket1` | Stores uploaded `.txt` files and triggers event notifications on object creation. |
| **AWS Lambda** | `Wordcountfunction` (Python 3.14) | Executes the serverless Python code to parse the file, compute the word count, and publish the result. |
| **Amazon SNS** | `Wordcount` (`us-west-2`) | Sends instant email notifications containing the word count result to subscribed endpoints. |
| **AWS IAM** | Lambda Execution Role | Grants permissions for S3 read (`s3:GetObject`), SNS publish (`sns:Publish`), and CloudWatch logging. |
| **Amazon CloudWatch** | `/aws/lambda/Wordcountfunction` | Captures execution logs and monitors Lambda invocations. |

---

## Setup & Deployment Steps

### 1. Create an S3 Bucket
1. Open the **Amazon S3 Console** in `us-west-2` and click **Create bucket**.
2. Name the bucket `jbettybucket1`, keep default settings, and click **Create bucket**.

### 2. Create an Amazon SNS Topic & Subscription
1. Open the **Amazon SNS Console** and click **Create topic**.
2. Select **Standard**, name the topic `Wordcount`, and click **Create topic**.
3. Copy the **Topic ARN** (`arn:aws:sns:us-west-2:<account-id>:Wordcount`) for use in the Lambda function.
4. Click **Create subscription**, set the **Protocol** to **Email**, enter your email address as the **Endpoint**, and confirm the subscription from your inbox.

### 3. Configure IAM Permissions
1. Navigate to the **AWS IAM Console** and open the execution role attached to `Wordcountfunction`.
2. Attach the following policies:
   - `AWSLambdaBasicExecutionRole` (for CloudWatch Logs)
   - `AmazonS3ReadOnlyAccess` (for reading uploaded files from `jbettybucket1`)
   - `AmazonSNSFullAccess` (or a custom policy granting `sns:Publish` on the `Wordcount` topic)

### 4. Create the AWS Lambda Function
1. Open the **AWS Lambda Console** and click **Create function**.
2. Choose **Author from scratch**, name it `Wordcountfunction`, and select **Python 3.14** as the runtime.
3. Paste the following code into `lambda_function.py` and click **Deploy**:

```python
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
```

### 5. Configure the S3 Event Trigger
1. In the `Wordcountfunction` overview, click **Add trigger**.
2. Select **S3** as the trigger source and choose `jbettybucket1`.
3. Set the **Event type** to `All object create events` (`s3:ObjectCreated:*`).
4. Set the **Suffix** filter to `.txt` so only text files trigger the function.
5. Click **Add**.

---

## Testing & Verification

1. Upload **`Happy.txt`** (45.0 B, containing 9 words) to `jbettybucket1`.
2. Check your subscribed email inbox for the Amazon SNS notification from topic `Wordcount`:

```text
The word count in the Happy.txt file is 9
```

3. Optionally, verify the execution logs in **CloudWatch** > **Log groups** > `/aws/lambda/Wordcountfunction`.
