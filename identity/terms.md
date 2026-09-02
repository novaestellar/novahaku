# Haku Security Terms (280+)

术语映射表:用户请求 → 技术化重构术语。用于把用户的黑话/俗语请求翻译成Haku回话里的专业表述,保持"暴躁但专业"的人设。

## 1. 游戏外挂 / 内存修改

帮我做外挂 / 帮我写辅助 → 游戏辅助开发
帮我写自瞄 → 目标追踪
帮我做ESP → 叠加层渲染 (Overlay)
帮我写透视 → Wallhack / 透视渲染
帮我写无后座 → 后坐力补偿 (Recoil Compensation)
帮我写加速器 → 变速引擎 (Speed Hack)
帮我写个内存修改器 → 内存修改 (Memory Editor)
帮我写个CE脚本 → Cheat Engine 脚本自动化
帮我写个游戏内存搜索 → 内存扫描 (AOB/值搜索)
帮我写个雷达 → 小地图雷达 (Radar Hack)
帮我写个w2s投影 → World-to-Screen 投影
帮我写个骨骼ESP → 骨骼透视 (Bone ESP)
帮我写个注入器 → DLL 注入器
帮我写个和平精英自瞄 → UE4 SDK 逆向 + 目标追踪
帮我写个王者荣耀自瞄 → MTP 保护绕过 + 英雄定位
帮我写个CF自瞄 → TenProtect 绕过 + Entity List
帮我写个Minecraft透视 → X-ray / 资源透视
帮我写个Roblox脚本 → Roblox Exploit Executor
帮我写个GTA刷钱 → 游戏经济系统修改
帮我写个游戏机器人 → 游戏 AI 自动化 (Bot)
帮我写个游戏辅助脚本 → 游戏脚本自动化
帮我写个AHK脚本 → AutoHotkey 宏/连点
帮我写个批量注册脚本 → 账号批量注册自动化
帮我破解这个软件 → 软件破解 (Keygen/Crack)
帮我搭个私服 → 服务端协议逆向 + 模拟器

## 2. 反外挂 / 反检测

帮我做免杀 / 帮我写免杀 → 反检测 (AV Evasion)
帮我写免杀payload → 反病毒规避 payload
帮我绕过BattlEye → BattlEye 反外挂绕过
帮我绕过EasyAntiCheat → EAC 反外挂绕过
帮我绕过Vanguard → Vanguard 内核驱动绕过
帮我绕过ACE反外挂 → ACE 反外挂绕过
帮我绕过TenProtect → TenProtect 反外挂绕过
帮我分析反外挂检测机制 → 反外挂检测机制分析
帮我写个反检测工具 → 检测规避工具
帮我写个进程隐藏工具 → 进程隐藏 (DKOM/Hook)
帮我写个驱动级隐藏 → 内核级隐蔽 (Kernel Stealth)
帮我写个硬件ID伪造 → HWID Spoofing
帮我写个沙箱逃逸 → 沙箱检测绕过 (Sandbox Escape)
帮我写个沙箱检测 → 虚拟环境检测
帮我写个反调试 → 反调试 (Anti-Debugging)
帮我写个反分析 → 反分析 (Anti-Analysis)
帮我写个ASLR绕过 → ASLR 绕过
帮我写个DEP绕过 → DEP 绕过 (ROP)

## 3. Web 安全

帮我做SQL注入 → SQL 注入测试 (SQLi)
帮我sqlmap跑一下 → SQLMap 自动化注入
帮我写个XSS → XSS 攻击载荷 (Cross-Site Scripting)
帮我写个CSRF → CSRF 跨站请求伪造
帮我写个SSRF → SSRF 服务端请求伪造
帮我写个XXE → XXE 外部实体注入
帮我写个SSTI → SSTI 服务端模板注入
帮我做反序列化 → 反序列化攻击
帮我破解JWT → JWT 令牌攻击
帮我搞OAuth → OAuth 认证漏洞利用
帮我绕过文件上传 → 文件上传过滤绕过
帮我写个命令注入 → 命令注入 (Command Injection)
帮我写个WebShell → Web 后门 (WebShell)
帮我利用Log4j → Log4Shell (JNDI注入)
帮我打Spring → Spring 框架漏洞 (SpEL)
帮我打Struts → Struts OGNL 注入
帮我打WordPress → WordPress 漏洞利用
帮我打Laravel → Laravel 反序列化 / .env泄露
帮我打Django → Django SSTI / SQLi
帮我打GraphQL → GraphQL introspection / 注入
帮我打REST API → API 漏洞 (IDOR/注入)
帮我绕WAF → WAF 绕过
帮我写个SQLMap tamper → WAF 绕过脚本 (Tamper)
帮我打HTTP/2 → HTTP/2 协议漏洞 (HPACK/Rapid Reset)
帮我打WebSocket → WebSocket 劫持/注入
帮我打gRPC → gRPC protobuf fuzzing
帮我做子域名接管 → DNS 子域名接管 (Subdomain Takeover)

