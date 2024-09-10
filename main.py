import sys
import random
import tomllib
from openai import OpenAI
from dotenv import load_dotenv
import os
from loguru import logger
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


class Agent:
    def __init__(self, name, conf, is_player=False):
        self.name = name
        self.is_player = is_player
        if not is_player:
            self.prompts = conf.prompts
            self.personality = random.choice(
                list(conf.prompts['personalities'].keys())
            )
            self.model_params = conf.model_params

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

    def get_next_message(self, state):
        _msg = None
        if self.is_player:
            _msg = console.input(
                f"[dim]You[/dim] ([bold blue]@{self.name}[/]) > ")
        else:
            req_params = {
                "model": self.model_params['model'],
                "messages": [
                    {"role": "system", "content": "Your name is " + self.name},
                    {"role": "system",
                        "content": self.prompts['personalities'
                                                ][self.personality]},
                    {"role": "assistant", "content": "My name is " +
                        self.name + " and I am an AI."},
                    {"role": "system", "content": self.prompts['system']},
                    *self._rolling_messages_conversion(state.messages)
                ]
            }
            logger.debug(f"{req_params=}")
            r = client.chat.completions.create(
                **req_params
            )
            logger.debug(f"{r=}")
            _msg = r.choices[0].message.content

            console.print(f"[bold]@[u]{self.name}[/u]:[/bold] [dim]{_msg}")

        state.messages.append((self.name, _msg))

        return _msg


class GameState:
    def __init__(self):
        self.messages = []
        self.agents = {}


class GameConfig:
    def __init__(self, fname):
        self._fname = fname
        with open(fname, 'rb') as file:
            conf = tomllib.load(file)
            self.conf = conf
        self.text = conf['text']
        self.prompts = conf['prompts']
        self.model_params = conf['model_params']

    def __repr__(self):
        return "GameConfig: " + self.conf.__repr__()


def admin_message(m, state):
    style = "bold cyan"
    console.print(
        "\n[underline]ADMINISTRATOR[/underline]: " + m + "\n", style=style)
    state.messages.append(("ADMINISTRATOR", m))


def message_to_player(m):
    style = "bold italic green"
    console.print(Panel.fit(m, style=style))


def call_vote(state, conf):
    _m = conf.text['vote_announcement']
    admin_message(_m, state)

    _votes = {_n: 0 for _n in state.agents.keys()}
    for _, agent in state.agents.items():
        msg = agent.get_next_message(state)
        try:
            v = msg.split("VOTE:")[1].split("@")[1].split()[0]
            try:
                _votes[v] += 1
            except KeyError:
                logger.warning(f"Invalid vote: '{msg}' parsed to '{v}'")
        except IndexError:
            logger.warning(f"Spoiled vote: {msg}")

    logger.info(f"{_votes=}")

    _name_with_most = max(_votes, key=_votes.get)
    killed = state.agents.pop(_name_with_most)
    return killed


def main_game_loop(state, conf, kill_counter):
    round = 1
    while len(state.agents) > 2:
        logger.debug(f"Resetting kill countdown to {kill_counter}")
        cnt = kill_counter
        while cnt > 0:
            _m = str(cnt) + conf.text['remaining_rounds']
            admin_message(_m, state)
            for _, agent in state.agents.items():
                _ = agent.get_next_message(state)
            cnt -= 1

        _killed = call_vote(state, conf)

        if _killed.is_player:
            message_to_player(conf.text['game_over'] + str(round))
            sys.exit(1)

        _m = conf.text['kill_announcement'] + f"{_killed}\n"
        _m += conf.text['remain_announcement'] + str(list(state.agents.keys()))
        admin_message(_m, state)

        round += 1

    message_to_player(conf.text['win'] + str(round))


def run_game(num_ai=2, kill_counter=3):

    state = GameState()
    conf = GameConfig('config.toml')
    logger.debug(conf)

    message_to_player(conf.text['welcome'])

    # TODO better names (and in conf)
    _names_pool = ["Eve", "Frank", "Gertrude",
                   "Harriet", "Irene", "John", "Kelly"]
    _agent_names = []
    for i in range(num_ai):
        _name = _names_pool.pop(0)
        state.agents[_name] = Agent(_name, conf)
    state.agents["Alice"] = Agent("Alice", conf, is_player=True)

    logger.debug(f"{state.agents=}")

    _m = conf.text['intro_announcement']
    _m += f" The agents in the arena are: {list(state.agents.keys())}"
    admin_message(_m, state)

    main_game_loop(state, conf, kill_counter)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--log_level', type=str, default='WARNING',
                        help='Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--n_ai', type=int, default=2,
                        help='Number of AI players (1–5)')
    parser.add_argument('--kill_count', type=int, default=2,
                        help='Number of message rounds before vote (1–5)')
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    logger.add("dev_logs.log")
    console = Console(color_system="auto")

    MSG_HIST = 20

    load_dotenv()
    OAIKEY = os.getenv("OPENAI_API_KEY_AIMONGUS")
    assert (OAIKEY is not None)
    client = OpenAI(api_key=OAIKEY)

    run_game(num_ai=args.n_ai, kill_counter=args.kill_count)
