# AI List Generate (v2-iteration)

The project has been upgraded to **v2-iteration**.

## Key updates in v2

1. Added LoRA fine-tuned generation stack with **4 adapters**:
   - `default`
   - `shopee`
   - `tiktok`
   - `amazon`
2. Added **LiteLLM** as a unified gateway for model management.
3. Final generation round now uses:
   - `site`
   - selected `category_path` (from the category pipeline)
   - source `title`
   to generate site-specific listing style.

## v2 pipeline

1. Round 1 + Round 2 perform category inference and select a final category path.
2. The final round selects a LoRA adapter by scene/site.
3. It generates:
   - `product_title`
   - `product_desc`
   - `attributes`

## Routing and gateway

- Vision/category models and LoRA text models are managed behind LiteLLM.
- Backend keeps one OpenAI-compatible endpoint and routes model selection by task + scene.

## Outcome

- Stable category selection pipeline
- Site-style listing generation in the final round
- Unified output structure for title, description, and attributes

## License

This project is licensed under the Apache License 2.0.
See [LICENSE](LICENSE) for details.

Note: Some third-party models, datasets, and adapter weights may have their own
licenses and usage restrictions. Please review those terms before commercial use.

