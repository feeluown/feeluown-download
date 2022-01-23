# feeluown-download

feeluown 下载插件

## Roadmap

### 和 FeelUOwn 集成

- [ ] (#A) 在 FeelUOwn UI 反馈当前文件下载进度
- [ ] (#B) 可以配置并发度，目前是一个一个文件下载
- [ ] (#B) 给 fuo 命令行工具添加 `dl` 子命令，比如 `fuo dl fuo://xxx/songs/1`

### 自身

- [ ] (#A) 提供一个 cli 工具来方便 debug
- [ ] (#A) 有比较完善的错误处理机制
- [ ] (#B) 程序重启可以从上次的临时文件恢复

## Changelog

### v0.3 - 2022-01-23

* 适配 v3.8.1 的 FeelUOwn
* 修复部分已知问题

### v0.2 - 2020-10-18

* 修复下载内容和文件名不符的重大 bug
* 默认使用基于 requests 的多线程下载器

### v0.1 - 2020-09-07

* 支持 FeelUOwn v3.5.3
* 提供 CurlDownloader 来简单的下载歌曲
