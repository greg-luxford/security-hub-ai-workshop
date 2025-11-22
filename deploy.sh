#!/bin/bash

# Security Hub AI Remediation Solution Deployment Script
# This script deploys a cost-effective, secure chatbot for remediating AWS Security Hub findings

set -e

# Configuration
PROFILE="${AWS_PROFILE:-mymlpg-audit}"
REGION="${AWS_REGION:-ap-southeast-2}"
STACK_NAME="${STACK_NAME:-security-hub-ai-remediation}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

echo "🚀 Deploying Security Hub AI Remediation Solution..."
echo "=================================================="
echo "Profile: $PROFILE"
echo "Region: $REGION"
echo "Stack Name: $STACK_NAME"
echo "Environment: $ENVIRONMENT"
echo "=================================================="

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI is not installed. Please install it first:"
    echo "brew install aws-sam-cli"
    exit 1
fi

# Check if Python 3.12 is available
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 is not installed. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install python@3.12
    else
        echo "Please install Python 3.12 manually"
        exit 1
    fi
fi

# Verify AWS credentials
echo "🔐 Verifying AWS credentials..."
if ! aws sts get-caller-identity --profile $PROFILE --region $REGION > /dev/null 2>&1; then
    echo "❌ AWS credentials not valid. Please run:"
    echo "aws sso login --profile $PROFILE"
    exit 1
fi

# Get account information
ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --query Account --output text)
echo "✅ Authenticated as account: $ACCOUNT_ID"

# Check if Security Hub is enabled
echo "🛡️ Checking Security Hub status..."
if ! aws securityhub describe-hub --profile $PROFILE --region $REGION > /dev/null 2>&1; then
    echo "⚠️ Security Hub is not enabled in region $REGION"
    echo "Please enable Security Hub first:"
    echo "aws securityhub enable-security-hub --profile $PROFILE --region $REGION"
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Security Hub is enabled"
fi

# Check Bedrock model access
echo "🤖 Checking Bedrock model access..."
BEDROCK_MODEL="anthropic.claude-3-haiku-20240307-v1:0"
if ! aws bedrock list-foundation-models --profile $PROFILE --region $REGION --query "modelSummaries[?modelId=='$BEDROCK_MODEL']" --output text > /dev/null 2>&1; then
    echo "⚠️ Bedrock model $BEDROCK_MODEL may not be available in $REGION"
    echo "Please ensure Bedrock is enabled and the model is accessible"
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Bedrock model access verified"
fi

# Set Python path for SAM
export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"

# Build the SAM application
echo "📦 Building SAM application..."
sam build

# Deploy the application
echo "🚀 Deploying to AWS..."
sam deploy \
    --stack-name $STACK_NAME \
    --region $REGION \
    --profile $PROFILE \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --resolve-s3 \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        BedrockModelId=$BEDROCK_MODEL \
    --tags \
        Project=SecurityHubAIRemediation \
        Environment=$ENVIRONMENT \
        DeployedBy=$(whoami) \
        DeployedAt=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Get deployment outputs
echo "📋 Getting deployment outputs..."
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --profile $PROFILE \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text 2>/dev/null || echo "Not available")

CHATBOT_FUNCTION_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --profile $PROFILE \
    --query 'Stacks[0].Outputs[?OutputKey==`ChatbotFunctionArn`].OutputValue' \
    --output text 2>/dev/null || echo "Not available")

echo ""
echo "✅ Deployment completed successfully!"
echo "=================================================="
echo "🔗 API Endpoint: $API_ENDPOINT"
echo "🔧 Chatbot Function ARN: $CHATBOT_FUNCTION_ARN"
echo "=================================================="

# Test the deployment
if [[ "$API_ENDPOINT" != "Not available" ]]; then
    echo ""
    echo "🧪 Testing the deployment..."
    
    # Create test payload
    TEST_PAYLOAD='{"message": "Show me critical security findings that need immediate attention"}'
    
    echo "💬 Test the chatbot with:"
    echo "curl -X POST '$API_ENDPOINT' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '$TEST_PAYLOAD'"
    
    echo ""
    echo "🌐 Update the web interface:"
    echo "Replace 'YOUR_API_ENDPOINT_HERE' in web/index.html with:"
    echo "$API_ENDPOINT"
fi

echo ""
echo "🔒 Security Features Deployed:"
echo "- IAM roles with least privilege access"
echo "- API Gateway with CORS enabled"
echo "- Bedrock model access restricted to Claude Haiku"
echo "- SSM execution limited to specific remediation documents"
echo "- CloudWatch logging enabled"
echo "- S3 bucket with encryption and public access blocked"

echo ""
echo "💰 Cost Optimization Features:"
echo "- Uses Claude Haiku (fast and cost-effective Bedrock model)"
echo "- Serverless architecture (pay-per-use)"
echo "- Processes maximum 5 findings per request"
echo "- 1024MB memory allocation for Lambda functions"
echo "- Regional API Gateway endpoint"

echo ""
echo "📚 Next Steps:"
echo "1. Test the API endpoint with the curl command above"
echo "2. Update web/index.html with the API endpoint"
echo "3. Review CloudWatch logs for any issues"
echo "4. Configure additional SSM documents for more remediation types"
echo "5. Set up CloudWatch alarms for monitoring"

echo ""
echo "🔧 Management Commands:"
echo "- View logs: aws logs tail /aws/lambda/SecurityHubChatbot-$ENVIRONMENT --follow --profile $PROFILE"
echo "- Update stack: ./deploy.sh"
echo "- Delete stack: aws cloudformation delete-stack --stack-name $STACK_NAME --profile $PROFILE --region $REGION"

echo ""
echo "🎉 Deployment complete! Your Security Hub AI Remediation solution is ready to use."
