# 🏗️ KILAT: Technical Architecture (Supercharge Update)

This document provides a technical overview of the KILAT system as of v0.0.4.

## 🏛️ Core Components

### 1. Main Application (`kilat.py`)
The central entry point and interactive loop.
- **Role**: Tool orchestration, state management, and user interaction.
- **Hardware Integration**: Automatically scales to 327,680 context tokens for RTX 3090.

### 2. Context Management (`kilat_core/context/`)
Advanced token and memory management system.
- **SmartTokenCounter**: O(1) incremental counting with periodic recalibration.
- **PriorityContextManager**: Tiers data into CRITICAL (current task), IMPORTANT (project global), and NORMAL (history).
- **HybridSummarizer**: 8:1 compression ratio using LLM-based recursive summarization.

### 3. Tool Intelligence Layer (`kilat_core/tools/`)
#### Batch Operations
- **`read_many_files`**: Batch reads with glob support to minimize round-trips.
- **`edit_many_files`**: Atomic multi-file edits with consistency rollback.

#### Semantic Navigation (Tree-sitter)
- **`semantic_search`**: AST-based symbol lookup. Provides precision results for functions, classes, and imports.

#### Supercharge Multi-Agents
- **Review Manager**: Concurrent audit of security, performance, and style.
- **Testing Tool**: Automated test generation and self-healing loop.

### 4. Planning & Reasoning (`kilat_core/planner.py`)
- **Planner-Executor**: Implementation of the `/plan` command. Allows the agent to derive sub-tasks and user-approved execution paths for complex refactorings.

### 5. Web Intelligence (MCP)
- **Bridge**: Automatic discovery and binding of MCP servers (DuckDuckGo, Playwright).
- **Researcher**: Synthesis of live web data into technical digests.

---

## 🚦 Execution Flow
1. **Init**: Smart MCP Manager starts auto-servers.
2. **Context**: Memory Manager injects project-wide decisions.
3. **Loop**:
   - User inputs task (CMD or Natural Language).
   - Planner (optional) derives steps.
   - LLM Orchestrator selects tools (Core, Legacy, or Supercharge).
   - Context Visualizer provides real-time token feedback.
4. **Exit**: Safe shutdown of all background MCP processes.

## ⚡ Hardware Optimizations (RTX 3090)
- **VRAM Caching**: Utilizes `q4_0` KV-cache for massive context.
- **Parallelism**: Multi-agent tools leverage GPU concurrency during file audits.
- **Flash Attention**: Enabled for sub-millisecond token processing at 100K+ depths.
