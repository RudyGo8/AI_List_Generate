# AI List Generate（v2-iteration）

当前项目已升级为 **第二代 v2-iteration**。

## v2 核心升级

1. 新增 LoRA 微调模型体系，包含 4 个适配器：
   - `default`
   - `shopee`
   - `tiktok`
   - `amazon`
2. 引入 **LiteLLM** 作为统一模型网关，统一管理多模型调用。
3. 最后一轮文案生成支持按业务上下文动态风格化：
   - 站点 `site`
   - 二轮类目结果 `category_path`
   - 商品标题 `source_title`

## v2 生成流程

1. 第一轮和第二轮完成类目推理，确定最终类目路径。
2. 最后一轮根据 `scene/site` 选择对应 LoRA 适配器。
3. 生成站点风格化结果：
   - `product_title`
   - `product_desc`
   - `attributes`

## 网关与路由说明

- 通过 LiteLLM 将视觉模型与 LoRA 文本生成模型统一在 OpenAI 兼容入口下管理。
- 后端按任务与场景进行模型分配，实现“类目阶段 + 文案阶段”解耦。

## 目标效果

- 类目阶段稳定识别
- 文案阶段按站点风格差异化输出
- 标题、描述、属性在最后一轮统一生成

## 许可证

本项目采用 Apache License 2.0。
详情见 [LICENSE](LICENSE)。

注意：部分第三方模型、数据集或 LoRA 适配器可能有独立许可证和使用限制，
商业使用前请分别确认对应条款。
