#!/bin/bash

# AWS Workshop Cleanup Script - Security Hub AI Remediation
# This script removes all workshop resources

set -e

REGION="${AWS_REGION:-us-east-1}"
WORKSHOP_PREFIX="workshop-security-hub"
STACK_NAME="${STACK_NAME:-security-hub-ai-remediation}"

echo "🧹 Cleaning up AWS Workshop Environment"
echo "Region: $REGION"
echo "Stack: $STACK_NAME"
echo "=================================="

# Delete CloudFormation stack
echo "🗑️ Deleting CloudFormation stack..."
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION > /dev/null 2>&1; then
    aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
    echo "Stack deletion initiated. This may take 5-10 minutes..."
    
    # Wait for stack deletion (optional)
    echo "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $REGION
    echo "✅ CloudFormation stack deleted"
else
    echo "⚠️ Stack not found or already deleted"
fi

# Delete test security group
echo "🔧 Removing test security group..."
if aws ec2 describe-security-groups --group-names $WORKSHOP_PREFIX-insecure-sg --region $REGION > /dev/null 2>&1; then
    aws ec2 delete-security-group --group-name $WORKSHOP_PREFIX-insecure-sg --region $REGION
    echo "✅ Security group deleted"
else
    echo "⚠️ Security group not found or already deleted"
fi

# Delete test S3 buckets
echo "🪣 Removing test S3 buckets..."
for bucket in $(aws s3 ls | grep $WORKSHOP_PREFIX | awk '{print $3}'); do
    echo "Deleting bucket: $bucket"
    # Empty bucket first
    aws s3 rm s3://$bucket --recursive 2>/dev/null || true
    # Delete bucket
    aws s3 rb s3://$bucket 2>/dev/null || true
    echo "✅ Bucket $bucket deleted"
done

# Clean up temporary files
echo "📁 Cleaning up temporary files..."
rm -f /tmp/public-policy.json
rm -rf .aws-sam/

echo ""
echo "🎉 Workshop cleanup complete!"
echo "=================================="
echo "Removed resources:"
echo "- CloudFormation stack: $STACK_NAME"
echo "- Security group: $WORKSHOP_PREFIX-insecure-sg"
echo "- S3 buckets with prefix: $WORKSHOP_PREFIX"
echo "- Temporary files"
echo ""
echo "Optional cleanup (if desired):"
echo "- Disable Security Hub: aws securityhub disable-security-hub --region $REGION"
echo "- Remove Bedrock model access via console"
echo ""
echo "✅ All workshop resources have been removed"
