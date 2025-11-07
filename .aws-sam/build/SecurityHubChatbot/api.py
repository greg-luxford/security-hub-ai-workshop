import json
import boto3
from chatbot import SecurityHubChatbot

def lambda_handler(event, context):
    """API Gateway handler for chatbot interactions"""
    
    # Handle CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            }
        }
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', 'Show me security findings that need remediation')
        
        # Initialize chatbot
        chatbot = SecurityHubChatbot()
        result = chatbot.process_chat_message(message)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': result['response'],
                'findings_count': result['findings_count'],
                'remediations': result.get('remediations', []),
                'timestamp': context.aws_request_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process chat message'
            })
        }
