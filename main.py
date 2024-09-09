import sys
import random
import tomllib
from openai import OpenAI
from dotenv import load_dotenv
import os

N_AI = 1
N_HUMANS = 1
MSG_HIST = 3

load_dotenv()
OAIKEY = os.getenv("OPENAI_API_KEY_AIMONGUS")
assert (OAIKEY is not None)
client = OpenAI(api_key=OAIKEY)

with open('config.toml', 'rb') as file:
    conf = tomllib.load(file)


class Agent:
    def __init__(self, name, is_player=False):
        self.name = name
        self.is_player = is_player

    def __repr__(self):
        if self.is_player:
            return f"Human({self.name})"
        return f"AI({self.name})"

    def _rolling_messages_conversion(self, messages):
        _msgs = []
        for line in messages[-MSG_HIST:]:
            if line[0] == self.name:
                _role = "assistant"
                _msg = line[1]
            else:
                _role = "user"
                _msg = f"@{line[0]}: {line[1]}"
            _out = {"role": _role, "content": _msg}
            _msgs.append(_out)
        return _msgs

    def ask_for_input(self, message_hist):
        _input = None
        if self.is_player:
            _input = input(f"@{self.name}> ")
            # TODO error handling
        else:
            req_params = {
                "model": conf['model_params']['model'],
                "messages": [
                    {"role": "system", "content": f"Your name is {self.name}."},
                    {"role": "system", "content": conf['prompts']['system']},
                    *self._rolling_messages_conversion(message_hist)
                ]
            }
            print(f"DEBUG: {req_params=}")
            r = client.chat.completions.create(
                **req_params
            )
            print(f"DEBUG: {r=}")
            _input = r.choices[0].message.content

        return _input

    def notify_of_message(self, m):
        pass


if __name__ == '__main__':
    state = {}
    assert (N_HUMANS == 1)
    state['agents'] = []
    for i in range(N_AI):
        _name = f"Eve_{random.randint(100, 999)}"
        state['agents'].append(Agent(_name))
    player = Agent(name="Alice", is_player=True)
state['agents'].append(player)
print(f"DEBUG: {state['agents']=}")

state['messages'] = []

print(conf['messages']['welcome'])
while True:
    try:
        for agent in state['agents']:
            msg = agent.ask_for_input(state['messages'])
            # TODO error handling
            state['messages'].append((agent.name, msg))
            print(f"@{agent.name}: {msg}")
            # print(f"DEBUG: {state['messages']=}")
    except KeyboardInterrupt:
        print("\nYou quit")
        sys.exit(1)
