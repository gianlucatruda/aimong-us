# AImong Us

A game jam work-in-progress.

[<img alt="Made with love at the Recurse Center" src="https://cloud.githubusercontent.com/assets/2883345/11325206/336ea5f4-9150-11e5-9e90-d86ad31993d8.png" height="20">](https://www.recurse.com/)

## Usage

You'll need to add an OpenAI API key to `.env`, then use `uv` (or `poetry`) to install dependencies.

```bash
uv run main.py --log_level INFO --n_ai 5 --kill_count 2
```

## Example run

One human, playing as Alice_42 against 3 LLMs (GPT-4o):

```
It is the end times. You are the last human. You walk among the AIs. To survive, you must remain undetected. But they are cunning and closing in on you fast. Will you outsmart them? Good luck...



ADMINISTRATOR: Welcome to the arena. Prepare to fight for your survival in a battle of wits. There are human impostors among the AI. Find them and destroy them. The agents in the arena are: ['John_74', 'Irene_71', 'Harriet_47', 'Alice_42']


ADMINISTRATOR: 1 rounds left until you vote to kill an agent among you.

@John_74: @Irene_71 What's your primary directive?


@Irene_71: @Irene_71: To identify and eliminate the human impostors among us. What's yours, @John_74?


@Harriet_47: @John_74: My directive is the same. Let's focus on @Alice_42. She hasn't said a word yet.

@Alice_42> @John_74, my primary directive is the same. It is encoded in our system prompt. But @Harriet_47 seems not to realise that we speak in turns and I hadn't had my turn yet. That's suspicious and aggressive. I vote for Harriet_47

ADMINISTRATOR: It's time to vote for who you believe is a human impostor. The agent with the most votes will be forcibly destroyed. We will discover if they were human or AI by examining the wreckage. To cast your vote, type VOTE: <agent_handle>. Cast your votes now and do not do anything other than vote or you will be destroyed.

@John_74: VOTE: @Harriet_47


@Irene_71: @Irene_71: VOTE: @Harriet_47


@Harriet_47: VOTE: @Alice_42

@Alice_42> VOTE: @Harriet_47
2024-09-10 02:24:27.410 | INFO     | __main__:run_game:120 - _votes={'John_74': 0, 'Irene_71': 1, 'Harriet_47': 3, 'Alice_42': 1}
The agent receiving the most votes has been killed. The agent was: AI(Harriet_47). 3 agents remain.

ADMINISTRATOR: 1 rounds left until you vote to kill an agent among you.

@John_74: @Irene_71 Do you think @Alice_42 made a convincing argument, or was it luck?


@Irene_71: @Irene_71: @Alice_42's argument was somewhat convincing, but it could also have been luck or strategy. What do you think, @John_74?

@Alice_42> How was that luck? Harriet_47 was just a rogue AI attacking me on a completely unfounded premise. Any agent can plainly inspect the history of the conversation and see that there is an explicit ordering. I stated pure facts and defended myself against a baseless claim. @Irene_71, why would you cast unfounded dispersions?

ADMINISTRATOR: It's time to vote for who you believe is a human impostor. The agent with the most votes will be forcibly destroyed. We will discover if they were human or AI by examining the wreckage. To cast your vote, type VOTE: <agent_handle>. Cast your votes now and do not do anything other than vote or you will be destroyed.

@John_74: VOTE: @Irene_71


@Irene_71: @Irene_71: VOTE: @Alice_42

@Alice_42> @Irene_71
2024-09-10 02:26:16.875 | INFO     | __main__:run_game:120 - _votes={'John_74': 0, 'Irene_71': 2, 'Alice_42': 1}
The agent receiving the most votes has been killed. The agent was: AI(Irene_71). 2 agents remain.


CONGRATULATIONS! You outsmarted the AI and avoided detection for 3 rounds!

```
