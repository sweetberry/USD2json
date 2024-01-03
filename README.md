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
# app ファイルが作成されます。
pipenv run makeApp
```
# Usage

- アプリのウインドウにUSDファイルをドロップ。  
- 書き出したいカメラやXFormを選択し、
- Exportを押してください。  
- .jsonファイルが書き出されます。

# Author

* pixel@sweetberry.com

# License

[MIT license](https://en.wikipedia.org/wiki/MIT_License).
