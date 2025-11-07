#!/bin/bash

# AWS Workshop Setup Script - Security Hub AI Remediation
# This script prepares the workshop environment and creates test findings

set -e

REGION="${AWS_REGION:-us-east-1}"
WORKSHOP_PREFIX="workshop-security-hub"

echo "🎯 Setting up AWS Workshop Environment"
echo "Region: $REGION"
echo "Prefix: $WORKSHOP_PREFIX"
echo "=================================="

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Enable Security Hub
echo "🛡️ Enabling Security Hub..."
if aws securityhub describe-hub --region $REGION > /dev/null 2>&1; then
    echo "✅ Security Hub already enabled"
else
    echo "Enabling Security Hub..."
    aws securityhub enable-security-hub --region $REGION
    
    echo "Enabling AWS Foundational Security Standard..."
    aws securityhub batch-enable-standards \
        --region $REGION \
        --standards-subscription-requests StandardsArn=arn:aws:securityhub:$REGION::standard/aws-foundational-security-best-practices/v/1.0.0
    
    echo "✅ Security Hub enabled"
fi

# Create insecure resources for testing
echo "🔧 Creating test resources..."

# Create insecure security group
SG_ID=$(aws ec2 create-security-group \
    --group-name $WORKSHOP_PREFIX-insecure-sg \
    --description "Workshop insecure security group for testing" \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>/dev/null || echo "exists")

if [ "$SG_ID" != "exists" ]; then
    echo "Created security group: $SG_ID"
    
    # Add unrestricted SSH access
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # Add unrestricted RDP access
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 3389 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    echo "✅ Created insecure security group with unrestricted access"
else
    echo "⚠️ Security group already exists"
fi

# Create S3 bucket with public access for testing
BUCKET_NAME="$WORKSHOP_PREFIX-public-bucket-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket creation skipped"

if aws s3 ls s3://$BUCKET_NAME > /dev/null 2>&1; then
    # Disable block public access
    aws s3api put-public-access-block \
        --bucket $BUCKET_NAME \
        --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
    
    # Add public read policy
    cat > /tmp/public-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF
    
    aws s3api put-bucket-policy \
        --bucket $BUCKET_NAME \
        --policy file:///tmp/public-policy.json
    
    echo "✅ Created public S3 bucket: $BUCKET_NAME"
fi

# Check Bedrock model access
echo "🤖 Checking Bedrock model access..."
if aws bedrock list-foundation-models --region $REGION --query "modelSummaries[?modelId=='anthropic.claude-3-haiku-20240307-v1:0']" --output text > /dev/null 2>&1; then
    echo "✅ Bedrock Claude model access verified"
else
    echo "⚠️ Bedrock model access not enabled"
    echo "Please enable Bedrock model access:"
    echo "1. Go to https://console.aws.amazon.com/bedrock/"
    echo "2. Select region: $REGION"
    echo "3. Click 'Model access' → 'Request model access'"
    echo "4. Select 'Anthropic Claude' models"
    echo "5. Fill out use case form and submit"
fi

echo ""
echo "🎉 Workshop environment setup complete!"
echo "=================================="
echo "Resources created:"
echo "- Security Hub enabled with standards"
echo "- Insecure security group: $WORKSHOP_PREFIX-insecure-sg"
echo "- Public S3 bucket: $BUCKET_NAME"
echo ""
echo "⏰ Wait 10-15 minutes for Security Hub to detect findings"
echo ""
echo "Next steps:"
echo "1. Ensure Bedrock model access is enabled"
echo "2. Run: ./deploy.sh"
echo "3. Test the solution with workshop queries"
echo ""
echo "Cleanup command:"
echo "./workshop-cleanup.sh"
