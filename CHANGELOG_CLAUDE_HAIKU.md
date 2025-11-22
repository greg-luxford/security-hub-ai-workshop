# Changelog: Switch from Amazon Titan to Claude Haiku

## Summary
Updated all documentation to reflect the switch from Amazon Titan to Claude Haiku due to API Gateway timeout issues.

## Reason for Change
- **Problem**: Amazon Titan response times exceeded API Gateway's 30-second timeout limit
- **Solution**: Switched to Claude Haiku which responds in 2-5 seconds
- **Benefits**: 
  - Faster response times (no timeouts)
  - Better analysis quality
  - More cost-effective (~$0.25/1M input vs ~$0.50/1M for Titan)

## Files Updated

### README.md
- Updated architecture diagram to show Claude Haiku
- Added explanation of why Claude Haiku was chosen
- Updated prerequisites to include Claude Haiku model access requirement
- Added step-by-step instructions for enabling Claude Haiku in AWS Console
- Updated cost estimates ($5-20/month vs $4-18/month)
- Updated troubleshooting section with Claude-specific guidance
- Updated acknowledgments to credit Anthropic

### USER_GUIDE.md
- Changed title from "Amazon Titan" to "Claude Haiku"

### WORKSHOP_GUIDE.md
- Added important note about model selection and timeout issues
- Updated Step 2.2 with detailed Claude Haiku enablement instructions
- Changed duration from 15 to 20 minutes for service enablement
- Updated troubleshooting section with Claude-specific error messages
- Added resources section with Anthropic Claude documentation
- Added warning section explaining the Titan→Claude switch

### WORKSHOP_HANDOUT.md
- Updated setup instructions to enable Claude Haiku first
- Updated troubleshooting section with detailed model access steps
- Updated key learning points to mention Claude Haiku

### DEPLOYMENT_SUMMARY.md
- Changed model configuration section from Titan to Claude Haiku
- Added explanation of why we switched (timeout issues)
- Updated cost estimates
- Updated Lambda memory from 512MB to 1024MB
- Updated immediate action items with Claude Haiku enablement steps

## Key Changes Required by Users

### Before Deployment
Users must now:
1. Open AWS Console
2. Navigate to Amazon Bedrock → Model access
3. Click "Manage model access"
4. Select "Anthropic" → "Claude 3 Haiku"
5. Click "Request model access"
6. Fill out use case form
7. Wait for approval (usually instant)

### Model ID
- **Old**: `amazon.titan-text-express-v1`
- **New**: `anthropic.claude-3-haiku-20240307-v1:0`

## Technical Details

### Code Changes (Already Implemented)
The code in `src/chatbot.py` already supports both models:
- Anthropic format: Uses `messages` API with `anthropic_version`
- Titan format: Uses `inputText` with `textGenerationConfig`

### Template Configuration
Updated `template.yaml` to use Claude Haiku as the default:
```yaml
Parameters:
  BedrockModelId:
    Type: String
    Default: 'anthropic.claude-3-haiku-20240307-v1:0'  # Changed from Titan
    Description: 'Bedrock model ID for the chatbot (Claude Haiku recommended - fast and cost-effective)'
    AllowedValues:
      - 'anthropic.claude-3-haiku-20240307-v1:0'  # Now first/default
      - 'anthropic.claude-3-sonnet-20240229-v1:0'
      - 'amazon.titan-text-express-v1'  # Moved to last (not recommended)
```

## Testing Recommendations
After updating documentation, users should:
1. Enable Claude Haiku model access
2. Deploy/redeploy the solution
3. Test with sample queries
4. Verify response times are under 5 seconds
5. Confirm no API Gateway timeouts occur

## Date
November 22, 2025
