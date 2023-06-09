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

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ The Amazon S3 bucket will be created ++++++++++++++++
        #+++++ where the file that forms the chatbot will be saved.++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        BUCKET_NAME       = "demo-eli"
        bueket_key = "traductor_polly/"
      
        #chatbot_bucket = s3.Bucket(self, BUCKET_NAME ,  versioned=False, removal_policy=RemovalPolicy.DESTROY)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ The Lambda function invokes Amazon Comprehend for detect Languages +++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        requests_layer = aws_lambda.LayerVersion(self, "requestsLayer",
                                                 code = aws_lambda.AssetCode("layers/requests"),
                                                 compatible_runtimes = [aws_lambda.Runtime.PYTHON_3_9])

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ The Lambda function invokes Amazon Comprehend for detect Languages +++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_chatbot_translator = aws_lambda.Function(self, "lambda_chatbot_translator",
                                            handler = "lambda_function.lambda_handler",
                                            timeout = Duration.seconds(300),
                                            runtime = aws_lambda.Runtime.PYTHON_3_9,
                                            memory_size = 256, description = "Translate using Amazon Translate creating audio with Amazon Polly to LexChatBot",
                                            code = aws_lambda.Code.from_asset("./lambdas/chatbot-translate-polly"),
                                            layers = [requests],
                                            environment = {
                                                'ENV_REGION_NAME'  : REGION_NAME,
                                                'BUCKET_NAME'  : BUCKET_NAME,
                                                'BUCKET_KEY'  : bueket_key,

                                                }
                                                
                                            )

        lambda_chatbot_translator.add_to_role_policy(
            aws_iam.PolicyStatement(
                        actions=["translate:*","polly:*","comprehend:*"], 
                        resources=['*'])
                    )
        
        lambda_chatbot_translator.add_to_role_policy(
            aws_iam.PolicyStatement(
                        actions=["s3:PutObject","s3:GetObject"], 
                        resources=[f'arn:aws:s3:::{BUCKET_NAME}'.format(BUCKET_NAME),f"arn:aws:s3:::{BUCKET_NAME}/*".format(BUCKET_NAME)])
                    )
                

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++++++++++++++++++++++++++ Amazon Lex ChatBot +++++++++++++++++++++++++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        #bot_confirmar = LexBotV2(self, "BotTraductor", "Traductor", lambda_init.code_hook_confirmar, "Traductor.zip", _bot_files)

        # example resource
        # queue = sqs.Queue(
        #     self, "AwsChatbotTranslatorQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
