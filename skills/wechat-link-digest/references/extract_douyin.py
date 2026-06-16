# 抖音视频信息提取脚本
# 路径: D:\opc-workdown\extract_douyin.py
# 用法: python extract_douyin.py "https://v.douyin.com/xxxx/"
# 原理: 使用 iPhone User-Agent 请求分享页，解析嵌入的 JSON 数据
# 限制: 只能提取元数据（标题/作者/互动），video_text=null，无法获取视频转录
