import chess.pgn
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt

# Function to extract game information
def extract_game_info(pgn_stream):
    games = []
    while True:
        game = chess.pgn.read_game(pgn_stream)
        if game is None:
            break
        # Extract game headers
        headers = game.headers
        moves = game.mainline_moves()
        move_list = [str(move) for move in moves]
        games.append({
            'Event': headers.get('Event'),
            'Site': headers.get('Site'),
            'Date': headers.get('Date'),
            'White': headers.get('White'),
            'Black': headers.get('Black'),
            'Result': headers.get('Result'),
            'WhiteElo': headers.get('WhiteElo'),
            'BlackElo': headers.get('BlackElo'),
            'WhiteRatingDiff': headers.get('WhiteRatingDiff'),
            'BlackRatingDiff': headers.get('BlackRatingDiff'),
            'Variant': headers.get('Variant'),
            'TimeControl': headers.get('TimeControl'),
            'ECO': headers.get('ECO'),
            'Opening': headers.get('Opening'),
            'Termination': headers.get('Termination'),
            'Moves': move_list
        })
    return games

# Load and parse PGN file
with open('games.pgn', 'r') as file:
    pgn_data = file.read()

pgn_stream = StringIO(pgn_data)
games_data = extract_game_info(pgn_stream)
games_df = pd.DataFrame(games_data)

# Convert date to datetime
games_df['Date'] = pd.to_datetime(games_df['Date'])

# Convert Elo ratings to numeric, errors='coerce' will replace non-numeric values with NaN
games_df['WhiteElo'] = pd.to_numeric(games_df['WhiteElo'], errors='coerce')
games_df['BlackElo'] = pd.to_numeric(games_df['BlackElo'], errors='coerce')

# Overall performance
results = games_df['Result'].value_counts()

# Performance by color
white_wins = games_df[games_df['Result'] == '1-0'].shape[0]
black_wins = games_df[games_df['Result'] == '0-1'].shape[0]
draws = games_df[games_df['Result'] == '1/2-1/2'].shape[0]

# Rating changes over time
white_rating_change = games_df.groupby('Date')['WhiteElo'].mean()
black_rating_change = games_df.groupby('Date')['BlackElo'].mean()

# Opening analysis
opening_stats = games_df['Opening'].value_counts()

# Win rate by opening
opening_wins = games_df[games_df['Result'] == '1-0']['Opening'].value_counts()
opening_losses = games_df[games_df['Result'] == '0-1']['Opening'].value_counts()
opening_draws = games_df[games_df['Result'] == '1/2-1/2']['Opening'].value_counts()

# Time control analysis
time_control_stats = games_df['TimeControl'].value_counts()

# Plotting
plt.figure(figsize=(10, 6))
results.plot(kind='bar', title='Game Results')
plt.xlabel('Result')
plt.ylabel('Frequency')
plt.show()

plt.figure(figsize=(10, 6))
white_rating_change.plot(label='White Elo', legend=True)
black_rating_change.plot(label='Black Elo', legend=True)
plt.title('Rating Changes Over Time')
plt.xlabel('Date')
plt.ylabel('Elo Rating')
plt.show()

plt.figure(figsize=(10, 6))
opening_stats.head(10).plot(kind='bar', title='Top 10 Openings')
plt.xlabel('Opening')
plt.ylabel('Frequency')
plt.show()

plt.figure(figsize=(10, 6))
time_control_stats.head(10).plot(kind='bar', title='Time Controls Used')
plt.xlabel('Time Control')
plt.ylabel('Frequency')
plt.show()

# Displaying overall performance and additional insights
print("Overall Performance:\n", results)
print(f"\nTotal number of games: {len(games_df)}")
print(f"\nPerformance by Color: White Wins: {white_wins}, Black Wins: {black_wins}, Draws: {draws}")
print("\nTop 10 Openings:\n", opening_stats.head(10))
print("\nWin Rate by Opening (Top 5):")
print("Wins:\n", opening_wins.head(5))
print("Losses:\n", opening_losses.head(5))
print("Draws:\n", opening_draws.head(5))

# Save dataframe to CSV for further analysis if needed
games_df.to_csv('parsed_lichess_games.csv', index=False)
