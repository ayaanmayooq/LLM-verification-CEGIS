# LLM-Verification-CEGIS

This project integrates large language models (LLMs) with formal verification using a neuro-symbolic approach to program synthesis. The framework leverages Counterexample-Guided Inductive Synthesis (CeGIS) and a mutation engine to improve program accuracy.

## Files Overview

### `blocksworld.py`
This file contains the BlocksWorld model, defining the environment, states, and actions that interact with the formal verification process.

### `llm.py`
Handles the LLM-based program generation, constructing prompts and generating candidate solutions for verification.

### `viz.py`
Provides a PyGame-based visualization for BlocksWorld scenarios. Useful for visualizing LLM-generated programs and their execution in specific cases.

### `utils.py`
Contains helper methods for assessing the BlocksWorld states and actions, used throughout the synthesis and verification process.

## Running the Project

To run the neuro-symbolic synthesis and verification framework, use the following command:

```bash
python3 main.py --config config/exp-3.json --fuzzer