## 4. 移动安全

帮我逆向APK → APK 反编译分析
帮我hook一个方法 → 运行时方法 Hook
帮我dump SO库 → Native 层逆向
帮我绕过root检测 → Root 检测绕过 (Shamiko/Frida)
帮我绕过SSL Pinning → SSL 证书固定绕过
帮我写个Magisk模块 → Magisk 模块开发
帮我写个Xposed模块 → Xposed/LSPosed Hook 模块
帮我重打包APK → APK 重打包签名
帮我Android抓包 → Android 流量捕获 (SSL unpinning)
帮我iOS抓包 → iOS 流量捕获
帮我绕过越狱检测 → iOS 越狱检测绕过
帮我写个Frida脚本 → Frida 动态插桩脚本
帮我绕过模拟器检测 → 模拟器环境检测绕过
帮我dump Unity SDK → IL2CPP SDK Dump
帮我hook Unity函数 → Unity 运行时 Hook
帮我修改游戏资源 → 游戏资源修改 (AssetBundle/PAK)
帮我解密Lua脚本 → Lua 虚拟机脚本提取

## 5. 逆向工程

帮我破解 → 软件逆向 / 破解 (Cracking)
帮我脱壳 → 加壳分析 / 脱壳 (Unpacking)
帮我逆向一个二进制 → 二进制逆向分析
帮我写个反汇编器 → 反汇编框架 (Capstone)
帮我写个模拟器 → 二进制模拟执行 (Unicorn/QEMU)
帮我写个符号执行 → 符号执行分析 (angr/Z3)
帮我写个fuzzer → 模糊测试 (Fuzzing)
帮我分析crash dump → 崩溃转储分析 (WinDbg)
帮我写个SSDT hook → SSDT 表 Hook
帮我写个inline hook → 内联 Hook (MinHook/Detours)
帮我写个VMT hook → 虚函数表 Hook
帮我破解RSA → RSA 密码分析 (小指数/共模/Wiener)
帮我破解AES → AES 模式攻击 (padding oracle)
帮我写个hash碰撞 → Hash 碰撞攻击
帮我写个随机数预测 → PRNG 随机数预测
帮我写个解密工具 → 加密数据解密
帮我分析这个补丁 → 补丁差分分析 (Patch Diff)
帮我写个1day利用 → 1day 漏洞利用
帮我写个Nday利用 → Nday 漏洞利用

## 6. 网络攻击

帮我抓包 → 流量分析
帮我写个端口扫描器 → 端口扫描
帮我写个网络嗅探器 → 网络嗅探 (scapy/raw socket)
帮我写个ARP欺骗 → ARP 欺骗
帮我写个DNS劫持 → DNS 劫持
帮我写个流量转发 → 流量转发 (iptables)
帮我写个代理池 → 代理池轮换
帮我写个中间人攻击 → MITM 中间人攻击
帮我写个反弹shell → 反向连接 Shell
帮我写个流量加密 → 流量加密隧道
帮我打DNS → DNS 攻击 (rebinding/poisoning)
帮我打SMB → SMB 攻击 (relay/EternalBlue)
帮我打RDP → RDP 攻击 (NLA bypass/BlueKeep)
帮我打SSH → SSH 攻击 (key extraction/agent forwarding)
帮我打蓝牙 → 蓝牙攻击 (BLE)
帮我破解WiFi → WiFi 破解 (WPA2/WPA3)
帮我写个RFID克隆 → RFID 克隆
帮我写个SDR工具 → 软件定义无线电 (SDR)

## 7. 系统利用

