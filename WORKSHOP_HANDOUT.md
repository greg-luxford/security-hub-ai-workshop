# 🎯 Workshop Handout: Security Hub AI Remediation

## Quick Start Commands

### 1. Setup Workshop Environment
```bash
# Clone repository
git clone <repo-url>
cd security-hub-ai-solution

# Enable Claude Haiku model access first!
# Go to: AWS Console → Bedrock → Model access
# Select "Anthropic" → "Claude 3 Haiku" → Request access

# Setup test resources
./workshop-setup.sh

# Wait 10-15 minutes for Security Hub findings
```

### 2. Deploy Solution
```bash
# Deploy infrastructure
./deploy.sh

# Note your API endpoint from output
```

### 3. Test Queries

#### Basic Testing (curl)
```bash
# Replace YOUR_API_ENDPOINT with actual endpoint
export API_ENDPOINT="https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/workshop/chat"

# Test 1: General overview
curl -X POST $API_ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{"message": "Show me all security findings"}'

# Test 2: Critical findings
curl -X POST $API_ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{"message": "Show me critical security findings"}'

# Test 3: Automated remediation
curl -X POST $API_ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{"message": "Fix unrestricted SSH access automatically"}'
```

#### Web Interface Testing
1. Open `web/index.html` in browser
2. Try these conversational queries:
   - "What security issues do I have?"
   - "Fix the SSH security problem"
   - "Show me network security violations"
   - "Remediate high priority findings"

## 🧪 Workshop Exercises

### Exercise 1: Query Variations
Try these natural language queries:
- "What's the most critical issue?"
- "Show me findings about encryption"
- "Are there compliance violations?"
- "Fix all network problems"

### Exercise 2: Response Analysis
Examine the JSON response structure:
- `findings_count`: Total findings analyzed
- `automated_count`: Automatically remediated
- `manual_count`: Requiring manual review
- `remediations[]`: Detailed remediation actions

### Exercise 3: Monitoring
```bash
# View logs
aws logs tail /aws/lambda/SecurityHubChatbot-workshop --follow

# Check remediation status
aws ssm list-commands --max-items 5
```

## 🔧 Troubleshooting

### Common Issues

**No findings returned**
- Wait 15+ minutes after setup
- Check Security Hub is enabled: `aws securityhub describe-hub`

**Bedrock access denied**
- Enable Claude Haiku model access in Bedrock console
- Go to: AWS Console → Bedrock → Model access → Manage model access
- Select "Anthropic" → "Claude 3 Haiku"
- Submit use case form (approval usually instant)

**API Gateway errors**
- Check CORS settings
- Use curl instead of browser for testing
- Verify API endpoint URL

**Lambda timeout**
- Check CloudWatch logs
- Increase timeout in template.yaml if needed

## 📊 Expected Results

### Successful Response Example
```json
{
  "response": "Analyzed 3 Security Hub findings. 1 automatically remediated. 2 require manual review.",
  "findings_count": 3,
  "automated_count": 1,
  "manual_count": 2,
  "remediations": [
    {
      "finding_title": "Security group allows unrestricted SSH access",
      "severity": "HIGH",
      "analysis": {
        "remediation_action": "revoke_sg_rule",
        "automated": true,
        "explanation": "Removed 0.0.0.0/0 SSH access from security group"
      },
      "execution": {
        "status": "success",
        "message": "Remediation completed for sg-xxxxxxxxx"
      }
    }
  ]
}
```

## 🧹 Cleanup
```bash
# Remove all workshop resources
./workshop-cleanup.sh
```

## 💡 Key Learning Points

1. **AI Integration**: How to use Bedrock with Claude Haiku for security analysis
2. **Serverless Architecture**: Lambda + API Gateway patterns
3. **Infrastructure as Code**: SAM/CloudFormation deployment
4. **Security Automation**: Systems Manager document execution
5. **Cost Optimization**: Pay-per-use serverless design with fast, efficient AI model

## 📞 Need Help?

1. Check CloudWatch logs: `/aws/lambda/SecurityHubChatbot-workshop`
2. Verify AWS service status
3. Review workshop guide: `WORKSHOP_GUIDE.md`
4. Ask workshop instructor

---
**Workshop Duration**: 60-90 minutes  
**Estimated Cost**: <$5
