X（Twitter）Kodi 插件 1.0.6

项目主页
https://github.com/hjx885210-lang/kodi-x-twitter

稳定功能
- 首页推荐视频（For You）
- 关注页视频（Following）
- 推荐页 / 关注页手动刷新
- 搜索 X 视频
- 作者视频页与作者页刷新
- 插件本地“我喜欢”收藏
- 长按视频加入 / 移出本地收藏
- 长按视频进入作者主页
- 分页浏览
- 观看历史
- 播放前重新解析视频地址
- 自动选择可直接播放的最高码率 MP4
- 保持原视频横屏 / 竖屏比例
- 插件诊断

登录
1. 浏览器登录 https://x.com
2. 获取同一浏览器会话的 x.com Cookie
3. 最低要求 auth_token 和 ct0
4. Kodi -> X（Twitter）-> 登录 X -> 粘贴

Cookie 示例：
auth_token=XXX;ct0=XXX

安全
- auth_token / ct0 属于登录凭据，请按密码级别保护。
- 不要把真实 Cookie 上传到 GitHub、Issue、截图、日志或聊天记录。
- 本项目公开展示不使用成人、敏感或私人推荐流内容。

1.0.6
- 作者主页优先使用 SearchTimeline 的 from:用户名 拉取作者视频，降低对不稳定用户接口的依赖。
- 作者页支持刷新。
- 推荐 / 关注页支持刷新。
- “我喜欢的视频”使用 Kodi 插件本地收藏，不依赖 X 账号 Likes。

说明
X 的非公开 Web 接口可能发生变化。遇到接口兼容问题，请在 GitHub Issues 提交已脱敏的错误信息与 kodi.log 相关行。
