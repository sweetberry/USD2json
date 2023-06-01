# USD2json

USD ファイルから Camera や Xform を JSON 形式で書き出すためのアプリです。  
AfterEffects でカメラやヌルの Import&Export のために作成しました。

# Requirement

* Python >=3.6, <3.11
* usd-core
* tkinterdnd2

* pipenv

# Installation

```bash
# pipenv を導入済みであれば必要ありません。
pip install pipenv
```
```bash
pipenv install
```

- for OSX
```bash
pipenv run makeCommand
# usd2json.command ファイルが作成されダブルクリックで起動します。
```
# Usage

DEMOの実行方法など、"hoge"の基本的な使い方を説明する

```bash
git clone https://github.com/hoge/~
cd examples
python demo.py
```

# Note

現状 OSX 環境下で pyinnstaller での app 化がうまくいかない状況です。  
( pxr モジュール使用時に Segmentation fault: 11 で落ちる)  
その回避策として .command ファイルを作成しています。

もし上手くapp化できた方がおられましたらご一報ください。

# Author

* pixel@sweetberry.com

# License

[MIT license](https://en.wikipedia.org/wiki/MIT_License).
