# FeelUOwn 下载插件

FeelUOwn 下载插件，不提供（也不建议提供）安装包，需要的使用者可以自己下载安装。

## 第二版功能说明
### 下载按钮
下载按钮会集成到歌曲的右键菜单里面。

### 下载歌曲
只支持下载 v2 model 的歌曲。下载歌曲的时候，如果歌曲已经存在，则跳过下载。
下载歌曲时，会自动给歌曲添加 id3 tag 信息。

如果需要将文字（从繁体）自动转成简体，可以安装 `pip3 install inlp` 依赖，并配置
```python
app.config.dl.CORE_LANGUAGE = 'cn'
```

### 歌曲文件默认命名规则
`{title}__{artists_names}__{album_name}__{kbps}__{duration_ms}.{ext}`
`title`, `artists_names`, `album_name` 默认值为 unknown。
当任一一个值含有 `__` 分隔符的时候，都会进行转义。
kbps 默认值为 0kbps，duration_ms 默认值为 0。

## Roadmap

- [ ] (#A) 在 FeelUOwn UI 反馈当前文件下载进度
- [ ] (#B) 可以配置并发度，目前是一个一个文件下载
- [ ] (#B) 给 fuo 命令行工具添加 `dl` 子命令，比如 `fuo dl fuo://xxx/songs/1`
- [ ] (#A) 提供一个 cli 工具来方便 debug
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
