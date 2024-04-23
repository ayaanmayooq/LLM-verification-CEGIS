# LLM-verification-CEGIS

### `blocksworld.py`
The blocksworld model

### `llm.py`
LLM processing

### `viz.py`
Pygame-based vizualization

### `utils.py`
Helper methods for assessing blockworld states


## TODO
- [ ] implement verifier
- [ ] link to cegis
- [ ] experiments


# Experiments
- [ ] CGEIS vs LLM Pass @ K
    - 2 - 10 blocks
    - metric: found solution, number of iterations   
    - GPT3.5 vs GPT4


```
\begin{align*}
x:= \text{block}, \texttt{pickup(x)}\\
\neg\texttt{Arm(x)} \wedge \texttt{ArmFree}\\
\wedge 
(\forall \;y, y \neq x, \neg\texttt{Stacked(y,x)})
\end{align*}
```