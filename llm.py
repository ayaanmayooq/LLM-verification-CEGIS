import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import ast

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a helpful assistant for solving blockworlds tasks.
You are given an input world state and goal state and you
must output a sequence of commands that moves blocks from the input state to the goal state.
The input world state is represented as a list of stacks of blocks.
You have the following commands available to you:
- pickup(block): Pick up the given block.
- putdown(block): Put down the given block.
- unstack(block1, block2): Unstack block1 from block2.
- stack(block1, block2): Stack block1 on block2.
The blocks are always represented as strings.
For example, given this input:
initial_state = [["A", "B", "C"]]
goal_state = [["C", "A", "B"]]
The element left of each stack is on the table. So the initial state is:
C
B
A
====================
Return the following output:
[("unstack", 'C', 'B'), ('putdown', 'C'), ("unstack", 'B', 'A'), ('putdown', 'B'), ('pickup', 'A'), ('stack', 'A', 'C'), ('pickup', 'B'), ('stack', 'B', 'A')]
IMPORTANT:
Do not perform invalid commands. For example, for stack ["A", "B"], you cannot unstack "A" from "B" because "A" is on the table and "B" is stacked on "A".
RETURN ONLY THE SEQUENCE OF COMMANDS AS A SINGLE LINE. NO ADDITIONAL EXPLANATION. RETURN THE COMMANDS INSIDE OF A CODEBLOCK.
"""


class LanguageModel:
    def __init__(self, OPENAI_API_KEY=OPENAI_API_KEY, SYSTEM_PROMPT=SYSTEM_PROMPT, model_type="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.system_prompt = SYSTEM_PROMPT
        self.model_type = model_type

    def request(self, prompt):
        completion = self.client.chat.completions.create(
            model=self.model_type,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5
        )
        response = completion.choices[0].message.content
        return self.extract_code(response)

    def extract_code(self, response):
        if "```" not in response:
            print("[INFO] No code block found in response, returning RAW output.")
            return response
        code_snippets = []
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            code_snippets.append(match.strip())
        return code_snippets[0] if len(code_snippets) else response

    def solve(self, prompt):
        c = 0
        while c < 3:
            c += 1
            try:
                response = self.request(prompt)
                print(response)
                actions = list(ast.literal_eval(response))
                return actions
            except KeyboardInterrupt:
                exit(0)
            except Exception as e:
                print("[INFO] Unable to parse..retrying")


if __name__ == "__main__":
    lm = LanguageModel()
    response = lm.request(
        'initial state: [["A"], ["B"], ["C"], ["D"]]\ngoal state: [["A", "B", "C", "D"]].\nAnswer:'
    )
    print(response)
