# realtime-stable-diffusion_Docker



# はじめに

**realtime-stable-diffusion** はリアルタイムでお絵描きができるツールです。このガイドでは、Dockerを使ってこのツールをセットアップし、使い始める方法を説明します。
## 必要なもの
- Dockerがインストールされたコンピューター
- 基本的なコマンドラインの知識

解説記事はこちら

https://hamaruki.com/real-time-drawing-tool-realtime-stable-diffusion_docker-setup-guide/

## セットアップ手順
### Step 1: プロジェクトのクローン

まず、GitHubからrealtime-stable-diffusionのリポジトリをクローンします。これには以下のコマンドを使用します。

```bash
git clone https://github.com/Sunwood-ai-labs/realtime-stable-diffusion_Docker.git
cd realtime-stable-diffusion
```


### Step 2: Dockerファイルの確認

次に、Dockerファイルを確認します。このファイルは、realtime-stable-diffusionを実行するために必要な環境を設定します。 
- `Dockerfile`と`docker-compose.yml`が含まれていることを確認してください。
### Step 3: Dockerコンテナのビルドと起動

以下のコマンドを使用してDockerコンテナをビルドし、起動します。

```bash
docker-compose up
```



このコマンドを実行すると、Dockerが必要なイメージをビルドし、アプリケーションを起動します。正常に起動すると、以下のようなメッセージが表示されます。

```csharp
realtime-stable-diffusion_docker-realtime-stable-diffusion-1  | Running on local URL:  http://127.0.0.1:7860
realtime-stable-diffusion_docker-realtime-stable-diffusion-1  | Running on public URL: https://[ランダムなURL].gradio.live
```


### Step 4: アプリケーションのアクセス

アプリケーションが起動したら、ブラウザを開いて表示されたローカルURLにアクセスします。

これで、realtime-stable-diffusionを使ってリアルタイムでお絵描きを楽しむことができます。

![](https://github.com/Sunwood-ai-labs/realtime-stable-diffusion_Docker/blob/main/image/screenshot.png)


## メンテナンス用コマンド

```
docker-compose exec realtime-stable-diffusion /bin/bash
```