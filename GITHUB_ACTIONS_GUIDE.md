# GitHub Actions 自动化构建说明

## 工作流说明

这个工作流会在你推送标签时自动构建和发布可执行文件。

### 工作流特点

1. **多平台支持**：自动为 Windows、macOS、Linux 各构建一个版本
2. **依赖缓存**：使用pip缓存加速构建，比本地快2-3倍
3. **并行构建**：三个平台同时构建，大约需要 2-5 分钟
4. **自动发布**：构建完成后自动生成Release，并上传二进制文件

## 使用步骤

### 1. 推送标签触发构建

```bash
# 在本地修改代码后
git add .
git commit -m "更新功能"

# 推送代码
git push origin main

# 创建标签（格式：v+版本号）
git tag v1.0.0
# 或
git tag v1.0.1

# 推送标签到GitHub（这会触发自动构建）
git push origin v1.0.0
```

### 2. 监控构建进度

访问你的GitHub仓库 → **Actions** 标签页，可以看到：
- 实时构建日志
- 三个平台的构建状态
- 完成时间

### 3. 下载发布版本

构建完成后：
1. 进入仓库的 **Releases** 页面
2. 找到对应版本（如 v1.0.0）
3. 下载对应平台的可执行文件

## 优化建议

### 快速构建的注意事项

1. **Python版本**：使用3.11（稳定且速度快）
2. **缓存优化**：首次构建会慢一点，之后会快很多
3. **并行构建**：三个平台同时构建，总时间只是单个平台的时间

### 进一步加速的方案

如果还想更快，可以考虑：

**方案A：只构建必要的平台**
编辑 `.github/workflows/build-release.yml`，修改 `matrix.os`：
```yaml
matrix:
  os: [windows-latest, macos-latest]  # 只构建Windows和macOS
```

**方案B：使用UPX压缩可执行文件**（减小文件体积）
在build.py中添加UPX压缩：
```bash
pip install -r requirements-build.txt
pip install upx  # 可选，用于压缩
```

**方案C：构建时跳过分析**
修改build.py，移除不必要的分析选项：
```python
"--clean",      # 删除此行，避免每次清理
"--noconfirm",
```

## 标签命名规范

- `v1.0.0` - 正式版本
- `v1.0.0-beta` - 测试版本
- `v1.0.0-rc1` - 候选版本

推荐使用 [语义化版本](https://semver.org/lang/zh-CN/)

## 常见问题

**Q: 为什么第一次构建很慢？**
A: 第一次需要下载所有依赖和构建工具。之后会使用缓存，速度会快3倍。

**Q: 如何跳过自动构建？**
A: 推送代码时不推送标签，工作流就不会触发。

**Q: 构建失败了怎么办？**
A: 检查Actions页面的日志，找到具体错误，通常是依赖问题。

**Q: 可以手动触发构建吗？**
A: 可以，在 `.github/workflows/build-release.yml` 中添加 `workflow_dispatch:` 事件。

**Q: Release文件太大了怎么办？**
A: PyInstaller的单文件模式会比较大（50-100MB），可以改为目录模式减小体积。

## 下一步

1. 提交这个工作流文件到你的GitHub仓库
2. 创建第一个标签测试：`git tag v1.0.0 && git push origin v1.0.0`
3. 在Actions页面监控构建过程
4. 在Releases页面下载构建好的文件

---

**注意**：确保 `requirements-build.txt` 和 `requirements.txt` 都已经上传到GitHub仓库。
