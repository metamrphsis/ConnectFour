# Connect Four Game

## Usage

### Basic Command Structure

```bash
python3.10 ConnectFour.py <player1> <player2> [options]
```

`<player1>` and `<player2>` are mandatory arguments that specify the types of the two players. Each can be one of the following:
- `ai`: An AI-controlled player.
- `random`: A player that makes moves randomly.
- `human`: A human player controlling moves via the UI or command line.

## Options

- `--headless`: Run the game in headless mode (without a GUI), suitable for simulations or testing AI strategies.
- `--num <N>`: Specify the number of games to run in headless mode. The default is 10 games if not provided.
- `--seed <S>`: Set a seed for the random number generator to produce replicable game sequences. This option is useful for debugging or analyzing the behavior of AI players.

## Examples

### Run a Single Headless Game Between Random and AI Players

```bash
python3.10 ConnectFour.py random ai --headless
```
This command simulates a single game in headless mode between a random player and an AI player, using the default settings (10 games, no specific seed).

```bash
python3.10 ConnectFour.py random ai --headless --num 7
```
This command runs 7 games in headless mode between a random player and an AI player.

```bash
python3.10 ConnectFour.py random ai --headless --num 7 --seed 7777
```
This command runs 7 games in headless mode between a random player and an AI player, with the random number generator seeded with 7777. This ensures that the sequence of moves and outcomes can be replicated in future runs with the same command.

