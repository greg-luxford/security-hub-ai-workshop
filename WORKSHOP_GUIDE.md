# AWS Workshop Guide - Security Hub AI Remediation Solution

## 🎯 Workshop Overview

This workshop demonstrates how to build and deploy an AI-powered chatbot that automatically remediates AWS Security Hub findings using natural language interactions.

**Duration**: 60-90 minutes  
**Level**: Intermediate  
**Services Used**: Security Hub, Bedrock, Lambda, API Gateway, Systems Manager

## 🏗️ Architecture

```
User → API Gateway → Lambda → Bedrock (AI Analysis) → Systems Manager → AWS Resources
                        ↓
                  Security Hub Findings
```

## 📋 Prerequisites

### AWS Account Requirements
- AWS account with admin permissions
- Region: `us-east-1` or `ap-southeast-2` (Bedrock availability)
- No existing resource conflicts

### Local Environment
- AWS CLI v2 installed
- SAM CLI installed
- Python 3.12+ installed
- Git installed
- Terminal/Command prompt access

## 🚀 Workshop Steps

### Step 1: Environment Setup (10 minutes)

#### 1.1 Configure AWS CLI
```bash
# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, Region, and output format

# Verify access
aws sts get-caller-identity
```

#### 1.2 Install Required Tools
```bash
# Install SAM CLI (macOS)
brew install aws-sam-cli

# Install SAM CLI (Windows)
# Download from: https://github.com/aws/aws-sam-cli/releases

# Install Python 3.12 (if needed)
brew install python@3.12  # macOS
```

#### 1.3 Clone Workshop Repository
```bash
git clone <workshop-repo-url>
cd security-hub-ai-solution
```

### Step 2: Enable AWS Services (15 minutes)

#### 2.1 Enable Security Hub
```bash
# Enable Security Hub
aws securityhub enable-security-hub --region us-east-1

# Enable AWS Foundational Security Standard
aws securityhub batch-enable-standards \
  --standards-subscription-requests StandardsArn=arn:aws:securityhub:us-east-1::standard/aws-foundational-security-best-practices/v/1.0.0
```

