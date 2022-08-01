# Aliyun-DDNS-Clientless
基于阿里云解析DNS、函数计算，无需搭建服务器、安装客户端的的阿里云动态域名套件.
## 使用
### Windows (Powershell)
用Powershell获取本机IPv6地址并构建请求URI后执行请求，在单出口网卡的机器上应该能够正常使用.\
如果是IPv4地址，可以去掉请求中的``type``及``value``字段，会自动使用请求来源的IPv4地址.
````
$DDNS_ENDPOINT="https://******.fcapp.run/setRecord"
$SECRET="19260817"
$PREFIX="O-O"
$TYPE="AAAA"
$IPV6_ADDRESS=[System.Net.Dns]::GetHostAddresses('') | Where-Object {$_.AddressFamily -eq 'INterNetworkV6' -and $_.IsIPv6LinkLocal -eq 0 -and $_.IsIPv6Teredo -eq 0} | Select-Object -ExpandProperty IPAddressToString -First 1
$REQUEST_URI=$DDNS_ENDPOINT+"?secret="+$SECRET+"&prefix="+$PREFIX+"&type="+$TYPE+"&value="+$IPV6_ADDRESS
(New-Object System.Net.WebClient).DownloadString($REQUEST_URI)
````
### Linux
还没在Linux下用过，获取IPv6地址自己想办法.
IPv4同上.
````
DDNS_ENDPOINT="https://******.fcapp.run/setRecord"
SECRET="19260817"
PREFIX="O-O"
TYPE="AAAA"
IPV6_ADDRESS="另请高明"
REQUEST_URI=$DDNS_ENDPOINT"?secret="$SECRET"&prefix="$PREFIX"&type="$TYPE"&value="$IPV6_ADDRESS
curl $REQUEST_URI >> /dev/null
````
## Ⅰ.需求
  一个阿里云账号\
  用阿里云解析的域名
## Ⅱ.配置RAM
打开[RAM 访问控制](https://ram.console.aliyun.com/users)
### 创建权限策略
创建一个新的[权限策略](https://ram.console.aliyun.com/policies)\
允许云解析DNS服务下的3个操作
````
alidns:AddDomainRecord
alidns:DescribeDomainRecords
alidns:UpdateDomainRecords
````
将策略限制为**指定资源**以提高安全性，添加资源中将``domainId``字段填入域名即可.\
![Policy](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/RAM\Create_Policy_1.png)
### 设置RAM角色
创建一个新的[RAM 角色](https://ram.console.aliyun.com/roles)\
可信实体类型为**阿里云服务**，将受信服务设为**函数计算**.\
创建完成后为角色新增授权，选择先前创建的权限策略.
![RAM Role 1](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/RAM\Create_RAM_1.png)
![RAM Role 2](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/RAM\Create_RAM_2.png)
![Grant](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/RAM\Grant.png)
## Ⅲ.配置函数计算
#### 创建服务
![Create Service](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/Create_Service.png)
#### 分配角色
将服务角色设定为刚刚创建好的角色.
![Assign Role](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/RAM\Assign_Role.png)
#### 创建函数
**请求处理程序**设置为``ddns.handler``.
![Create Function](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/Create_Function.png)
#### 配置函数
配置环境变量\
``domain_name``即云解析DNS中添加的域名，``secret``为请求中必须包含的密码.
![FC Env](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/FC_Env.png)
上传``ddns.py``至函数编辑器中，删除自动生成的``index.py``.\
用以下命令安装函数需要的依赖，安装完成后点击编辑器右上角的``保存并部署``。
````
pip3 install alibabacloud_tea_util==0.3.6 alibabacloud_alidns20150109==2.0.2 --target .
````
![Install Packages](https://github.com/Fawkex/Aliyun-DDNS-Clientless/blob/main/instruction/Install_Packages.png)
#### 获取入口
在``触发器管理``标签页可以获得函数的公网访问地址``https://******.fcapp.run``，在地址后加上``/setRecord``即可作为接入点用于DDNS脚本.