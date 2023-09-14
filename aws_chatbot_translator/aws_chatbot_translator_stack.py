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
from lambdas import Lambdas #Para desplegar la Funcion Lambda
from bots import LexBotV2, S3BotFiles #Para desplegar el bot de Amazon Lex

#from chatbot_code import (LexBotV2, LexBotV2Multi, S3BotFiles)


class AwsChatbotTranslatorStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)
        account_id = stk.account
        Fn  = Lambdas(self,'Fn')

        REGION_NAME = self.region

        REGION_ENDPOINT = self.region

        endpoint_text_to_image =
        bucket_name = 
        distribution_name = 


    
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ The Lambda function invokes Amazon Comprehend for detect Languages +++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_hook_translate = Fn.chatbot_translator_hook

        lambda_hook_translate.add_environment(key='ENV_BUCKET_NAME', value= bucket_name)
        lambda_hook_translate.add_environment(key='ENV_DISTRIBUTION_NAME', value= distribution_name)


        lambda_hook_translate.add_to_role_policy(
            aws_iam.PolicyStatement(
                        actions=["translate:TranslateText","comprehend:DetectDominantLanguage","polly:StartSpeechSynthesisTask","polly:GetSpeechSynthesisTask"], 
                        resources=['*'])
                    )
        
        lambda_hook_translate.add_to_role_policy(aws_iam.PolicyStatement(
            actions=[
				"s3:PutObject",
				"s3:GetObject"
			],resources=[f"arn:aws:s3:::{bucket_name}/*",f"arn:aws:s3:::{bucket_name}"
			])
        )

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ Query for summary and to create great images  +++++++++++++++
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


        lambda_hook_image = Fn.cool_image_hook

        lambda_hook_image.add_environment(key='ENV_ENDPOINT_TEXT_TO_IMAGE', value= endpoint_text_to_image)
        lambda_hook_image.add_environment(key='ENV_BUCKET_NAME', value= bucket_name)
        lambda_hook_image.add_environment(key='ENV_DISTRIBUTION_NAME', value= distribution_name)
        lambda_hook_image.add_environment(key='REGION_ENDPOINT', value= REGION_ENDPOINT)


        lambda_hook_image.add_to_role_policy(
            aws_iam.PolicyStatement(
                        actions=["translate:TranslateText","comprehend:DetectDominantLanguage"], 
                        resources=['*'])
                    )
        
        lambda_hook_image.add_to_role_policy(aws_iam.PolicyStatement(
            actions=["sagemaker:InvokeEndpoint"],resources=[f"arn:aws:sagemaker:{REGION_ENDPOINT}:{account_id}:endpoint/{endpoint_text_to_image}"])
        )

        lambda_hook_image.add_to_role_policy(aws_iam.PolicyStatement(
            actions=[
				"s3:PutObject",
				"s3:GetObject"
			],resources=[f"arn:aws:s3:::{bucket_name}/*",f"arn:aws:s3:::{bucket_name}"
			]))
        
        #+++++++++++++++++++++++++++++++++++++
        #++++ Desplegar el bot y permisos ++++
        #+++++++++++++++++++++++++++++++++++++

        bot_language = ["en_US"]
        bot_zip_file =  "demo-cool-image-LexJson.zip"
        bot_name = "cool-image-bot"

        _bot_files = S3BotFiles(self, "Files", "./bots/bot_files")
        demo_bot = LexBotV2(self, "Bot", bot_name, lambda_hook_image, bot_zip_file, _bot_files, bot_language)
    
        bot_zip_file_2 =  "demo-chatbot-traductor-LexJson.zip"
        bot_name_2 = "chatbot-traductor"

        _bot_files_2 = S3BotFiles(self, "Files_2", "./bots/bot_files")
        demo_bot_2 = LexBotV2(self, "Bot_2", bot_name_2, lambda_hook_translate, bot_zip_file_2, _bot_files_2, bot_language)
             


