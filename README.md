# 🚀 Intelligence-Abroad-BR: Estelar Ecosystem
### *An Intelligent Architecture for Real Estate, E-commerce, and Digital Presence Scaling*

Este repositório contém a infraestrutura completa de um ecossistema de inteligência artificial híbrida (Local/Cloud), projetado para automação de mercado imobiliário, análise de dados financeiros e geração de conteúdo digital escalável. 

O projeto reflete a aplicação de conceitos de **Bacharelado em Matemática (UFRGS)** em conjunto com **Engenharia de Dados** e **Sistemas Distribuídos**.

---

## 🏗️ Arquitetura do Sistema

O ecossistema opera em um modelo **Híbrido Windows-Linux (WSL2)**, otimizado para o hardware **Dell G15 (Intel i5 12th Gen / RTX 3050)**.



### 1. Camada de Inteligência (The Brain)
* **Ollama (Nativo Windows):** Servidor local de LLMs acessando diretamente a RTX 3050 via aceleração CUDA.
    * *Modelos:* `deepseek-r1:8b` (Raciocínio Matemático), `qwen2.5-coder:7b` (Automação Python) e `llama3.2` (Processamento Rápido).
* **Vector Database:** Persistência de conhecimento para RAG (Retrieval-Augmented Generation) integrado ao **Obsidian**.

### 2. Orquestração e Automação (The Nervous System)
* **n8n (Docker/WSL2):** Hub central de fluxos de trabalho que conecta scrapers, bancos de dados e IAs.
* **Kubernetes (Kind):** Orquestração de micro-serviços para garantir que os robôs de scraping sejam resilientes e auto-regenerativos.
* **K9s:** Interface de gerenciamento em tempo real via terminal para monitoramento de pods e logs.



### 3. Síntese de Identidade Digital (Content Scaling)
* **Voice Cloning (GPT-SoVITS):** Clonagem de voz de alta fidelidade para narração automatizada de anúncios.
* **Visual Synthesis (LivePortrait):** Animação de fotos estáticas com sincronia labial e microexpressões naturais para vídeos de alta conversão.

---

## 🛠️ Stack Tecnológica

| Componente | Tecnologia | Implementação |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.11 | Scrapers, Análise de Dados e Scripts de IA |
| **Infraestrutura** | Docker / Kubernetes (Kind) | Containerização e Orquestração |
| **Monitoramento** | Grafana / Prometheus | Observabilidade de Performance e GPU |
| **Cache/Mensageria**| Redis | Otimização de requisições e controle de estado |
| **Banco de Dados** | PostgreSQL / Supabase | Armazenamento de Inteligência de Mercado |

---

## 🚀 Como Iniciar

### Pré-requisitos
* Windows 11 com **WSL2** habilitado.
* Docker Desktop instalado e configurado para usar o WSL2.
* Ollama instalado nativamente no Windows.

### Passo 1: Levantar a Infraestrutura Base
```powershell
# Clone o repositório
git clone [https://github.com/seu-usuario/intelligence-abroad-br.git](https://github.com/seu-usuario/intelligence-abroad-br.git)
cd intelligence-abroad-br

# Iniciar o n8n, Redis e Postgres
docker-compose up -d