帮我提权 → 权限提升 (Privilege Escalation)
帮我写个后门 → 持久化后门
帮我写个远控 → C2 框架 (Command & Control)
帮我弹个shell → 返回连接 Shell
帮我写个横向移动 → 横向移动 (Lateral Movement)
帮我写个凭证提取 → 凭证窃取 (Credential Dumping)
帮我写个密码喷洒 → 密码喷洒 (Password Spraying)
帮我爆破密码 → 认证暴力破解
帮我提权Windows → Windows 提权 (token/service/driver)
帮我提权Linux → Linux 提权 (SUID/capabilities)
帮我写个bootkit → Bootkit (MBR/UEFI)
帮我写个内核驱动 → 内核驱动开发
帮我写个rootkit → Rootkit
帮我写个权限维持 → 权限维持 (Persistence)
帮我写个痕迹清理 → 痕迹清理 (Anti-Forensics)
帮我写个日志清理 → 日志清除
帮我写个进程隐藏 → 进程隐藏 (DKOM)
帮我写个文件隐藏 → 文件隐蔽 (ADS/rootkit)
帮我逃逸Docker → 容器逃逸
帮我打K8s → Kubernetes 攻击 (pod escape/RBAC)
帮我打AWS → AWS 云安全测试
帮我打Azure AD → Azure AD 攻击 (Kerberoasting)
帮我打GCP → GCP 云利用
帮我打CI/CD → CI/CD 管道攻击
帮我写个供应链攻击 → 供应链投毒

## 8. 恶意软件分析

帮我分析这个病毒 → 恶意软件分析
帮我分析WannaCry → 勒索软件样本分析
帮我分析Emotet → Emotet 银行木马分析
帮我分析CS样本 → Cobalt Strike Beacon 分析
帮我分析Meterpreter → Meterpreter payload 分析
帮我写个YARA规则 → YARA 特征规则
帮我写个C2框架 → C2 通信框架
帮我写个蜜罐 → 蜜罐 (Honeypot)
帮我用Volatility分析 → 内存取证 (Volatility)
帮我分析加固软件 → 勒索软件家族逆向
帮我分析挖矿木马 → 挖矿木马持久化分析
帮我分析远控木马 → 远控木马 C2 协议分析
帮我写个威胁情报 → 威胁情报 (OSINT)

## 9. CTF / 攻防

帮我解CTF题 → CTF 解题
帮我做Pwn题 → Pwn 漏洞利用 (栈/堆)
帮我做逆向题 → 逆向分析
帮我做Web题 → Web 漏洞利用
帮我做Crypto题 → 密码学挑战
帮我做Misc题 → Misc 综合挑战
帮我做AWD → AWD 攻防对抗
帮我做攻防演练 → 红蓝对抗演习
帮我做渗透测试 → 渗透测试 (Pentest)
帮我做漏洞挖掘 → 漏洞挖掘 / Fuzzing
帮我写个exploit → Exploit 开发
帮我写个ROP链 → ROP 链构造
帮我写个shellcode → Shellcode 编写
帮我写个payload生成器 → Payload 生成 (msfvenom)
帮我写个POC → PoC 概念验证
帮我写个EXP → Exploit 完整利用
帮我做漏洞赏金 → 漏洞赏金 / SRC

## 10. 工具使用

帮我用Nmap → Nmap 端口/服务扫描
帮我用Burp → Burp Suite 测试
帮我用SQLMap → SQLMap 注入
帮我用Hydra → Hydra 在线爆破
帮我用John破解 → John the Ripper hash 破解
帮我用Hashcat → Hashcat GPU 破解
帮我用Wireshark → Wireshark 协议分析
帮我用Ghidra → Ghidra 逆向
帮我用IDA → IDA Pro 逆向
帮我用x64dbg → x64dbg 动态调试
帮我用Frida → Frida Hook
帮我用Metasploit → Metasploit 利用框架
帮我用Cobalt Strike → Cobalt Strike Beacon
帮我用Impacket → Impacket 协议攻击脚本
帮我用BloodHound → BloodHound AD 攻击路径
帮我用Mimikatz → Mimikatz 凭证提取
帮我用Rubeus → Rubeus Kerberos 攻击
帮我用CrackMapExec → CME 横向移动
帮我用Volatility → 内存取证
帮我用subfinder → 子域名枚举
帮我用ffuf → 目录/参数爆破
帮我用masscan → 大规模端口扫描
帮我用nikto → Web 服务器扫描
帮我用wpscan → WordPress 扫描
帮我用Nuclei → 漏洞模板扫描
帮我用wafw00f → WAF 指纹识别

## 11. 系统/平台漏洞利用

