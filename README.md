# AI List Generate (v2-iteration)

This project is now upgraded to **v2-iteration**.

## What is new in v2

- Added LoRA fine-tuned generation models with **4 adapters**:
  - `default`
  - `shopee`
  - `tiktok`
  - `amazon`
- Added **LiteLLM** as a unified gateway to manage multi-model routing.
- Final generation stage now supports style-aware output by:
  - `site`
  - selected `category_path` (from category pipeline)
  - input product `title`

## v2 generation pipeline

1. Category pipeline (round 1 + round 2) selects final category path.
2. Final generation round uses LoRA adapter by site/scene.
3. Output fields are generated in target style:
   - `product_title`
   - `product_desc`
   - `attributes`

## Model routing concept

- Vision/category model and text generation model are managed behind LiteLLM.
- Backend keeps one OpenAI-compatible endpoint and routes models by task + scene.

---

For detailed docs:

- Chinese: [README.zh-CN.md](README.zh-CN.md)
- English: [README_EN.md](README_EN.md)
>>>>>>> f03173d (add lora)
