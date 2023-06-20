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
    
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ The Lambda function invokes Amazon Comprehend for detect Languages +++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_chatbot_translator = aws_lambda.Function(self, "lambda_chatbot_translator",
                                            handler = "lambda_function.lambda_handler",
                                            timeout = Duration.seconds(300),
                                            runtime = aws_lambda.Runtime.PYTHON_3_9,
                                            memory_size = 256, description = "Translate using Amazon Translate creating audio with Amazon Polly to LexChatBot",
                                            code = aws_lambda.Code.from_asset("./lambdas"),
                                            environment = {
                                                'ENV_REGION_NAME'  : REGION_NAME,

                                                }
                                                
                                            )

        lambda_chatbot_translator.add_to_role_policy(
            aws_iam.PolicyStatement(
                        actions=["translate:TranslateText","comprehend:DetectDominantLanguage"], 
                        resources=['*'])
                    )

