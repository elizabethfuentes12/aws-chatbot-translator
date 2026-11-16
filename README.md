# ⚠ This repository is deprecated

> **Finished version available:** this repo was the working draft of the "cool image" Lex bot. The complete, documented version (CDK stack, SageMaker/Lex/Translate wiring, React front end) lives in:
>
> **[de-la-mente-a-la-pantalla](https://github.com/elizabethfuentes12/de-la-mente-a-la-pantalla)**

This repository is no longer maintained. The CDK stack here does not synthesize as-is (`aws_chatbot_translator_stack.py` has placeholders for `endpoint_text_to_image`, `bucket_name` and `distribution_name` that must be filled in), it targets the deprecated `python3.8` Lambda runtime and `aws-cdk-lib` 2.50.0. Use the repository above instead.

---

# Create your own chatbot! 

Deploy the CDK for AWS lambdas functions and create the Amazon lex Chatbot [Importing](https://docs.aws.amazon.com/lexv2/latest/dg/import-console.html) the [].zip files](https://github.com/elizabethfuentes12/aws-chatbot-translator/tree/master/aws_chatbot_translator/chatbots)

This (repo)[https://github.com/aws-samples/aws-lex-web-ui] provides a chatbot UI which you can deploy using the [AWS CloudFormation](https://aws.amazon.com/es/cloudformation/) templates


# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
