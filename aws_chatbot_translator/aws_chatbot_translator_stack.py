from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_lex as lex,
    aws_s3 as s3,
    aws_lambda,
    aws_iam,
    aws_logs as logs,
    # aws_sqs as sqs,
)

from constructs import Construct
#from chatbot_code import (LexBotV2, LexBotV2Multi, S3BotFiles)


class AwsChatbotTranslatorStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)
        account_id = stk.account

        REGION_NAME = self.region
        REGION_ENDPOINT = you_endpoint_region

        endpoint_text_to_text = your_text_to_text_endpoint
        endpoint_text_to_image = your_text_to_image_endpoint
        bucket_name = your_bucket_name
    
    
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ The Lambda function invokes Amazon Comprehend for detect Languages +++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_chatbot_build_on = aws_lambda.Function(self, "lambda_chatbot_translator",
                                            handler = "lambda_function.lambda_handler",
                                            timeout = Duration.seconds(300),
                                            runtime = aws_lambda.Runtime.PYTHON_3_9,
                                            memory_size = 256, description = "Translate using Amazon Translate creating audio with Amazon Polly to LexChatBot",
                                            code = aws_lambda.Code.from_asset("./lambdas/chatbot_translator"),
                                            environment = {
                                                'ENV_REGION_NAME'  : REGION_NAME,
                                                "ENV_S3_BUCKET_NAME" : bucket_name,
                                                }
                                                
                                            )

        lambda_chatbot_build_on.add_to_role_policy(
            aws_iam.PolicyStatement(
                        actions=["translate:TranslateText","comprehend:DetectDominantLanguage","polly:StartSpeechSynthesisTask","polly:GetSpeechSynthesisTask"], 
                        resources=['*'])
                    )
        
        lambda_chatbot_build_on.add_to_role_policy(aws_iam.PolicyStatement(
            actions=[
				"s3:PutObject",
				"s3:GetObject"
			],resources=[f"arn:aws:s3:::{bucket_name}/*",f"arn:aws:s3:::{bucket_name}"
			])
        )
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ Query for summary and to create great images  +++++++++++++++
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_smart_chatbot = aws_lambda.Function(self, "lambda_smart_chatbot",
                                            handler = "lambda_function.lambda_handler",
                                            timeout = Duration.seconds(300),
                                            runtime = aws_lambda.Runtime.PYTHON_3_9,
                                            memory_size = 256, description = "Query for summary and to create great images",
                                            code = aws_lambda.Code.from_asset("./lambdas/smart_chatbot"),
                                            environment = {
                                                'ENV_REGION_NAME'  : REGION_NAME,
                                                "ENV_REGION_ENDPOINT" : REGION_ENDPOINT,
                                                "ENV_ENDPOINT_TEXT_TO_TEXT" : endpoint_text_to_text,
                                                "ENV_ENDPOINT_TEXT_TO_IMAGE" : endpoint_text_to_image,
                                                "ENV_BUCKET_NAME" : bucket_name
                                                }
                                                
                                            )

        lambda_smart_chatbot.add_to_role_policy(
            aws_iam.PolicyStatement(
                        actions=["translate:TranslateText","comprehend:DetectDominantLanguage"], 
                        resources=['*'])
                    )
        
        lambda_smart_chatbot.add_to_role_policy(aws_iam.PolicyStatement(
            actions=["sagemaker:InvokeEndpoint"],resources=[f"arn:aws:sagemaker:{REGION_ENDPOINT}:{account_id}:endpoint/{endpoint_text_to_text}"])
        )
        lambda_smart_chatbot.add_to_role_policy(aws_iam.PolicyStatement(
            actions=["sagemaker:InvokeEndpoint"],resources=[f"arn:aws:sagemaker:{REGION_ENDPOINT}:{account_id}:endpoint/{endpoint_text_to_image}"])
        )

        lambda_smart_chatbot.add_to_role_policy(aws_iam.PolicyStatement(
            actions=[
				"s3:PutObject",
				"s3:GetObject"
			],resources=[f"arn:aws:s3:::{bucket_name}/*",f"arn:aws:s3:::{bucket_name}"
			]))


