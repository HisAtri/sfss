# SFSS - Secure File Storage Service
Secure File Storage Service

**你真的需要使用对象存储来保存文件吗？**

## 使用阿里云OSS的利与弊

### 优点
- S3兼容，阿里云OSS可以在大多数S3兼容的应用中使用
- 直链，允许公网直链访问

### 缺点
- 安全性，存在流量盗刷、秘钥泄漏等安全问题。
- 成本，OSS本身的存储成本就不低，流量和https请求数都是额外计费项目。虽然可以通过CDN来降低流量成本，但是CDN的成本也不低。
- 性能，OSS的带宽和IOPS都不高。

## 你真的需要使用OSS吗？

### 替代方案
- 云盘存储，例如百度网盘。尽管百度网盘的速度为人诟病，但是在没有S3API需求的情况下，它的存储成本和流量成本都远远低于OSS；更何况免费用户也有2T的存储空间。
- 自建NAS，如果有公网IP，那么你完全可以使用它来搭建一个NAS，这样你就可以在家里、公司、学校等地方访问你的文件了。

#### 实际场景

如果你的文件较为重要，那么你应当使用多端备份以提高安全性。

例如，可以使用百度网盘的免费2TB空间，以及其他网盘的免费空间作为冷备份，使用本地存储或者NAS存储和热更新数据。

如果没有公网IP，那么你可以选择以下方式，使你的文件可以在任何地方访问：
- FRP内网穿透服务，例如Natapp等。
- 使用自有的VPS搭建FRP/Ngrok服务。
- 使用Cloudflare免费的Argo Tunnel服务，缺点是速度较慢。

## SFSS的使用方法

### 简介
SFSS是一个基于AES对称加密的文件加密工具，它允许你对本地文件进行加密和解密，支持遍历目录。

### 安装依赖
```bash
pip install -r requirements.txt
```

### 使用方法
加密单一文件
```bash
python main.py encrypt -f "C:\Users\user\Music\music.mp3" -o "C:\Users\user\Music-encryped\music.mp3.enc" -p "password"
```
解密单一文件
```bash
python main.py decrypt -f "C:\Users\user\Music-encryped\music.mp3.enc" -o "C:\Users\user\Music-decrypted\music.mp3" -p "password"
```
加密目录
```bash
python main.py encrypt -p "C:\Users\user\Music" -op "C:\Users\user\Music-encryped" -p "password"
```
解密目录
```bash
python main.py decrypt -p "C:\Users\user\Music-encryped" -op "C:\Users\user\Music-decrypted" -p "password"
```

你可以不指定秘钥，程序会自动生成一个秘钥，存储在`key.aes`文件中。

你也可以用自己的秘钥文件替代它。秘钥文件没有格式要求。
