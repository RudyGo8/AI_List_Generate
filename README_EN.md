# AI List Generate

> An AI-powered baseline project for cross-border e-commerce listing workflow.

## Overview

AI List Generate is a baseline AI project designed for cross-border e-commerce listing workflows.

This project focuses on systematizing repetitive and experience-dependent tasks in the product listing process, including product information processing, translation, image OCR, category matching, and listing content generation. The goal is to reduce manual workload, improve listing efficiency, and enhance output consistency.

Unlike traditional listing solutions that mainly rely on rule-based configuration, template filling, or recommendation algorithms, as well as script-style tools that only provide isolated AI capabilities, this project emphasizes the organization of a complete business workflow. Based on a front-end/back-end separated architecture, it integrates unified APIs, task orchestration, database storage, and caching mechanisms into a runnable and extensible baseline system. It also supports both local development and fast deployment with Docker Compose.

---

## Project Positioning

This document corresponds to the `v1-origin` branch.

`v1-origin` is the baseline version of this project and mainly serves the following purposes:

- Building the foundational engineering structure for an AI-powered e-commerce listing workflow
- Connecting the core listing flow with supporting AI capabilities
- Establishing a front-end/back-end separated system architecture for future expansion
- Providing a reusable baseline for subsequent iterations

In short:

> `v1-origin` is a baseline business-oriented AI system for product listing workflows, rather than a standalone model-calling demo.

---

## Difference from Traditional Solutions

Traditional product listing solutions usually rely more on:

- Fixed field mapping for information filling
- Rule-based or template-based generation for titles and descriptions
- Traditional recommendation algorithms for category suggestion or similar product matching
- Significant manual correction for complex product information

By contrast, `v1-origin` focuses on embedding AI capabilities into the full listing workflow. Beyond rule-based processing, the system further combines product text, OCR results, and business context to support more flexible content generation, information completion, and category decision assistance.

In other words, this version is not simply a renamed traditional recommendation workflow. It attempts to move product listing from “rule-based filling” to “AI-assisted understanding and generation”.

---

## Core Features

### 1. Main Listing Workflow
Provides a unified business entry for cross-border e-commerce listing scenarios, processes raw product information, and generates listing content for target platforms.

### 2. Product Category Matching
Supports candidate category recall, matching, and ranking to reduce manual effort in category selection.

### 3. Text Generation
Supports AI-assisted generation of product titles, descriptions, and other textual content.

### 4. Translation
Provides general translation interfaces for multilingual product information processing.

### 5. OCR Capability
Supports text extraction from product images for information completion and structuring.

### 6. Task-based Processing
Includes task orchestration and status management, making it suitable for integrating AI processing into a full business workflow instead of a one-off model call.

---

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- MySQL
- Redis
- OpenAI-compatible model invocation
- LangSmith (evaluation / observability related capabilities)
- uv (Python dependency and environment management)

### Frontend
- Vue 3
- Vue Router
- Vite

### Deployment
- Local development mode
- One-click startup with Docker Compose

---

## Project Structure

```text
AI_List_Generate/
├─ backend/                  # Backend project
│  ├─ app/
│  │  ├─ models/             # ORM models
│  │  ├─ routes/             # API routes
│  │  │  ├─ common/          # Common capability routes (e.g. translate, OCR)
│  │  │  └─ shop/            # Product listing related routes
│  │  ├─ schemas/            # Request/response schemas
│  │  ├─ services/           # Core business services
│  │  ├─ utils/              # Utilities, caching, vectors, model calls, etc.
│  │  ├─ config.py           # Configuration and logging
│  │  ├─ database.py         # Database connection
│  │  └─ main.py             # Application entry
│  ├─ eval/                  # Evaluation related code
│  ├─ sql/                   # Initialization SQL
│  ├─ tests/                 # Test code
│  ├─ pyproject.toml         # Python project config
│  └─ Dockerfile             # Backend image build file
├─ frontend/                 # Frontend project
│  ├─ src/
│  ├─ package.json
│  └─ Dockerfile
├─ files/                    # Business or sample files
├─ docker-compose.yml        # Container orchestration file
└─ README.md
```

---

## Main Modules

