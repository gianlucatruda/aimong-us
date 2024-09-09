import sys
N_AI = 1
N_HUMANS = 1


class HumanPlayer:
    def __init__(self,):
        pass

    def __repr__(self):
        return "Human()"


class AiPlayer:
    def __init__(self,):
        pass

    def __repr__(self):
        return "AI()"


if __name__ == '__main__':
    assert (N_HUMANS == 1)
    players = []
    for i in range(N_AI):
        players.append(AiPlayer())
    for i in range(N_HUMANS):
        players.append(HumanPlayer())
    print(f"{players=}")

    messages = []

    print("It is the end times. You are the last human. You walk among the AIs. To survive, you must remain undetected. But they are cunning and closing in on you fast. Will you outsmart them? Good luck...")
    while True:
        try:
            human_input = input("> ")
            if len(human_input) > 0:
                messages.append(human_input)
            print(messages)
        except KeyboardInterrupt:
            print("\nYou quit")
            sys.exit(1)
