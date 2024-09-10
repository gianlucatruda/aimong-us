import sys
import random
import tomllib
from openai import OpenAI
from dotenv import load_dotenv
import os
from loguru import logger
import argparse


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
                    {"role": "system", "content": "Your name is " + self.name},
                    {"role": "assistant", "content": "My name is " +
                        self.name + " and I am an AI."},
                    {"role": "system", "content": conf['prompts']['system']},
                    *self._rolling_messages_conversion(message_hist)
                ]
            }
            logger.debug(f"{req_params=}")
            r = client.chat.completions.create(
                **req_params
            )
            logger.debug(f"{r=}")
            _input = r.choices[0].message.content

        return _input

def run_game(N_AI=2, KILL_CNT=3):
    print(conf['messages']['welcome'])

    state = {}
    assert (N_HUMANS == 1)
    state['agents'] = []
    _names = ["Eve", "Frank", "Gertrude", "Harriet", "Irene", "John"]
    for i in range(N_AI):
        _name = f"{_names.pop()}_{random.randint(10, 99)}"
        state['agents'].append(Agent(_name))
    player = Agent(name="Alice_42", is_player=True)

    state['agents'].append(player)
    logger.debug(f"{state['agents']=}")
    state['messages'] = []

    # TODO refactor this pattern to a function
    _m = conf['messages']['intro_announcement'] + \
        f" The agents in the arena are: {[a.name for a in state['agents']]}\n"
    print("\nADMINISTRATOR: " + _m)
    state['messages'].append(("ADMINISTRATOR", _m))

    round = 1
    while len(state['agents']) > 2:
        logger.debug(f"Resetting kill countdown to {KILL_CNT}")
        cnt = KILL_CNT
        while cnt > 0:
            _m = f"{cnt} rounds left until you vote to kill an agent among you."
            print("\nADMINISTRATOR: " + _m)
            state['messages'].append(("ADMINISTRATOR", _m))
            try:
                for agent in state['agents']:
                    msg = agent.ask_for_input(state['messages'])
                    # TODO error handling
                    state['messages'].append((agent.name, msg))
                    if not agent.is_player:
                        print(f"\n@{agent.name}: {msg}\n")
            except KeyboardInterrupt:
                print("\nYou quit")
                sys.exit(1)
            cnt -= 1
        # TODO implement actual vote()
        _m = conf['messages']['vote_announcement']
        print("\nADMINISTRATOR: " + _m)
        state['messages'].append(("ADMINISTRATOR", _m))
        _votes = {_a.name: 0 for _a in state['agents']}
        try:
            for agent in state['agents']:
                msg = agent.ask_for_input(state['messages'])
                # TODO error handling
                state['messages'].append((agent.name, msg))
                if not agent.is_player:
                    print(f"\n@{agent.name}: {msg}\n")
                if "VOTE" in msg:
                    for k in list(_votes.keys()):
                        if k in msg:
                            _votes[k] += 1
        except KeyboardInterrupt:
            print("\nYou quit")
            sys.exit(1)

        logger.info(f"{_votes=}")

        # This is probably the most disgusting code I've ever written
        # TODO fix this dumpster fire (when RSI symptoms subside)
        _killed = None
        for (k, v) in _votes.items():
            if v == max(_votes.values()):
                for i, _a in enumerate(state['agents']):
                    if _a.name == k:
                        _killed = state['agents'].pop(i)
                        break
        if _killed is None:
            _killed = state['agents'].pop(0)
            logger.warn("Vote didn't work, so popped from list")

        if _killed.is_player:
            _r = input(
                f"\nGAME OVER: You were eliminated in round {round}. Type `continue` to watch it play out or hit ctrl+c to exit\n> ")
            if _r.lower() != 'continue':
                sys.exit(1)

        _m = conf['messages']['kill_announcement'] + \
            f"{_killed}. {len(state['agents'])} agents remain."
        print(_m)
        state['messages'].append(("ADMINISTRATOR", _m))

        round += 1

    print(f"\n\nCONGRATULATIONS! You outsmarted the AI and avoided detection for {round} rounds!")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--log_level', type=str, default='INFO',
                        help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--n_ai', type=int, default=2,
                        help='Set the number of AI players (1–10)')
    parser.add_argument('--kill_count', type=int, default=3,
                        help='Set the number of messages before kill vote (1–10)')
    args = parser.parse_args()

    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level=args.log_level)
    logger.add("dev_logs.log")

    N_HUMANS = 1
    MSG_HIST = 50

    load_dotenv()
    OAIKEY = os.getenv("OPENAI_API_KEY_AIMONGUS")
    assert (OAIKEY is not None)
    client = OpenAI(api_key=OAIKEY)

    with open('config.toml', 'rb') as file:
        conf = tomllib.load(file)

    run_game(N_AI=args.n_ai, KILL_CNT=args.kill_count)
