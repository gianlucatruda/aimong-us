import sys
import random
import tomllib

N_AI = 1
N_HUMANS = 1


class Agent:
    def __init__(self, name, is_player=False):
        self.name = name
        self.is_player = is_player

    def __repr__(self):
        if self.is_player:
            return f"Human({self.name})"
        return f"AI({self.name})"

    def ask_for_input(self):
        _input = None
        if self.is_player:
            _input = input(f"@{self.name}> ")
            # TODO error handling
        else:
            _input = "I am a robot, beep boop."
            # TODO implement LLM call

        return _input

    def notify_of_message(self, m):
        pass


if __name__ == '__main__':
    state = {}
    with open('config.toml', 'rb') as file:
        conf = tomllib.load(file)
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
            msg = agent.ask_for_input()
            # TODO error handling
            state['messages'].append((agent.name, msg))
            print(f"@{agent.name}: {msg}")
            # print(f"DEBUG: {state['messages']=}")
    except KeyboardInterrupt:
        print("\nYou quit")
        sys.exit(1)
