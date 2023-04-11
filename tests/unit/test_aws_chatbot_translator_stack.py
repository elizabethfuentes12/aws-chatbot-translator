import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_chatbot_translator.aws_chatbot_translator_stack import AwsChatbotTranslatorStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_chatbot_translator/aws_chatbot_translator_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsChatbotTranslatorStack(app, "aws-chatbot-translator")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
