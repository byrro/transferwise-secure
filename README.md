
# Transferwise Secure

Track debit transactions in your Transferwise account and receive SMS alerts for early fraud-detection and financial loss mitigation.

[![Test Framework](https://img.shields.io/badge/testing-pytest-green)](https://github.com/pytest-dev/pytest/)
![Test Coverage](https://raw.githubusercontent.com/byrro/transferwise-secure/main/coverage.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code Style](https://img.shields.io/badge/code%20style-PEP8-lightgrey)](https://github.com/hhatto/autopep8/)
[![Code Formatter](https://img.shields.io/badge/formatter-autopep8-lightgrey)](https://github.com/hhatto/autopep8/)

---

## Built with

### [Python 3](https://python.org)

![Python Logo](https://logo.clearbit.com/python.org?size=50)

### [Transferwise](https://transferwise.com) API

![Transferwise Logo](https://logo.clearbit.com/transferwise.com?size=50)

### [Twilio](https://twilio.com)

![Twilio Logo](https://logo.clearbit.com/twilio.com?size=50)

### AWS [Lambda](https://aws.amazon.com/lambda) & [DynamoDB](https://aws.amazon.com/dynamodb)

![AWS Logo](https://logo.clearbit.com/amazonaws.com?size=50)



## Requirements

- Obviously, a [Transferwise account](https://transferwise.com/register/)
- [Twilio account](https://www.twilio.com/try) a phone number for sending SMS
- [AWS account](https://aws.amazon.com/) (free tier should easily cover your needs here)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed in your computer (works on Linux, MacOS and Windows)

## Deployment instructions

1. Fork and/or clone the repo and enter the twsecure directory: `cd twsecure`
1. Build the local images and dependencies: `sam build`
1. Deploy in your AWS account `sam deploy --guided`

Open an [issue](https://github.com/byrro/transferwise-secure/issues) if you have any trouble, but it should be straightforward.

Below is a list of parameters the deployment process will prompt for in the command line. Do not quote or double-quote strings when entering the data.

- **Stack Name**: identify the AWS stack (e.g. "transferwise-monitor"), choose at your own discretion
- **AWS Region**: e.g. "us-east-1"
- **TransferwiseApiToken**: see [instructions](https://transferwise.com/help/articles/2958107/how-can-my-business-use-the-transferwise-api) to get your Transferwise token
- **SendSmsToPhoneNumber**: this is the phone number where you want to receive debit alert messages
- **TwilioPhoneNumber**: your Twilio number (from which messages will be sent), you can [get a trial](https://www.twilio.com/try-twilio) Twilio number for free, [follow these instructions](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account)
- **TwilioAccountId**: available in your [account console](https://www.twilio.com/console)
- **TwilioApiToken**: also available in your [account console](https://www.twilio.com/console)
- **TimeDeltaUnit**: units of time to look for latest statements when scanning - **Transferwise API, recommended is "hours" *
- **TimeDeltaValue**: recommended is "24" *
- **Confirm changes before deploy**: N
- **Allow SAM CLI IAM Role creation**: Y
- **Save arguments to configuration file**: N (setting this to Y will simplify subsequent re-deployments - if you run any - but will store your API secrets in plain text, so be careful)
- **SAM configuration file**: just hit ENTER to go with default
- **SAM configuration environment**: just hit ENTER to go with default

_* A temporary local memory avoids missing transactions and double-alerting. The 24-hour time frame is a reasonable cushion for API downtimes, or even clock mismatches. You can get extra cautious here and go with 48 or even 72 hours here._
