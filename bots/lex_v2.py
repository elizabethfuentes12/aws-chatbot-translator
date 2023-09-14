import aws_cdk.aws_lex as lex
from constructs import Construct
from aws_cdk import ( 
    CfnTag,  
    Stack,
    aws_iam as iam,
)


data_privacy = {'ChildDirected': False}
sentiment_analysis_settings = {'DetectSentiment': False}
idle_session_ttl_in_seconds = 120

from bots.lex_v2_cloudwatch_logs import CWLogGroup
from bots.lex_v2_role import LexV2Role



class LexBotV2(Construct):
    def __init__(self, scope: Construct, id: str, bot_name, code_hook, bot_zip, s3_bots, bot_locales,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        bot_role = LexV2Role(self, 'SLRLexV2', bot_name)
        log_group = CWLogGroup(self, "logGroup", log_group_name = bot_name)


        code_hook_specification=lex.CfnBot.CodeHookSpecificationProperty(
            lambda_code_hook=lex.CfnBot.LambdaCodeHookProperty(
                code_hook_interface_version="1.0",
                lambda_arn=code_hook.function_arn
            )
        )
        bot_alias_locale_setting=lex.CfnBot.BotAliasLocaleSettingsProperty(
            enabled=True, code_hook_specification=code_hook_specification
        )

        conversation_log_settings=lex.CfnBot.ConversationLogSettingsProperty(
            audio_log_settings=[lex.CfnBot.AudioLogSettingProperty(
                destination=lex.CfnBot.AudioLogDestinationProperty(
                    s3_bucket=lex.CfnBot.S3BucketLogDestinationProperty(
                        log_prefix=f"{bot_name}/audios",
                        s3_bucket_arn=s3_bots.bucket.bucket_arn,
                    )
                ),
                enabled=True
            )],
            text_log_settings=[lex.CfnBot.TextLogSettingProperty(
                destination=lex.CfnBot.TextLogDestinationProperty(
                    cloud_watch=lex.CfnBot.CloudWatchLogGroupLogDestinationProperty(
                        cloud_watch_log_group_arn=log_group.log_grop.log_group_arn,
                        log_prefix=f"{bot_name}/text"
                    )
                ),
                enabled=True
            )]
        )


        bot_locale_settings_list = [
            lex.CfnBot.BotAliasLocaleSettingsItemProperty(bot_alias_locale_setting= bot_alias_locale_setting, locale_id=loc) 
            for loc in bot_locales
        ]


        cfn_bot = lex.CfnBot(self, "CfnBot",
            data_privacy = data_privacy,
            idle_session_ttl_in_seconds = idle_session_ttl_in_seconds,
            name=bot_name,
            role_arn=bot_role.arn,
            bot_file_s3_location=lex.CfnBot.S3LocationProperty(
                s3_bucket=s3_bots.s3deploy.deployed_bucket.bucket_name,
                s3_object_key=f'bot_files/{bot_zip}'),
            auto_build_bot_locales=True,
            description="Cool Image is a chatbot that receives instructions in any language to generate images using the stable diffusion 2.1 model (activate it by saying cool image)" ,
            test_bot_alias_settings=lex.CfnBot.TestBotAliasSettingsProperty(
                
                bot_alias_locale_settings= bot_locale_settings_list,
                conversation_log_settings = conversation_log_settings,
                sentiment_analysis_settings=sentiment_analysis_settings
            )
        )


        code_hook.add_permission(
            principal=iam.ServicePrincipal("lexv2.amazonaws.com"),id=f"{bot_name}-invoke",
            action='lambda:InvokeFunction', source_arn = f"arn:aws:lex:{Stack.of(self).region}:{Stack.of(self).account}:bot-alias/*"
            )

        
        cfn_bot.node.add_dependency(bot_role.role)
        cfn_bot.node.add_dependency(s3_bots.s3deploy.deployed_bucket)



        self.bot = cfn_bot