# Secure, Durable, and Future-Ready Agentic Assistant

This project presents **Maya 3×**, a next-generation agentic assistant designed to overcome key limitations in modern AI assistants related to durability, privacy, and structured tool integration.

## 🚀 Overview

While popular AI assistants excel in conversational tasks, they often lack persistence, privacy guarantees, and reliable integration with user tools. Maya 3× addresses these gaps using a tri-track architecture:

1. **Studio:**

   - Durable multi-agent workflows for long-running tasks.
   - Built with LangGraph and Temporal to guarantee workflow completion despite failures.
   - Integrates Model Context Protocol (MCP) to dynamically connect to workplace tools (e.g., Notion, Google Calendar, Slack).

2. **Live:**

   - Real-time voice, vision, and text interaction.
   - Uses OpenAI’s Realtime API for low-latency, continuous voice and image-based interaction.
   - Supports structured function calling and tool integrations during conversations.

3. **Private:**
   - On-device inference using WebLLM and ONNX for strict privacy.
   - Handles confidential queries locally, allowing the assistant to operate without cloud connectivity.
   - Falls back automatically to offline mode when needed.

## ⚙️ System Design

- **Model Context Protocol (MCP):** Acts like a universal interface to integrate external services into the assistant, allowing seamless tool interoperability without hardcoded APIs.
- **GraphRAG (Graph-based RAG):** Manages a knowledge graph of user data, enabling complex multi-hop retrieval and reasoning across documents and notes.
- **LangGraph + Temporal:**
  - Enables reliable orchestration of multi-step workflows, storing state and recovering from failures automatically.
  - Example workflows include travel planning, team stand-up summarization, and code debugging tasks.

## ✅ Key Features

- Persistent memory of user interactions and workflows
- Privacy-first design with a local model fallback
- Structured output validation to enforce safe, consistent responses
- Human-in-the-loop confirmation for critical actions (e.g., sending emails, deleting files)
- Transparent logs of agent actions for user review

## 📊 Evaluation Results

- **Task Success:** Achieved 92% success in complex user scenarios compared to lower baselines (e.g., Siri, standard ChatGPT plugins).
- **Durability:** Workflows reliably resumed after simulated crashes or network drops.
- **Privacy Mode Performance:**
  - Local model answered ~60% of confidential queries successfully.
  - Latency averaged ~2 tokens/sec on high-end hardware.
  - On-device memory footprint around ~4GB RAM.
- **Safety Mechanisms:**
  - 90% structured output success rate under LangSmith evaluation.
  - Tool calls succeeded in 96% of cases with fallback retries.

## 🔧 Implementation Stack

- Backend in Python using LangChain and LangGraph
- Temporal Python SDK for durable workflow execution
- OpenAI Realtime API for voice and image input/output
- MCP servers for Notion, Google Calendar, Slack, Filesystem
- WebLLM and ONNX Runtime for on-device inference
- Chroma and Neo4j for vector-based and graph-based knowledge management

## 💡 Future Work

- Autonomous tool discovery from MCP registries
- Improved on-device performance and latency
- Enhanced UI for better task state visibility
- Integration of privacy-preserving computation techniques like Private Compute Enclaves

## 📚 Conclusion

Maya 3× demonstrates that a durable, private, and tool-integrated agentic assistant is feasible and effective. It provides a unified experience where users can interact naturally while relying on a resilient backend to manage complex tasks autonomously and securely.

---

## 📂 License

[MIT License](LICENSE)
