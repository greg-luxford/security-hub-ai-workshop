import json
import boto3
import os
import logging
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class SecurityHubChatbot:
    def __init__(self):
        """Initialize the Security Hub Chatbot with AWS clients"""
        try:
            self.region = os.environ.get('REGION', 'ap-southeast-2')
            self.account_id = os.environ.get('ACCOUNT_ID')
            self.environment = os.environ.get('ENVIRONMENT', 'dev')
            
            # Initialize AWS clients
            self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
            self.securityhub = boto3.client('securityhub', region_name=self.region)
            self.ssm = boto3.client('ssm', region_name=self.region)
            self.ec2 = boto3.client('ec2', region_name=self.region)
            
            self.model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
            
            logger.info(f"Initialized SecurityHubChatbot for region: {self.region}, environment: {self.environment}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SecurityHubChatbot: {str(e)}")
            raise

    def get_security_hub_findings(self, filters: Optional[Dict] = None, max_results: int = 10) -> List[Dict]:
        """Retrieve Security Hub findings with optional filters"""
        try:
            # Default filters for active findings
            default_filters = {
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}],
                'WorkflowStatus': [{'Value': 'NEW', 'Comparison': 'EQUALS'}]
            }
            
            if filters:
                default_filters.update(filters)
            
            paginator = self.securityhub.get_paginator('get_findings')
            findings = []
            
            for page in paginator.paginate(
                Filters=default_filters,
                PaginationConfig={'MaxItems': max_results}
            ):
                findings.extend(page['Findings'])
                if len(findings) >= max_results:
                    break
            
            logger.info(f"Retrieved {len(findings)} Security Hub findings")
            return findings[:max_results]
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidAccessException':
                logger.error("Security Hub is not enabled in this region")
                return []
            else:
                logger.error(f"Error retrieving Security Hub findings: {str(e)}")
                return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving findings: {str(e)}")
            return []

    def analyze_finding_with_ai(self, finding: Dict, user_query: str) -> Dict:
        """Use Bedrock to analyze finding and suggest remediation"""
        try:
            # Extract key information from finding
            title = finding.get('Title', 'N/A')
            description = finding.get('Description', 'N/A')
            severity = finding.get('Severity', {}).get('Label', 'N/A')
            compliance_status = finding.get('Compliance', {}).get('Status', 'N/A')
            
            # Get resource information
            resources = finding.get('Resources', [])
            resource_info = []
            for resource in resources[:3]:  # Limit to first 3 resources
                resource_info.append({
                    'id': resource.get('Id', 'N/A'),
                    'type': resource.get('Type', 'N/A'),
                    'region': resource.get('Region', 'N/A')
                })
            
            prompt = f"""You are a security expert analyzing AWS Security Hub findings. Based on the user query and finding details, provide a JSON response with remediation recommendations.

User Query: {user_query}

Finding Details:
- Title: {title}
- Description: {description}
- Severity: {severity}
- Compliance Status: {compliance_status}
- Resources: {json.dumps(resource_info, indent=2)}

Analyze this finding and provide a JSON response with these exact fields:
{{
    "remediation_action": "specific action to take (e.g., 'revoke_sg_rule', 'manual_review', 'update_policy')",
    "ssm_document": "SSM document name if applicable (e.g., 'SecurityHub-RemediateUnrestrictedSSH-{self.environment}') or null",
    "parameters": {{"key": "value pairs needed for remediation"}},
    "explanation": "brief explanation of the issue and fix",
    "severity_assessment": "your assessment of the risk level",
    "automated": true/false whether this can be automatically remediated
}}

Focus on common Security Hub findings like:
- Unrestricted SSH (port 22) access from 0.0.0.0/0
- Unrestricted RDP (port 3389) access from 0.0.0.0/0
- Security group misconfigurations
- IAM policy issues

Only suggest automated remediation for well-defined, low-risk changes."""

            # Call Bedrock
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "temperature": 0.1,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            ai_response = result['content'][0]['text']
            
            # Parse JSON response from AI
            try:
                # Extract JSON from the response (in case there's extra text)
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = ai_response[start_idx:end_idx]
                    analysis = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in AI response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse AI JSON response: {str(e)}")
                analysis = {
                    "remediation_action": "manual_review",
                    "ssm_document": None,
                    "parameters": {},
                    "explanation": f"AI analysis completed but response parsing failed: {ai_response[:200]}...",
                    "severity_assessment": severity,
                    "automated": False
                }
            
            logger.info(f"AI analysis completed for finding: {title}")
            return analysis
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {str(e)}")
            return {
                "remediation_action": "manual_review",
                "ssm_document": None,
                "parameters": {},
                "explanation": f"AI analysis failed due to Bedrock error: {str(e)}",
                "severity_assessment": "unknown",
                "automated": False
            }
        except Exception as e:
            logger.error(f"Unexpected error in AI analysis: {str(e)}")
            return {
                "remediation_action": "manual_review",
                "ssm_document": None,
                "parameters": {},
                "explanation": f"AI analysis failed: {str(e)}",
                "severity_assessment": "unknown",
                "automated": False
            }

    def execute_remediation(self, remediation: Dict, finding: Dict) -> Dict:
        """Execute the suggested remediation using Systems Manager"""
        try:
            ssm_document = remediation.get('ssm_document')
            parameters = remediation.get('parameters', {})
            
            if not ssm_document or not remediation.get('automated', False):
                return {
                    "status": "manual",
                    "message": "This finding requires manual remediation or review"
                }
            
            # Extract resource information for targeting
            resources = finding.get('Resources', [])
            if not resources:
                return {
                    "status": "error",
                    "message": "No resources found in finding for remediation"
                }
            
            # For security group remediations, extract SG ID from resource
            resource_id = resources[0].get('Id', '')
            
            if 'security-group' in resource_id.lower():
                # Extract security group ID (format: arn:aws:ec2:region:account:security-group/sg-xxxxxxxxx)
                sg_id = resource_id.split('/')[-1] if '/' in resource_id else resource_id.split(':')[-1]
                
                if sg_id.startswith('sg-'):
                    parameters['SecurityGroupId'] = sg_id
                    
                    # Execute SSM document
                    response = self.ssm.send_command(
                        DocumentName=ssm_document,
                        Parameters={k: [str(v)] for k, v in parameters.items()},
                        Targets=[{
                            'Key': 'tag:Name',
                            'Values': ['*']
                        }],
                        MaxConcurrency='1',
                        MaxErrors='0'
                    )
                    
                    command_id = response['Command']['CommandId']
                    
                    logger.info(f"Remediation command executed: {command_id} for SG: {sg_id}")
                    
                    return {
                        "status": "success",
                        "command_id": command_id,
                        "message": f"Remediation initiated for security group {sg_id}",
                        "resource_id": sg_id
                    }
            
            return {
                "status": "error",
                "message": f"Unsupported resource type for automated remediation: {resource_id}"
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS API error during remediation: {error_code} - {str(e)}")
            return {
                "status": "error",
                "message": f"Remediation failed: {error_code} - {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during remediation: {str(e)}")
            return {
                "status": "error",
                "message": f"Remediation failed: {str(e)}"
            }

    def process_chat_message(self, message: str) -> Dict:
        """Process user chat message and provide response with remediation actions"""
        try:
            logger.info(f"Processing chat message: {message[:100]}...")
            
            # Get recent findings based on message context
            filters = {}
            if 'critical' in message.lower():
                filters['SeverityLabel'] = [{'Value': 'CRITICAL', 'Comparison': 'EQUALS'}]
            elif 'high' in message.lower():
                filters['SeverityLabel'] = [{'Value': 'HIGH', 'Comparison': 'EQUALS'}]
            
            findings = self.get_security_hub_findings(filters=filters, max_results=5)
            
            if not findings:
                return {
                    "response": "No active Security Hub findings found that match your criteria. This could mean:\n- Security Hub is not enabled in this region\n- No findings match your filter criteria\n- All findings have been resolved",
                    "findings_count": 0,
                    "remediations": []
                }
            
            # Analyze findings with AI
            responses = []
            automated_count = 0
            manual_count = 0
            
            for i, finding in enumerate(findings[:3]):  # Process top 3 findings
                logger.info(f"Analyzing finding {i+1}: {finding.get('Title', 'Unknown')}")
                
                analysis = self.analyze_finding_with_ai(finding, message)
                
                remediation_result = None
                if analysis.get('automated', False) and analysis.get('ssm_document'):
                    remediation_result = self.execute_remediation(analysis, finding)
                    if remediation_result.get('status') == 'success':
                        automated_count += 1
                    else:
                        manual_count += 1
                else:
                    manual_count += 1
                
                responses.append({
                    "finding_id": finding.get('Id', 'unknown'),
                    "finding_title": finding.get('Title', 'Unknown Finding'),
                    "severity": finding.get('Severity', {}).get('Label', 'Unknown'),
                    "analysis": analysis,
                    "execution": remediation_result
                })
            
            # Generate summary response
            summary = f"Analyzed {len(findings)} Security Hub findings. "
            if automated_count > 0:
                summary += f"Automatically remediated {automated_count} findings. "
            if manual_count > 0:
                summary += f"{manual_count} findings require manual review. "
            
            summary += f"\n\nProcessed findings:\n"
            for i, resp in enumerate(responses, 1):
                status = "✅ Auto-remediated" if resp['execution'] and resp['execution'].get('status') == 'success' else "⚠️ Manual review needed"
                summary += f"{i}. {resp['finding_title']} ({resp['severity']}) - {status}\n"
            
            return {
                "response": summary,
                "findings_count": len(findings),
                "remediations": responses,
                "automated_count": automated_count,
                "manual_count": manual_count
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return {
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "findings_count": 0,
                "remediations": [],
                "error": str(e)
            }

def lambda_handler(event, context):
    """Lambda handler for the Security Hub Chatbot"""
    try:
        logger.info(f"Lambda invoked with event: {json.dumps(event, default=str)}")
        
        chatbot = SecurityHubChatbot()
        
        # Extract message from event
        message = event.get('message', 'Show me security findings that need remediation')
        
        # Process the message
        result = chatbot.process_chat_message(message)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error occurred'
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
