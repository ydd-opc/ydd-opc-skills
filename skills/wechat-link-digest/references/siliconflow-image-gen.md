# 硅基流动 (SiliconFlow) 图像生成配置

## 注册
- 网址: https://siliconflow.cn
- 注册方式: 手机号
- 免费额度: 注册即送，Z-Image-Turbo 模型免费

## API 配置
- 端点: `https://api.siliconflow.cn/v1/image/generations`
- 认证: `Authorization: Bearer <API_KEY>`
- 环境变量: `SILICONFLOW_API_KEY` (已写入 `D:\soft\hermes\.env`)

## 可用模型
| 模型 | 状态 | 速度 |
|------|:---:|:---:|
| Tongyi-MAI/Z-Image-Turbo | ✅ 免费 | 快 (3-5s) |
| Tongyi-MAI/Z-Image | ✅ 免费 | 中 |
| Qwen/Qwen-Image | ✅ 免费 | 中 |
| baidu/ERNIE-Image-Turbo | ✅ 免费 | 快 |

## 生成脚本
`D:\opc-workdown\siliconflow_gen.py`

```bash
# 命令行
python siliconflow_gen.py "prompt" <api_key>

# 或设置环境变量后省略key
export SILICONFLOW_API_KEY=sk-xxx
python siliconflow_gen.py "prompt"
```

## 参数
- `model`: 默认 `Tongyi-MAI/Z-Image-Turbo`
- `image_size`: `1024x1024` | `512x512` | `1024x768` 等
- `num_inference_steps`: 20 (可省略，Turbo模型自动优化)

## 注意事项
- Turbo 模型不支持 `negative_prompt` 参数
- 生成的图片 URL 有时效性（约24小时），需及时下载
- 余额为 0 也能正常使用免费模型
