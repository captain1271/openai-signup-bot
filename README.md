# openai注册机

## 介绍

协议版本openai注册机。纯接口，不包含浏览器。

## 免责声明

本项目仅供学习交流使用，严禁用于商业用途，否则后果自负。

## 使用方法

### 前置准备

- 一个支持openai注册的域名，比如`example.com`
- 一个支持`catch all`的收件服务，比如cloudflare或者自建的邮箱服务器
- 一个用于接受`catch all`邮件的且支持imap协议的邮箱，比如`outlook`、`gmail`

### 开始使用

1. 配置邮箱  
   配置好你前置准备的域名和邮箱，保证所有openai的邮件都会转发到你的支持imap协议的邮箱中。
2. 克隆本项目

```bash
git clone https://github.com/MagicalMadoka/openai-signup-bot.git

cd openai-signup-bot
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

3. 重命名`config/config.json.example`为`config/config.json`

- `domain`: 必填，你注册用的域名。
- `proxy`: 选填，代理地址。正常的URL格式例如：`http://user:password@123.45.67.89:8080`。
    - 请使用高质量的代理池，可以减少过cf和arkose的麻烦，也会增加获取5刀账号的概率。
    - 请使用支持后端自动轮换ip的代理，可以减少你的麻烦。
- `signupWorkerNum`: 必填，注册线程的个数，根据你代理轮换ip的频率和机器的配置自行决定。
- `emailWorkerNum`: 必填，处理邮件的线程个数，一般和注册线程个数保持一致或略多。
- `emailAddr`: 必填，你的邮箱地址。
- `emailPassword`: 必填，你的邮箱密码，或应用密码。这取决于你的邮箱服务的提供方。
- `emailImapServer`: 必填，你的邮箱的imap服务器地址，一般可以在你邮箱服务的提供方的文档中找到。
- `emailImapPort`: 选填，你的邮箱的imap服务器端口，一般可以在你邮箱服务的提供方的文档中找到。
- `capsolverKey`: 必填，[capsolver](https://dashboard.capsolver.com/passport/register?inviteCode=DcXKh_eA522p)
  的key，用于获取arkose token
- `yesClientKey`: 必填，[yescaptcha](https://yescaptcha.com/i/oFmkQz)的clientKey，用于过邮箱验证的cf
- `cfSolverProxy`:
  必填。过cf时用的代理。格式和要求参考[文档](https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/86409217/CloudFlareTask+CloudFlare5)
  我在调试脚本的时候用的是[okeyproxy](https://www.okeyproxy.com?ref=y6lg9s)。
- `maxSuccessAccounts`: 选填，最多注册成功的账号数，达到此数量脚本会自动停止，-1表示无限制。
- `maxFailureAccounts`: 选填，最多注册失败的账号数，达到此数量脚本会自动停止，-1表示无限制。我建议你最好限制一下。

4. 运行

```bash
python src/main.py
```

注册成功的账号会出现在`data/accounts.txt`中。如果账号被授权了额度。会保存到`data/credit.txt`中。

## 交流沟通

- 本项目相关的讨论请提issue。先点star哦。
- 其他技术交流: [Telegram](https://t.me/+iNf8qQk0KUpkYmEx)
  请注意，这是其他技术交流群，不是项目部署群，也不是答疑群。任何和此项目有关的问题，请提issue，请提issue，请提issue。提之前先点star。

