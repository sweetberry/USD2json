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
# プロジェクトの初期化
pipenv --python 3.10

# パッケージのインストール
pipenv install

# アプリが起動します。
pipenv run app

```


- for Windows 
```bash
# exe ファイルが作成されます。
pipenv run makeExe
```

- for OSX
```bash
# usd2json.command ファイルが作成されダブルクリックで起動します。
pipenv run makeCommand
```
# Usage

- アプリのウインドウにUSDファイルをドロップ。  
- 書き出したいカメラやXFormを選択し、
- Exportを押してください。  
- .jsonファイルが書き出されます。


# Note

現状 OSX 環境下で pyinnstaller での app 化がうまくいかない状況です。  
( pxr モジュール使用時に Segmentation fault: 11 で落ちる)  
その回避策として .command ファイルを作成しています。

もし上手くapp化できた方がおられましたらご一報ください。

# Author

* pixel@sweetberry.com

# License

[MIT license](https://en.wikipedia.org/wiki/MIT_License).
