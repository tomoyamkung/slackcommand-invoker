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
