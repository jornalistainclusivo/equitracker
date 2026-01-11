# 🌍 EquiTracker | v0.3 Alpha (Sovereign & Local)

**Data:** 11/01/2026
**Status:** Ready for Development
**Ambiente:** Windows 11 (WSL2) + Docker Desktop + VS Code

## 🎯 1. Visão Geral e Mudança de Paradigma

* **A Evolução:** Saímos de uma arquitetura "híbrida" para uma arquitetura **"Local-First"**.
* **A Promessa (Refinada):** "Soberania Radical". Não alugamos inteligência, nós a hospedamos. O EquiTracker v0.3 roda o ciclo completo de inteligência (Coleta -> Análise -> Armazenamento) dentro da sua máquina, sem enviar metadados de vetores para terceiros.
* **Viabilidade Econômica:** Custo de operação próximo de zero (apenas consumo de energia local e chamadas de API do LLM).
* **Viabilidade Técnica no Windows:** Unificação de serviços. Em vez de rodar múltiplos bancos (Neo4j + Pinecone + Redis), usaremos o **Neo4j 5.x** para **TUDO** (Grafo + Vetores), economizando RAM do WSL2.

---

## 🛠️ 2. Tech Stack: "The Sovereign Stack"

Esta stack foi escolhida para ser orquestrada por Agentes de IA no VS Code.

* **Frontend (UI):** Next.js 15 (App Router) + Shadcn/UI (Acessibilidade nativa) + TailwindCSS.
* **Backend (Brain):** Python 3.11 + **FastAPI**.
* *Por que Python?* Bibliotecas de IA e Scrapers são nativos aqui. O Next.js será apenas a "casca" visual.

* **Orquestração de IA:** **LangChain** + **LangGraph** (Gerenciamento de estado dos agentes).
* **Banco de Dados Unificado (The Core):** **Neo4j Community Edition (v5.15+)**.
* *Função Dupla:* Armazena o Grafo (Nós/Relacionamentos) **E** o Índice Vetorial (Embeddings) no mesmo lugar.
* *Vantagem:* Elimina a necessidade do Pinecone. Simplifica queries híbridas.

* **Ingestão (Local Scraper):** **Crawl4AI** (Python Library).
* *Substituto do Apify:* Biblioteca open-source leve que usa o navegador local (Playwright) para ler sites dinâmicos sem custo.

* **LLMs:**
* **Raciocínio/Extração:** Google Gemini 1.5 Pro.
* **Triagem Rápida:** Google Gemini 1.5 Flash (Baixa latência).
* **Embeddings:** `text-embedding-3-small` (OpenAI) ou `models/embedding-001` (Google) - *Custo irrisório*.

---

## 🧠 3. Arquitetura Lógica: GraphRAG Local

O maior desafio técnico é o GraphRAG. Aqui está como seus agentes devem construí-lo:

### O Fluxo de Dados "GraphRAG"

1. **Ingestão:** O `Crawl4AI` baixa a notícia.
2. **Chunking:** O texto é dividido em pedaços.
3. **Vetorização:** Cada pedaço vira um vetor (embedding) e é salvo no Neo4j como uma propriedade do nó `:Chunk`.
4. **Extração de Entidades (Graph):** O Gemini Pro lê o texto e extrai: `(:Pessoa)-[:PROPÔS]->(:Lei)`.
5. **A Mágica da Busca (Retrieval):**

* Quando você pergunta algo, o sistema faz uma **Busca Híbrida**:
* 1. Busca Vetorial (acha textos semanticamente parecidos).

* 1. Travessia de Grafo (acha conexões ocultas a partir dos nós encontrados).

---

## ⚡ 4. Roteiro de Implementação (Focado em Agentes)

Use estes passos para guiar o Copilot/Antigravity.

### Fase 1: A Fundação de Ferro (Infraestrutura)

* **Objetivo:** Subir o Neo4j preparado para Vetores no Docker.
* **Desafio Windows:** Configurar memória do Java no Neo4j para não estourar o WSL2.
* **Arquivo:** `docker-compose.yml`

> **Prompt para o Agente:**
> "Crie um `docker-compose.yml` para Neo4j 5.x Community.
>
> 1. Configure portas 7474 e 7687.
> 2. Habilite plugin APOC.
> 3. **Crítico:** Defina variáveis de ambiente para limitar memória Java: `NEO4J_server_memory_pagecache_size=1G` e `NEO4J_server_memory_heap_initial_size=1G` (para rodar leve no Windows).
> 4. Adicione persistência de volume local."
>
>

### Fase 2: O Agente de Ingestão (Sovereign Scraper)

* **Objetivo:** Ler notícias sem pagar API de terceiros.
* **Ferramenta:** `AsyncWebCrawler` (da lib Crawl4AI).

> **Prompt para o Agente:**
> "Crie um script Python `ingest.py`. Use a biblioteca `crawl4ai` para acessar uma URL de teste (ex: um site de notícias governamentais). Extraia o markdown limpo. Em seguida, use `LangChain` para dividir o texto (TextSplitter) em pedaços de 1000 caracteres."

### Fase 3: O Cérebro Híbrido (Graph + Vector)

* **Objetivo:** Salvar dados no Neo4j com Embeddings.

> **Prompt para o Agente:**
> "Crie uma classe Python `KnowledgeBase`.
>
> 1. Conecte ao Neo4j.
> 2. Crie um índice vetorial no Neo4j chamado `news_vector` usando Cypher: `CREATE VECTOR INDEX...`.
> 3. Ao receber um texto, gere o embedding (Google GenAI) e salve o nó com a propriedade `.embedding`."
>
>

---

## 🛡️ 5. Configuração Crítica de Windows (WSL2)

Antes de começar, você **precisa** garantir que o Docker não trave seu computador. Isso é pré-requisito para rodar o GraphRAG localmente.

**Arquivo `.wslconfig` (Na pasta `C:\Users\SeuUsuario\`):**
Seus agentes não podem criar isso, você deve fazer manualmente.

```ini
[wsl2]
memory=6GB   # Limita o WSL a 6GB de RAM (ajuste conforme seu PC)
processors=2 # Limita a 2 núcleos para não travar o sistema
swap=2GB
localhostForwarding=true

```

---

## 🧪 6. Métricas de Sucesso do MVP (v0.3)

1. **Zero Crash:** O ambiente Docker roda por 24h sem reiniciar o WSL2.
2. **Custo Zero de Ingestão:** O sistema lê 50 URLs/dia usando processamento local (Crawl4AI) em vez de APIs pagas.
3. **Recuperação Precisa:** Ao buscar "Enchentes", o sistema traz a notícia E o nome do político responsável (conexão via Grafo).

---
