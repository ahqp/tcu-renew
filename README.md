## これは何をするものか  
東京都市大学図書館の資料の貸出更新を、自動で行ってくれるスクリプトです。  
一日一回定期的に貸出中の資料の一覧を確認しに行き、貸出期限当日の資料があれば自動的に更新処理を行います。  
また、貸出更新を行った場合、あるいはうまくいかなかった場合、LINEで詳細を通知します。  
Herokuに設置して定期実行させる使い方を想定してますが、  
付けっ放しのコンピュータやVPSをお持ちの方はcronなどで定期実行することもできます。  

## 必要のもの  
- LINE アカウント  
- Heroku アカウント  
 どちらも無料で取得可能です。  

## LINE  
まず[LINE Developers](https://developers.line.biz/en/)のページへ行き、プロバイダを選択、または新規作成します。  
続いて、新規チャンネルを作成します。  
今回は一人のユーザにPushメッセージを送信できればいいので、Developer Trialプランを選択してください。  
プロバイダ名、チャンネル名、アプリ名、アプリの説明などは自分で使うだけなので、自分がわかればなんでもいいです。  
登録が完了したら、Botの設定画面から、メッセージ送受信設定の項目にあるアクセストークンと、  
その他の項目にあるYour user IDを確認します。  
アクセストークンは最初は何も表示されていないので、再発行ボタンを押してください。  
それから、QRコードを読み込んでBOTを友達追加しておいてください。  

## Herokuの準備をする前に  
続いて、このリポジトリをクローンしてください。  
`git clone https://github.com/ahqp/tcu-renew.git`  

## Heroku
[Heroku](https://www.heroku.com/)アカウントを取得し、[Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)をインストールしてください。  
コランドラインからherokuにログインします。  
```
heroku login
heroku create
```
次に、chromedriverとgoogle chromeのbuildpackを追加します。  
```
heroku buildpacks:set https://github.com/heroku/heroku-buildpack-chromedriver.git
heroku buildpacks:set https://github.com/heroku/heroku-buildpack-google-chrome.git
```
heroku appに tcu-renewのファイルを追加します。  
```
git add renew.py
git add requirements.txt
git commit -m "Initial Commit"
git push heroku master
```
LINEのアクセストークン、Your user ID、大学アカウントのIDとパスワードを環境変数を設定します。  
```
heroku config:set LINE_TOKEN=""
heroku config:set LINE_USER_ID=""
heroku config:set TCU_USER_ID=""
heroku config:set TCU_PASSWORD=""
```
<!--
ここまできたら設置したheroku app を試しに実行してみましょう  
`heroku run -a python renew.py ` )
実行がうまくいっていれば、
-->
定期実行のためのアドオンを追加します。 
`heroku addons:add scheduler:standard`  

あとはHerokuコンソールからAdd new jobを選択して  
`python renew.py`  
を登録してください。  

一日一回実行したいので、FrequencyはDailyに指定。  
next due はUTCなので設定したい日本時間-9:00としなければいけません。  
私の場合は午前1:00に実行したいので、16:00に設定しています。  

## Support Me  
[IssueHunt](https://issuehunt.io/repos/160844308)  
## 大学図書館関係者各位へ  
このスクリプトは、できるだけシステムに負荷をかけないように書いたつもりです。  
もし、このスクリプトに対し、多くの利用者が不便を感じてしまうような対処をなされるくらいなら、事前にご相談ください。  
そのような事態は私の本意ではありません。  

# 最後に、一番大切なこと

期限まで余裕があっても、利用が終わった資料は速やかに図書館に返却してください。  
たとえ予約が入っていなくても、その資料が本棚に無いことは他の利用者にとって損失になります。  
