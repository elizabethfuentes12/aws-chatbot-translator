import sys

from aws_cdk import (
    Duration,
    aws_lambda,
    aws_ssm as ssm,
    aws_iam as iam, 
    Stack

)

from constructs import Construct

from layers import (Pillow)


LAMBDA_TIMEOUT= 60

BASE_LAMBDA_CONFIG = dict (
    timeout=Duration.seconds(LAMBDA_TIMEOUT),       
    memory_size=256,
    tracing= aws_lambda.Tracing.ACTIVE)

COMMON_LAMBDA_CONF = dict (runtime=aws_lambda.Runtime.PYTHON_3_8, **BASE_LAMBDA_CONFIG)


class Lambdas(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pil = Pillow(self, 'PilLay')

        common = aws_lambda.LayerVersion(
            self, "common-layer", code=aws_lambda.Code.from_asset("./layers/common/"),
            compatible_runtimes = [aws_lambda.Runtime.PYTHON_3_8,aws_lambda.Runtime.PYTHON_3_9], 
            description = 'librerias adicionales', layer_version_name = "librerias-adicionales"
        )
        
        self.common = common

        self.chatbot_translator_hook = aws_lambda.Function(
            self, "chatbot_translator_hook", handler="lambda_function.lambda_handler",
            description = "Translate using Amazon Translate creating audio with Amazon Polly to LexChatBot",
            code=aws_lambda.Code.from_asset("./lambdas/code/chatbot_translator"),
            layers= [common, pil.layer],
            **COMMON_LAMBDA_CONF)
        
        
        self.cool_image_hook = aws_lambda.Function(
            self, "cool_image_hook", handler="lambda_function.lambda_handler",
            description = "Esta Lambda maneja la convesación del bot Cool Image de Amazon Lex, traduce con Amazon Translate e invoca el endopoint de Amazon SageMaker",
            code=aws_lambda.Code.from_asset("./lambdas/code/cool_image"),
            layers= [common, pil.layer],
            **COMMON_LAMBDA_CONF)

    
        
        
        
        
        
       
