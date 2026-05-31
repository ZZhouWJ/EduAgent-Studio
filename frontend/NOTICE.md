# NOTICE - 开源组件与模板归属说明

本项目（智研协作 AI 项目质量审计系统）的前端部分基于以下开源项目二次开发：

## 前端基础模板

**V3 Admin Vite**
- 仓库地址：https://github.com/un-pany/v3-admin-vite
- 作者：pany <https://github.com/pany-ang>
- 许可证：MIT License
- 版权声明：Copyright (c) 2022-present pany
- 本项目在 V3 Admin Vite 的基础上进行了以下修改：
  1. 将系统名称、品牌标识替换为"智研协作 AI 项目质量审计系统"
  2. 替换登录页，去除验证码逻辑，对接后端 /api/auth/login 接口
  3. 修改路由配置，替换示例路由为业务占位页面
  4. 修改用户状态管理，对接后端 /api/auth/me 和 /api/auth/logout 接口
  5. 修改 Axios 封装，适配后端统一返回格式 { code, message, data }
  6. 删除模板自带示例页面（demo、permission 等）
  7. 调整环境变量配置，适配本项目后端地址
  8. 替换 Logo 和品牌图片

## 本项目的修改内容

本项目对 V3 Admin Vite 的修改遵循 MIT 许可证，允许自由使用、复制、修改和分发。

## 许可证

除特别注明外，本项目所有代码均采用 MIT 许可证。

---

# NOTICE - Open Source Attribution

This project (AI-Collab-Audit-System Frontend) is based on the following open-source project:

## Base Template

**V3 Admin Vite**
- Repository: https://github.com/un-pany/v3-admin-vite
- Author: pany <https://github.com/pany-ang>
- License: MIT License
- Copyright: Copyright (c) 2022-present pany

All original copyright notices and this permission notice shall be included in all copies or substantial portions of the Software.

See LICENSE file for the full MIT License text.
