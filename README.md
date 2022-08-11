# slackcommand-invoker

## Purpose / 目的

Slack のスラッシュコマンドと連携して AWS Lambda を実行する基盤プログラム。

Slack 側のタイムアウトは 3 秒しかないため、少しでも時間がかかる処理はタイムアウトとなってしまう。
本プログラムでは、Lambda から Lambda を呼び出す部分を提供し、実際の処理は別の Lambda が対応する想定とする。

トピックスは以下の通り。

- Slack のスラッシュコマンドから Lambda を実行する
- 呼び出された Lambda から別の Lambda を起動する

## Advance preparation / 事前準備

### Install the AWS CLI / AWS CLI をインストールしておく

The installation method is optional. a Docker image is also acceptable.

インストール方法は任意。Docker イメージでも構わない。

```sh
➜  aws --version
aws-cli/2.4.29 Python/3.9.12 Darwin/19.6.0 source/x86_64 prompt/off
```

### Install the AWS SAM CLI / AWS SAM CLI をインストールしておく

Install AWS SAM CLI referring to the following.

- https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html

https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html を参考に AWS SAM CLI をインストールする。

### Register a profile / プロファイルを登録しておく

Register a profile using IAM credentials.csv.
Specify this profile as an option to the command.

IAM の credentials.csv を使用してプロファイルを登録する。
このプロファイルをコマンドのオプションに指定する。

## Deployment to AWS Lambda / デプロイ

First, prepare template.yaml.

まず template.yaml を準備する。

1. Now that you have template.yaml.sample, copy it with the filename template.yaml / template.yaml.sample を用意したので、それを template.yaml のファイル名でコピーする
2. There are three "TBD" in template.yaml, so modify the contents to suit each environment / template.yaml に "TBD" が3箇所あるので、各環境に即した内容で修正する

```sh
➜  cp template.yaml.sample template.yaml
➜  vim template.yaml
```

Next, build the project.

次にプロジェクトをビルドする。

```sh
➜  sam build
```

Finally, deploy to AWS.
The `--guided` option should be specified for the first deployment; the samconfig.toml file will be created, so you do not need to specify the `--guided` option for the second and subsequent deployments.

最後に AWS へデプロイする。
初回デプロイ時は `--guided` オプションを付ける。samconfig.toml ファイルが作成されるため、2回目以降は `--guided` オプションを指定しなくて良い。


```sh
➜  sam deploy --profile PROFILE --guided  # first deployment
➜  sam deploy --profile PROFILE
```

## 開発

パッケージや VirtualEnv の管理に Pipenv を、ユニットテストや Lint チェックの実行に tox を使用している。

ユニットテストの実行や Lint チェックを実行する場合は `pipenv shell` として仮想環境にログインする。

```sh
➜  pipenv shell
Launching subshell in virtual environment...
 . /path/to/.local/share/virtualenvs/slackcommand-invoker-2cy1skFo/bin/activate
```

ユニットテストだけを実行する場合は `tox -e py39` を実行する。

```sh
➜  tox -e py39
py39 installed: attrs==22.1.0,boto3==1.24.49,botocore==1.27.49,iniconfig==1.1.1,jmespath==1.0.1,packaging==21.3,pluggy==1.0.0,py==1.11.0,pyparsing==3.0.9,pytest==7.1.2,python-dateutil==2.8.2,s3transfer==0.6.0,six==1.16.0,tomli==2.0.1,urllib3==1.26.11
py39 run-test-pre: PYTHONHASHSEED='492914414'
py39 run-test: commands[0] | pytest -rsfp
============================================================== test session starts ===============================================================
platform darwin -- Python 3.9.12, pytest-7.1.2, pluggy-1.0.0
cachedir: .tox/py39/.pytest_cache
rootdir: /path/to/slackcommand-invoker
collected 4 items

tests/test_lambda_function.py ....                                                                                                         [100%]

============================================================ short test summary info =============================================================
PASSED tests/test_lambda_function.py::test_parse_params[None-None]
PASSED tests/test_lambda_function.py::test_parse_params[-None]
PASSED tests/test_lambda_function.py::test_parse_params[text=a-expected2]
PASSED tests/test_lambda_function.py::test_parse_params[text=a b-expected3]
=============================================================== 4 passed in 0.14s ================================================================
____________________________________________________________________ summary _____________________________________________________________________
  py39: commands succeeded
  congratulations :)
```

Lint チェックだけを実行する場合は `tox -e lint` を実行する。

```sh
➜  tox -e lint
lint installed: black==22.6.0,click==8.1.3,flake8==5.0.4,flake8-blind-except==0.2.1,flake8-docstrings==1.6.0,flake8-import-order==0.18.1,isort==5.10.1,mccabe==0.7.0,mypy==0.971,mypy-extensions==0.4.3,pathspec==0.9.0,platformdirs==2.5.2,pycodestyle==2.9.1,pydocstyle==6.1.1,pyflakes==2.5.0,snowballstemmer==2.2.0,tomli==2.0.1,typing_extensions==4.3.0
lint run-test-pre: PYTHONHASHSEED='2466430279'
lint run-test: commands[0] | isort .
Skipped 4 files
lint run-test: commands[1] | black .
All done! ✨ 🍰 ✨
4 files left unchanged.
lint run-test: commands[2] | flake8 .
lint run-test: commands[3] | mypy .
Success: no issues found in 4 source files
____________________________________________________________________ summary _____________________________________________________________________
  lint: commands succeeded
  congratulations :)
```

ユニットテストも Lint チェックも実行したい場合は `tox` とする。

## 備考

### Slack のスラッシュコマンドを実行すると dispatch_failed となる事象の対応

原因はロールにエンティティが不足していたためだった。
具体的には以下の apigateway.amazonaws.com の部分が不足していたので dispatch_failed となっていた。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "apigateway.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

以下の内容で整理した。

- Lambda を実行するので AWSLambdaExecute が必要
- Lambda の送信先が Lambda なので InvokeFunction が必要
- API Gateway から Lambda を呼び出すので apigateway.amazonaws.com が必要

具体的なテンプレートは template.yaml.sample の `LambdaRole` に定義してある。

### API Gateway のマッピングテンプレートについて

API Gateway の統合リクエストの設定に「Lambda プロキシ統合の使用」がある。
これはチェックを付ける。

以前は、チェックを外して Content-Type を `application/x-www-form-urlencoded` で受け取るようにマッピングテンプレートを適用したが、現在は不要となっている。