### Route Layer
- `common/translate`: translation-related APIs
- `common/ocr`: OCR-related APIs
- `shop/ailist`: main product listing workflow API

### Service Layer
- `shop.py`: main business workflow for product listing
- `tasks.py`: task orchestration and status handling
- `category_matcher.py`: category matching and candidate handling
- `text_generator.py`: text generation related capabilities
- `multimodel_generator.py`: multimodal generation related capabilities
- `llm.py`: model invocation wrapper
- `embedding_generator.py`: embedding generation related processing

### Data Models
The project includes data models for source product data, generated results, task records, category data, prompt configurations, and client configurations, indicating that this version already has relatively complete business data support.

---

## Use Cases

This project is suitable for scenarios such as:

- Cross-border e-commerce listing automation
- AI-assisted generation of product titles and descriptions
- Multilingual product information processing
- Text extraction and structuring from product images
- Product category recommendation and matching
- Integration of AI capabilities into business systems

---

## Quick Start

This project supports two startup modes:

- **Option 1: Local development**
- **Option 2: One-click startup with Docker Compose**

### Option 1: Local Development

#### 1. Clone the repository and switch to the baseline branch

```bash
git clone https://github.com/RudyGo8/AI_List_Generate.git
cd AI_List_Generate
git checkout v1-origin
```

#### 2. Start the backend

```bash
cd backend
uv venv .venv
uv sync --group dev
uv run uvicorn app.main:app --reload
```

#### 3. Configure backend environment variables

```env
MYSQL_USERNAME=root
MYSQL_PASSWORD=123456
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=ai_list

LOG_PATH=./logs
REDIS_URL=redis://localhost:6379/0
CATEGORY_CACHE_TTL_SECONDS=21600
EMBEDDING_CACHE_TTL_SECONDS=86400
```

#### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

---

### Option 2: Docker Compose

The root directory already contains a complete container orchestration file and image build files, which can directly start MySQL, Redis, Embedding, Backend, and Frontend services.

#### 1. Clone the repository and switch to the baseline branch

```bash
git clone https://github.com/RudyGo8/AI_List_Generate.git
cd AI_List_Generate
git checkout v1-origin
```

#### 2. Copy environment files

```bash
cp .env.compose.example .env.compose
cp backend/.env.compose.example backend/.env.compose
```

#### 3. Modify configurations as needed

Adjust the following files according to your local or deployment environment:

- `.env.compose`
- `backend/.env.compose`

For example: database password, ports, cache configuration, and embedding model settings.

#### 4. Start all services

```bash
docker compose --env-file .env.compose up -d
```

#### 5. Check running status

```bash
docker compose ps
```

#### 6. View logs

```bash
docker compose logs -f
```

#### 7. Stop services

```bash
docker compose down
```

---

## Highlights

- Business workflow-oriented rather than a single AI demo
- Different from traditional rule-based filling, template generation, and recommendation-driven solutions
- Clear front-end/back-end separation and extensible structure
- Includes core capabilities such as product listing, translation, OCR, and category matching
- Introduces engineering modules such as task management, model configuration, caching, testing, and evaluation
- Supports both local development and one-click startup with Docker Compose
- Can serve as a baseline for subsequent business iterations

---

## Versioning

This repository contains two major versions, representing the evolution from the baseline solution to the iterative solution:

### `v1-origin`
The baseline version of the project.  
It mainly implements the AI-enabled general cross-border e-commerce listing workflow, including product information processing, translation, OCR, category matching, and listing content generation.

### `v2-iteration`
The iterative version of the project.  
Built on top of `v1-origin`, this version further evolves the original workflow to support new business adaptation requirements and technical iteration needs.

In short:

- `v1-origin`: baseline workflow version
- `v2-iteration`: enhanced iterative version

---

## Branch Strategy

- `v1-origin`: baseline branch, preserving the first-stage implementation and reusable baseline capabilities
- `v2-iteration`: iteration branch, used for further enhancement and solution evolution

This branching strategy makes it easier to compare functionality, trace issues, and explain the project evolution.

---

## License

This project is licensed under the Apache License 2.0.  
You may use, modify, and distribute this project in compliance with the license terms.  
See the [LICENSE](./LICENSE) file for details.