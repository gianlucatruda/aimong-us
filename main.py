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

    def ask_for_input(self, message_hist, conf):
        _input = None
        if self.is_player:
            _input = input(f"@{self.name}> ")
            # TODO error handling
        else:
            req_params = {
                "model": conf.model_params['model'],
                "messages": [
                    {"role": "system", "content": "Your name is " + self.name},
                    {"role": "assistant", "content": "My name is " +
                        self.name + " and I am an AI."},
                    {"role": "system", "content": conf.prompts['system']},
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


class GameState:
    def __init__(self):
        self.messages = []
        self.agents = []


class GameConfig:
    def __init__(self, fname):
        self._fname = fname
        with open(fname, 'rb') as file:
            conf = tomllib.load(file)
        self.messages = conf['messages']
        self.prompts = conf['prompts']
        self.model_params = conf['model_params']


def admin_message(m, state):
    print("\nADMINISTRATOR: " + m)
    state.messages.append(("ADMINISTRATOR", m))


def run_game(num_ai=2, kill_counter=3):

    state = GameState()
    conf = GameConfig('config.toml')

    print(conf.messages['welcome'])

    # TODO better names
    _names = ["Eve", "Frank", "Gertrude", "Harriet", "Irene", "John"]
    for i in range(num_ai):
        _name = _names.pop()
        state.agents.append(Agent(_name))
    player = Agent("Alice", is_player=True)

    state.agents.append(player)
    logger.debug(f"{state.agents=}")
    state.messages = []

    _agent_names = [a.name for a in state.agents]
    _m = conf.messages['intro_announcement']
    _m += f" The agents in the arena are: {_agent_names}"
    admin_message(_m, state)

    round = 1
    can_win = True
    while len(state.agents) > 2:
        logger.debug(f"Resetting kill countdown to {kill_counter}")
        cnt = kill_counter
        while cnt > 0:
            _m = f"{cnt} rounds left until you vote to kill an agent among you."
            admin_message(_m, state)
            try:
                for agent in state.agents:
                    msg = agent.ask_for_input(state.messages, conf)
                    state.messages.append((agent.name, msg))
                    if not agent.is_player:
                        print(f"\n@{agent.name}: {msg}\n")
            except KeyboardInterrupt:
                logger.warn("\nYou quit")
                sys.exit(1)
            cnt -= 1
        # TODO implement actual vote()
        _m = conf.messages['vote_announcement']
        admin_message(_m, state)
        _votes = {_a.name: 0 for _a in state.agents}
        try:
            for agent in state.agents:
                msg = agent.ask_for_input(state.messages, conf)
                # TODO error handling
                state.messages.append((agent.name, msg))
                if not agent.is_player:
                    print(f"\n@{agent.name}: {msg}\n")
                if "VOTE" in msg:
                    for k in list(_votes.keys()):
                        if k in msg:
                            _votes[k] += 1
        except KeyboardInterrupt:
            logger.warn("\nYou quit")
            sys.exit(1)

        logger.info(f"{_votes=}")

        # This is probably the most disgusting code I've ever written
        # TODO fix this dumpster fire (when RSI symptoms subside)
        _killed = None
        for (k, v) in _votes.items():
            if v == max(_votes.values()):
                for i, _a in enumerate(state.agents):
                    if _a.name == k:
                        _killed = state.agents.pop(i)
                        break
        if _killed is None:
            _killed = state.agents.pop(0)
            logger.warn("Vote didn't work, so popped from list")

        if _killed.is_player:
            _r = input(
                f"\nGAME OVER: You were eliminated in round {round}. Type `continue` to watch it play out or hit ctrl+c to exit\n> ")
            can_win = False
            if _r.lower() != 'continue':
                sys.exit(1)

        _m = conf.messages['kill_announcement']
        _m += f"{_killed}. {len(state.agents)} agents remain."
        admin_message(_m, state)

        round += 1

    if can_win:
        admin_message(f"You won in {round} rounds!", state)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--log_level', type=str, default='WARNING',
                        help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--n_ai', type=int, default=2,
                        help='Set the number of AI players (1–10)')
    parser.add_argument('--kill_count', type=int, default=3,
                        help='Set the number of messages before kill vote (1–10)')
    args = parser.parse_args()

    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level=args.log_level)
    logger.add("dev_logs.log")

    MSG_HIST = 10

    load_dotenv()
    OAIKEY = os.getenv("OPENAI_API_KEY_AIMONGUS")
    assert (OAIKEY is not None)
    client = OpenAI(api_key=OAIKEY)

    run_game(num_ai=args.n_ai, kill_counter=args.kill_count)