#### 2.2 Enable Bedrock Model Access
1. Navigate to [Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Select your workshop region
3. Click "Model access" in left sidebar
4. Click "Request model access"
5. Select "Anthropic Claude" models
6. Fill out use case form:
   - **Use case**: Educational/Workshop
   - **Description**: "AWS Workshop for Security Automation"
7. Submit request (usually approved instantly)

#### 2.3 Create Test Security Findings
```bash
# Create an insecure security group to generate findings
aws ec2 create-security-group \
  --group-name workshop-insecure-sg \
  --description "Workshop insecure security group"

# Add unrestricted SSH rule
aws ec2 authorize-security-group-ingress \
  --group-name workshop-insecure-sg \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Wait 5-10 minutes for Security Hub to detect the finding
```

### Step 3: Deploy the Solution (15 minutes)

#### 3.1 Review Configuration
```bash
# Set workshop environment variables
export AWS_REGION=us-east-1
export ENVIRONMENT=workshop
export STACK_NAME=security-hub-ai-workshop

# Review the deployment script
cat deploy.sh
```

#### 3.2 Deploy Infrastructure
```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy the solution
./deploy.sh
```

**Expected Output**:
```
✅ Deployment completed successfully!
🔗 API Endpoint: https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/workshop/chat
```

#### 3.3 Verify Deployment
```bash
# Test API endpoint
curl -X POST 'https://your-api-endpoint/workshop/chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hello, show me security findings"}'
```

### Step 4: Using the Solution (20 minutes)

#### 4.1 Basic Queries
Test these natural language queries:

```bash
# Query 1: General findings overview
curl -X POST 'https://your-api-endpoint/workshop/chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Show me all security findings"}'

# Query 2: Critical findings only
curl -X POST 'https://your-api-endpoint/workshop/chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Show me critical security findings that need immediate attention"}'

# Query 3: Network security issues
curl -X POST 'https://your-api-endpoint/workshop/chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Fix unrestricted SSH access in my security groups"}'
```

#### 4.2 Web Interface Testing
1. Open `web/index.html` in a browser
2. The API endpoint should already be configured
3. Try these conversational queries:
   - "What security issues do I have?"
   - "Fix the SSH security group problem"
   - "Show me high priority findings"
   - "Remediate network security violations"

#### 4.3 Understanding Responses
The chatbot returns structured responses:
```json
{
  "response": "Human-readable summary",
  "findings_count": 3,
  "automated_count": 1,
  "manual_count": 2,
  "remediations": [
    {
      "finding_title": "Security group allows unrestricted access",
      "severity": "HIGH",
      "analysis": {
        "remediation_action": "revoke_sg_rule",
        "automated": true,
        "explanation": "Removes dangerous 0.0.0.0/0 access"
      },
      "execution": {
        "status": "success",
        "message": "Remediation completed"
      }
    }
  ]
}
```

### Step 5: Monitoring and Validation (10 minutes)

#### 5.1 Check CloudWatch Logs
```bash
# View Lambda function logs
aws logs tail /aws/lambda/SecurityHubChatbot-workshop --follow

# View recent log events
aws logs describe-log-streams \
  --log-group-name /aws/lambda/SecurityHubChatbot-workshop
```

#### 5.2 Verify Remediation
```bash
# Check if security group rule was removed
aws ec2 describe-security-groups \
  --group-names workshop-insecure-sg \
  --query 'SecurityGroups[0].IpPermissions'

# Check Security Hub finding status
aws securityhub get-findings \
  --filters '{"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}' \
  --query 'Findings[?Title==`EC2.19 Security groups should not allow unrestricted access to ports with high risk`]'
```

#### 5.3 Cost Monitoring
```bash
# Check current month costs (approximate)
aws ce get-cost-and-usage \
  --time-period Start=2025-11-01,End=2025-11-07 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## 🧪 Workshop Exercises

### Exercise 1: Custom Query Testing
Try these advanced queries and observe the AI responses:
- "What's the most critical security issue I should fix first?"
- "Show me findings related to data encryption"
- "Are there any compliance violations?"
- "Fix all network security problems automatically"

### Exercise 2: Add New Remediation
1. Create a new SSM document in `template.yaml`
2. Add logic in `src/chatbot.py`
3. Redeploy with `./deploy.sh`
4. Test the new remediation

### Exercise 3: Security Analysis
1. Create additional insecure resources
2. Wait for Security Hub detection
3. Use the chatbot to analyze and remediate
4. Verify fixes were applied

## 🔧 Troubleshooting

### Common Issues

#### Bedrock Access Denied
```bash
# Error: Model use case details not submitted
# Solution: Complete Bedrock model access request in console
```

#### No Security Findings
```bash
# Wait 10-15 minutes after creating insecure resources
# Security Hub needs time to detect and report findings

# Force a compliance check
aws configservice start-config-rules-evaluation \
  --config-rule-names securityhub-ec2-security-group-attached-to-eni
```

#### Lambda Timeout
```bash
# Increase timeout in template.yaml
Timeout: 900  # 15 minutes

# Redeploy
./deploy.sh
```

#### API Gateway CORS Issues
```bash
# Test with curl instead of browser
curl -X POST 'https://your-endpoint/workshop/chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "test"}'
```

## 📊 Workshop Outcomes

By the end of this workshop, participants will have:

✅ **Built** a serverless AI security automation solution  
✅ **Deployed** infrastructure using SAM/CloudFormation  
✅ **Integrated** multiple AWS services (Security Hub, Bedrock, Lambda)  
✅ **Tested** natural language security remediation  
✅ **Monitored** solution performance and costs  
✅ **Understood** AI-powered security automation patterns  

## 🧹 Cleanup

### Remove Workshop Resources
```bash
# Delete CloudFormation stack
aws cloudformation delete-stack \
  --stack-name security-hub-ai-workshop

# Remove test security group
aws ec2 delete-security-group \
  --group-name workshop-insecure-sg

# Disable Security Hub (optional)
aws securityhub disable-security-hub
```

### Verify Cleanup
```bash
# Check stack deletion status
aws cloudformation describe-stacks \
  --stack-name security-hub-ai-workshop

# Should return: Stack does not exist
```

## 💡 Workshop Extensions

### Advanced Topics (Optional)
1. **Multi-Region Deployment**: Deploy to multiple regions
2. **Custom Findings**: Create custom Security Hub findings
3. **Slack Integration**: Send remediation notifications to Slack
4. **Scheduled Scans**: Automate regular security assessments
5. **Cost Optimization**: Implement usage-based scaling

### Real-World Applications
- **Enterprise Security**: Scale for large organizations
- **Compliance Automation**: Automate regulatory compliance
- **DevSecOps Integration**: Integrate with CI/CD pipelines
- **Incident Response**: Automate security incident handling

## 📚 Additional Resources

- [AWS Security Hub User Guide](https://docs.aws.amazon.com/securityhub/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/)
- [Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)

---

**Workshop Duration**: 60-90 minutes  
**Difficulty**: Intermediate  
**Cost**: <$5 for workshop duration
