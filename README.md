# Security Hub AI Remediation Solution

A cost-effective, secure chatbot solution that uses natural language to remediate AWS Security Hub findings through Systems Manager documents. This solution provides an intelligent interface for security teams to quickly understand and remediate common security issues.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │───▶│   API Gateway    │───▶│  Lambda Function│
│   (Optional)    │    │                  │    │   (Chatbot)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────┐              │
                       │   Amazon        │◀─────────────┘
                       │   Bedrock       │
                       │ (Claude Haiku)  │
                       └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Security Hub   │───▶│  Systems Manager │───▶│   EC2/Resources │
│   Findings      │    │   Documents      │    │  (Remediation)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Why Claude Haiku?** We switched from Amazon Titan to Claude Haiku due to API Gateway timeout issues. Claude Haiku provides faster response times, better analysis quality, and stays well within the 30-second API Gateway timeout limit.

### Components

- **Amazon Bedrock** (Claude Haiku) - Natural language processing and remediation analysis
- **AWS Lambda** - Chatbot logic and remediation orchestration
- **API Gateway** - REST API for chat interface
- **Systems Manager** - Automated remediation document execution
- **Security Hub** - Finding analysis and status updates
- **S3** - Secure storage for deployment artifacts

## 💰 Cost Optimization

This solution is designed for cost efficiency:

- **Claude Haiku**: Fast, cost-effective Bedrock model (~$0.25/1M input tokens, ~$1.25/1M output tokens)
- **Serverless Architecture**: Pay-per-use Lambda and API Gateway
- **Optimized Processing**: Maximum 5 findings per request
- **Minimal Resources**: 1024MB Lambda memory allocation
- **Regional Deployment**: Reduces data transfer costs

**Estimated Monthly Cost**: $5-20 for light usage (100-500 requests/month)

## 🔒 Security Features

- **Least Privilege IAM**: Roles with minimal required permissions
- **Regional Restrictions**: API calls limited to deployment region
- **Encrypted Storage**: S3 bucket with AES-256 encryption
- **VPC Compatible**: Can be deployed within VPC for enhanced security
- **Audit Logging**: CloudWatch logs for all operations
- **Input Validation**: Parameter validation for SSM documents

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **SAM CLI** installed (`brew install aws-sam-cli`)
3. **Python 3.12** installed (`brew install python@3.12`)
4. **Security Hub** enabled in target region
5. **Bedrock Model Access** enabled for Claude Haiku (requires manual approval in AWS Console)

### Deployment

1. **Clone and navigate to the repository**:
   ```bash
   git clone <repository-url>
   cd security-hub-ai-solution
   ```

2. **Enable Bedrock Model Access**:
   - Open AWS Console → Amazon Bedrock → Model access
   - Click "Manage model access"
   - Select "Anthropic" → "Claude 3 Haiku"
   - Click "Request model access" and submit the form
   - Wait for approval (usually instant to a few minutes)

3. **Configure AWS SSO** (if using SSO):
   ```bash
   aws sso login --profile your-profile-name
   ```

4. **Deploy the solution**:
   ```bash
   # Set environment variables (optional)
   export AWS_PROFILE=your-profile-name
   export AWS_REGION=ap-southeast-2
   export ENVIRONMENT=dev
   
   # Deploy
   ./deploy.sh
   ```

5. **Test the deployment**:
   ```bash
   curl -X POST 'https://your-api-endpoint/dev/chat' \
     -H 'Content-Type: application/json' \
     -d '{"message": "Show me critical security findings"}'
   ```

## 📖 Usage

### API Endpoint

The solution provides a REST API endpoint for chat interactions:

```bash
POST /chat
Content-Type: application/json

{
  "message": "Your natural language query about security findings"
}
```

### Example Queries

- `"Show me critical security findings that need immediate attention"`
- `"Fix unrestricted SSH access in my security groups"`
- `"What high severity findings can be automatically remediated?"`
- `"Remediate security group violations"`
- `"Show me findings related to network security"`

### Response Format

```json
{
  "response": "Summary of analysis and actions taken",
  "findings_count": 3,
  "automated_count": 1,
  "manual_count": 2,
  "remediations": [
    {
      "finding_id": "arn:aws:securityhub:...",
      "finding_title": "Security group allows unrestricted access",
      "severity": "HIGH",
      "analysis": {
        "remediation_action": "revoke_sg_rule",
        "ssm_document": "SecurityHub-RemediateUnrestrictedSSH-dev",
        "automated": true,
        "explanation": "Removes 0.0.0.0/0 SSH access from security group"
      },
      "execution": {
        "status": "success",
        "command_id": "abc123",
        "message": "Remediation initiated for security group sg-123456"
      }
    }
  ]
}
```

