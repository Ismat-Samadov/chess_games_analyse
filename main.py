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

# Plotting and saving plots
plt.figure(figsize=(10, 6))
results.plot(kind='bar', title='Game Results')
plt.xlabel('Result')
plt.ylabel('Frequency')
plt.savefig('results.png')
plt.close()

plt.figure(figsize=(10, 6))
white_rating_change.plot(label='White Elo', legend=True)
black_rating_change.plot(label='Black Elo', legend=True)
plt.title('Rating Changes Over Time')
plt.xlabel('Date')
plt.ylabel('Elo Rating')
plt.savefig('rating_changes.png')
plt.close()

plt.figure(figsize=(10, 6))
opening_stats.head(10).plot(kind='bar', title='Top 10 Openings')
plt.xlabel('Opening')
plt.ylabel('Frequency')
plt.savefig('top_openings.png')
plt.close()

plt.figure(figsize=(10, 6))
time_control_stats.head(10).plot(kind='bar', title='Time Controls Used')
plt.xlabel('Time Control')
plt.ylabel('Frequency')
plt.savefig('time_controls.png')
plt.close()

# Write results to an HTML file
with open('results.html', 'w') as f:
    f.write("<h1>Chess Games Analysis</h1>")
    f.write("<h2>Overall Performance</h2>")
    f.write(results.to_frame().to_html())
    f.write(f"<p>Total number of games: {len(games_df)}</p>")
    f.write(f"<p>Performance by Color: White Wins: {white_wins}, Black Wins: {black_wins}, Draws: {draws}</p>")
    f.write("<h2>Top 10 Openings</h2>")
    f.write(opening_stats.head(10).to_frame().to_html())
    f.write("<h2>Win Rate by Opening (Top 5)</h2>")
    f.write("<h3>Wins</h3>")
    f.write(opening_wins.head(5).to_frame().to_html())
    f.write("<h3>Losses</h3>")
    f.write(opening_losses.head(5).to_frame().to_html())
    f.write("<h3>Draws</h3>")
    f.write(opening_draws.head(5).to_frame().to_html())

# Save dataframe to CSV for further analysis if needed
games_df.to_csv('parsed_lichess_games.csv', index=False)