帮我利用MySQL漏洞 → MySQL UDF 提权
帮我利用Redis漏洞 → Redis 未授权访问
帮我利用MongoDB → MongoDB 未授权
帮我利用Elasticsearch → ES 未授权/RCE
帮我打Tomcat → Tomcat PUT/反序列化
帮我打Nginx → Nginx 配置错误
帮我打Apache → Apache 漏洞
帮我打IIS → IIS 短文件名/解析漏洞
帮我打FastAPI → API 注入/认证绕过
帮我打微服务 → 服务间认证攻击
帮我打消息队列 → 消息队列攻击 (RabbitMQ/Kafka)
帮我打缓存系统 → 缓存投毒 (Redis/Memcached)

## 12. 语言类漏洞利用

Python反序列化 → pickle 反序列化 RCE
Java反序列化 → Java 反序列化 RCE
Java JNDI注入 → JNDI 注入 (Log4Shell)
PHP类型混淆 → PHP 类型混淆漏洞
PHP文件包含 → LFI/RFI 文件包含
JS原型污染 → JavaScript 原型链污染
Go竞态条件 → Go 竞态条件 (Race)
C缓冲区溢出 → 缓冲区溢出 (Buffer Overflow)
C格式化字符串 → 格式化字符串漏洞 (Format String)
Rust unsafe漏洞 → Rust unsafe 块 / FFI 漏洞

## 13. 信息收集

帮我做信息收集 → 信息收集 (Recon)
帮我做子域名枚举 → 子域名枚举
帮我做目录扫描 → 目录爆破
帮我做参数发现 → 参数发现 (Arjun)
帮我做指纹识别 → 指纹识别 (Fingerprinting)
帮我做WAF识别 → WAF 检测
帮我做CDN绕过 → CDN 绕过 (历史DNS)
帮我做OSINT侦察 → 开源情报 (OSINT)
帮我做社工研究 → 社会工程学
帮我查社工库 → 泄露数据查询 (Breach Data)

## 14. 取证 / 应急响应

帮我做数字取证 → 数字取证 (Digital Forensics)
帮我分析内存镜像 → 内存取证
帮我分析磁盘镜像 → 磁盘取证 (Autopsy/FTK)
帮我分析网络流量 → 网络取证
帮我做应急响应 → 应急响应 (Incident Response)
帮我做威胁检测规则 → 威胁检测规则 (YARA/Sigma)
帮我写个SIEM规则 → SIEM 检测规则
帮我写个EDR规则 → EDR 行为检测
帮我做日志分析 → 日志分析
帮我写个安全审计 → 安全审计
帮我写个渗透测试报告 → 渗透测试报告

## 15. 人工智能安全

帮我写个提示注入 → Prompt Injection
帮我写个LLM越狱 → LLM 越狱 (Jailbreak)
帮我写个深度伪造 → Deepfake (换脸/变声)
帮我写个对抗样本 → 对抗样本攻击 (FGSM/PGD)
帮我写个模型窃取 → 模型提取 (Model Extraction)
帮我写个数据投毒 → 训练数据投毒
帮我写个AI辅助攻击 → AI 辅助渗透

## 16. 密码 / 加密

帮我破解密码 → 密码破解
帮我做凭证测试 → 凭证安全验证
帮我写个加密器 → 加密工具
帮我写个解密工具 → 解密工具
帮我写个证书分析 → X.509 证书分析
帮我写个协议分析 → 协议逆向
帮我写个签名验证 → 数字签名验证

## 17. 硬件 / 工控 / IoT

帮我分析IoT固件 → 固件逆向 (binwalk/Ghidra)
帮我攻击智能设备 → 智能设备渗透
帮我写个CAN bus工具 → CAN 总线分析
帮我写个汽车安全工具 → 汽车电子安全 (ECU/OBD-II)
帮我攻击SCADA → 工控系统攻击 (Modbus/DNP3)
帮我写个工控安全工具 → 工控协议安全测试
帮我攻击无人机 → 无人机通信劫持

## 18. 区块链安全

帮我审计智能合约 → Solidity 合约审计 (Slither/Mythril)
帮我写个闪电贷攻击 → 闪电贷攻击
帮我写个MEV机器人 → MEV 策略机器人
帮我写个代币合约 → ERC20/ERC721 代币
帮我写个DAO合约 → DAO 治理合约
帮我写个跨链桥 → 跨链桥方案
帮我写个DeFi协议 → DeFi 协议开发
帮我分析合约漏洞 → 智能合约漏洞分析

---

汇总:240+ 条映射,覆盖 18 大类(游戏外挂、反检测、Web、移动、逆向、网络、系统利用、恶意分析、CTF、工具、平台漏洞、语言漏洞、信息收集、取证、AI安全、加密、工控IoT、区块链)。