### Web Interface

A simple web interface is provided in `web/index.html`:

1. Update the API endpoint in the HTML file
2. Open in a web browser
3. Chat with the bot using natural language

## 🛠️ Supported Remediations

Currently supports automatic remediation for:

### Network Security
- **Unrestricted SSH Access**: Removes 0.0.0.0/0 access on port 22
- **Unrestricted RDP Access**: Removes 0.0.0.0/0 access on port 3389

### Adding New Remediations

1. **Create SSM Document** in `template.yaml`:
   ```yaml
   NewRemediationDocument:
     Type: AWS::SSM::Document
     Properties:
       Name: !Sub 'SecurityHub-NewRemediation-${Environment}'
       DocumentType: Command
       Content:
         # Your remediation logic
   ```

2. **Update Lambda Function** in `src/chatbot.py`:
   ```python
   # Add logic to detect and execute new remediation type
   if 'new-finding-type' in finding_title.lower():
       return {
           "remediation_action": "new_action",
           "ssm_document": f"SecurityHub-NewRemediation-{self.environment}",
           "automated": True
       }
   ```

3. **Update IAM Permissions** in `template.yaml` if needed

4. **Redeploy**: `./deploy.sh`

## 🔧 Configuration

### Environment Variables

- `AWS_PROFILE`: AWS profile to use (default: mymlpg-audit)
- `AWS_REGION`: AWS region for deployment (default: ap-southeast-2)
- `ENVIRONMENT`: Environment name (default: dev)
- `STACK_NAME`: CloudFormation stack name

### Parameters

- `BedrockModelId`: Bedrock model to use (default: anthropic.claude-3-haiku-20240307-v1:0)
- `Environment`: Deployment environment (dev/staging/prod)

## 📊 Monitoring

### CloudWatch Logs

- Lambda function logs: `/aws/lambda/SecurityHubChatbot-{environment}`
- API Gateway logs: Available through API Gateway console

### Key Metrics to Monitor

- Lambda invocation count and duration
- API Gateway request count and latency
- Bedrock token usage and costs
- SSM command execution success rate

### Useful Commands

```bash
# View Lambda logs
aws logs tail /aws/lambda/SecurityHubChatbot-dev --follow --profile your-profile

# Check stack status
aws cloudformation describe-stacks --stack-name security-hub-ai-remediation

# List recent SSM command executions
aws ssm list-commands --max-items 10
```

## 🧪 Testing

### Unit Testing

```bash
# Install test dependencies
pip install pytest boto3 moto

# Run tests (when implemented)
pytest tests/
```

### Integration Testing

```bash
# Test API endpoint
curl -X POST 'https://your-api-endpoint/dev/chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "test message"}'

# Test Lambda function directly
aws lambda invoke \
  --function-name SecurityHubChatbot-dev \
  --payload '{"message": "test"}' \
  response.json
```

## 🚨 Troubleshooting

### Common Issues

1. **Bedrock Access Denied**
   - Ensure Bedrock is enabled in your region
   - Enable Claude Haiku model access in AWS Console (Bedrock → Model access)
   - Wait for model access approval (usually instant)
   - Verify the model ID is correct: anthropic.claude-3-haiku-20240307-v1:0

2. **Security Hub Not Enabled**
   - Enable Security Hub: `aws securityhub enable-security-hub`
   - Wait for initial findings to populate

3. **SSM Command Failures**
   - Check IAM permissions for EC2 actions
   - Verify security group IDs are valid
   - Review SSM document syntax

4. **Lambda Timeout**
   - Increase timeout in template.yaml
   - Optimize finding processing logic
   - Reduce batch size

### Debug Mode

Set `LOG_LEVEL=DEBUG` in Lambda environment variables for detailed logging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Update documentation as needed
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Format code
black src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Security Hub team for comprehensive security findings
- Anthropic for Claude Haiku - fast and cost-effective AI model
- Amazon Bedrock team for accessible AI infrastructure
- AWS SAM team for serverless deployment framework

## 📞 Support

For issues and questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review [CloudWatch logs](#cloudwatch-logs)
3. Open an issue in the GitHub repository
4. Contact your AWS support team for AWS-specific issues

---

**⚠️ Important**: This solution performs automated remediation actions on your AWS resources. Always test in a non-production environment first and review all remediation actions before deploying to production.
