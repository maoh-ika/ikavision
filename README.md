# IkaVision
スプラトゥーン3のバトル動画解析システムです。

## ウェブサイト
[IkaVision試験版](https://ikavision.ikaruga.app/)

## システム構成
IkaVisionは、大きく以下の4つのコンポーネントで構成されています。  
<br/>
**1. バトル動画配信モニター**
<br/>
動画配信プラットフォームで公開されたスプラトゥーン3のバトル動画を検出し、プラットフォームが提供する手段によって動画データを収集します。  
<br/>
**2. バトル動画アナライザー**
<br/>
バトル動画の内容をAIで解析し、バトルごとにルール、ステージ、ブキ編成、XPレート帯、キル、デスなどの情報を抽出します。  
<br/>
**3. バトルデータベース**
<br/>
バトル動画アナライザーが抽出したデータを、検索しやすい形式でデータベース化します。  
<br/>
**4. IkaVisionウェブサイト**
<br/>
バトルデータベースに蓄積したデータを使用し、見たい条件の組み合わせを指定してバトルを検索する機能や、スプラトゥーン3の最新バトル環境の情報を提供します。
