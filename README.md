# LangGraph Advanced: AI Agent Development

## Overview
LangGraph Advanced is a project that explores the implementation of **advanced AI agents** using **LangGraph**. The goal is to create modular, scalable, and production-ready agents by leveraging **state-based workflows**, advanced memory management, and multi-agent interactions. This repository contains the code, notes, and solutions developed during the research and experimentation process.

## Key Features
- **State-Based Workflows** – Structuring agents with nodes and edges to ensure scalability and maintainability.
- **Advanced Memory Management** – Implementing short-term memory (checkpointers) and long-term memory (Store object).
- **Multi-Agent Interactions** – Developing architectures with multiple agents collaborating in complex scenarios.
- **Integration with FastAPI and Docker** – Creating production-ready AI systems with scalable APIs and automated deployment.

## Project Goals
- **Explore the advanced capabilities of LangGraph** to build intelligent and modular AI agents.
- **Experiment with orchestration models** to optimize decision-making and state management.
- **Test and validate integration with production stacks**, ensuring performance and reliability.

## Technologies Used
- **Python** for agent development
- **LangGraph** for flow and state management
- **FastAPI** for interactive API exposure
- **Docker** for scalable deployment
- **Unit testing and advanced debugging** for system stability

## Jupyter Notebooks
This repository includes various **Jupyter notebooks** demonstrating key concepts and features of LangGraph:
- **Basics.ipynb** – Introduction to LangGraph fundamentals and agent workflows.
- **Tool_calling_basics.ipynb** – Demonstrates tool invocation within LangChain.
- **Agent_basics.ipynb** – Explores essential agent functionalities in LangGraph.
- **RAG_Basics.ipynb** – Covers Retrieval-Augmented Generation (RAG) concepts.
- **RAG_Agent.ipynb** – Implements a RAG-enhanced AI agent for improved retrieval.
- **RAG_Agent_with_memory.ipynb** – Extends a RAG agent with memory for contextual awareness.
- **Advanced_State.ipynb** – Advanced techniques for managing agent states in workflows.
- **Human_in_the_Loop.ipynb** – Incorporates human feedback in decision-making processes.
- **ParallelExecution.ipynb** – Demonstrates parallel execution of nodes for efficiency.
- **AsyncAndStreaming.ipynb** – Explores asynchronous execution and streaming outputs.
- **Subgraphs.ipynb** – Shows how to use subgraphs to modularize workflows.
- **Agent_Patterns.ipynb** – Presents reusable agent design patterns.
- **LongTermMemory.ipynb** – Implements long-term memory in LangGraph-based agents.

## Getting Started
To run the project locally:
```sh
# Clone the repository
git clone https://github.com/<USERNAME>/<REPO>.git
cd <REPO>

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

LangGraph Advanced is the result of an extensive experimentation and optimization process in AI agent development. This repository documents the work done and the techniques used to create intelligent and efficient systems.

