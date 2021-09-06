"""
A backtesting module inspired by MT5 strategy tester. 
Contains relevant classes to develop and test trading strategies.
Developed by Ahmet Oguzlu
"""
from datetime import timedelta
import MetaTrader5 as mt5
import numpy as np
import pandas as pd

""" 
An interface for a strategy.
Strategies should implement this.
This class acts as the trader.
"""
class Strategy:
	def __init__(self, tfs):
		# List of timeframes that the strategy will listen to
		tfs.sort(reverse=True)
		self.tfs = tfs
		self.positions = []
		self.analyzer = Analyzer()

		# <timeframe> : [<Bar>, <Bar>, ...]
		self.bars = {tf: [] for tf in self.tfs}
		

	""" 
	Feeds a bar to the strategy. If the bar is new, 
	adds the bar and returns True. If the bar is the
	same as the last bar of the same timeframe, returns 
	False.
	"""
	def feed_bar(self, bar):
		if len(self.bars[bar.tf]) != 0 and self.bars[bar.tf][-1].close_time == bar.close_time:
			return False

		self.bars[bar.tf].append(bar)

		return True


	"""
	Called on each new bar
	"""
	def on_new_bar(self, new_tfs):
		pass

	"""
	Tests the strategy
	""" 
	def test(self, symbol, start_date, end_date, calc_weekly=True, display=True):
		tester = Tester(self, symbol, start_date, end_date)
		tester.test()
		self.analyzer.analyze(calc_weekly, display)


	def open_position(self, _type, price, time):
		pos = Position(_type, price, time)
		self.positions.append(pos)


	def close_position(self, pos, price):
		self.positions = []
		trade = Trade(pos.entry_time, pos.entry_price, price, pos.type)
		self.analyzer.add_trade(trade)



"""
Analyzes given history of trades
"""
class Analyzer:
	def __init__(self):
		self.trades = []
		self.stats = None
		self.weekly = None
		self.balances = [0]

	"""
	Analyzes the trade history.
	"""
	def analyze(self, calc_weekly, display):
		self.stats = self.trade_stats(self.trades)
		if calc_weekly:
			self.weekly = self.weekly_mean_dev_min_max(self.weekly_stats(self.trades))

		if display:
			self.display(calc_weekly)

	"""
	Logs the trade into trades list.
	"""
	def add_trade(self, trade):
		self.trades.append(trade)

	"""
	Displays the analysis.
	"""
	def display(self, calc_weekly):
		print("\n-----   General Stats   -----")
		print("Total trades:", self.stats['count'])
		print("Break even trades", self.stats['break_even'])
		print("Net profit (in pips):", self.stats['profit'])
		print("Accuracy:", self.stats['acc'])
		print("Average win:", self.stats['win_avg'])
		print("Average loss:", self.stats['loss_avg'])
		print("Max consecutive win:", self.stats['max_consecutive_win'])
		print("Max consecutive loss:", self.stats['max_consecutive_loss'])

		if calc_weekly:
			print("\n-----   Weekly Stats   -----")
			for k, v in self.weekly.items():
				print(k, ":", v)

			print("\nNote that we exclude first and last week to avoid incomplete weeks.")

	"""
	Returns weekly statistics in a list.
	"""
	def weekly_stats(self, trades):
		if len(trades) < 1:
			return []

		weekly_stats = []
		week_of_trades = []
		curr_date = trades[0].entry_time.date()
		last_monday = None
		i = 0
		while i < len(trades):
			trade = trades[i]

			# Check new Monday
			if curr_date.weekday() == 0 and curr_date != last_monday:
				weekly_stats.append(self.trade_stats(week_of_trades))
				week_of_trades = []
				last_monday = curr_date

			if trade.entry_time.date() == curr_date:
				week_of_trades.append(trade)
				i += 1
				continue
				
			curr_date += timedelta(days=1)

			# BUG CHECK
			if curr_date > trades[-1].entry_time:
				print("Something went wrong...")
				print("curr_date can't be later than the entry to the last trade")


		return weekly_stats

	"""
	Compute further statistics on weekly stats.
	We exclude first and last weeks to account for
	incomplete weeks.
	"""
	def weekly_mean_dev_min_max(self, weekly_stats):
		res = {}
		blacklist = ['win_avg', 'loss_avg', 'max_consecutive_loss', 'max_consecutive_win', 'break_even']
		weekly_stats = weekly_stats[1:-1]

		res['week_count'] = len(weekly_stats)

		if res['week_count'] == 0:
			return res

		for key in weekly_stats[0].keys():
			if key not in blacklist:
				lst = [stat[key] for stat in weekly_stats]

				res[key+'_mean'] = round(np.mean(lst), 3)
				res[key+'_std'] = round(np.std(lst), 3)
				res[key+'_min'] = round(np.min(lst), 3)
				res[key+'_max'] = round(np.max(lst), 3)

		return res

	"""
	Returns statistics for a list of trades.
	"""
	def trade_stats(self, trades):
		stats = {'profit': 0,
				'count': 0,
				'break_even': 0,
				'win_avg': 0,
				'loss_avg': 0,
				'acc': 0.5,
				'max_consecutive_loss': 0,
				'max_consecutive_win': 0}
		win = 0
		loss = 0
		break_even = 0
		win_tot = 0
		loss_tot = 0
		max_con_loss = 0
		max_con_win = 0
		con_loss = 0
		con_win = 0

		for trade in trades:
			prof = (trade.profit)*10000
			stats['profit'] += prof
			stats['count'] += 1

			"""
			This function is used multiple times, we 
			only want to append balances on the first "main"
			call to this function, to set self.stats
			"""
			if not self.stats:
				self.balances.append(self.balances[-1]+prof)

			if prof > 0:
				win += 1
				win_tot += prof

				if con_loss != 0:
					if max_con_loss == 0 or con_loss < max_con_loss:
						max_con_loss = con_loss
					con_loss = 0

				con_win += prof

			elif prof < 0:
				loss += 1
				loss_tot += prof

				if con_win != 0:
					if max_con_win == 0 or con_win > max_con_win:
						max_con_win = con_win
					con_win = 0

				con_loss += prof

			else:
				break_even += 1


		# There may be no trades
		if trades:
			stats['profit'] = round(stats['profit'], 3)
			if win+loss != 0:
				stats['acc'] = round(win / (win+loss), 3)
			if loss != 0:
				stats['loss_avg'] = round(loss_tot / loss, 3)
			if win != 0:
				stats['win_avg'] = round(win_tot / win, 3)
			stats['max_consecutive_win'] = round(max_con_win, 3)
			stats['max_consecutive_loss'] = round(max_con_loss, 3)
			stats['break_even'] = break_even

		return stats


"""
Collects data from MetaTrader 5 and feeds
it to the Strategy passed in. After the
test ends, performs analysis on the results.
This class acts as the broker.
"""
class Tester:
	def __init__(self, strategy, symbol, start_date, end_date):
		self.strategy = strategy
		self.symbol = symbol
		self.start = start_date
		self.end = end_date


	def test(self):
		# {<timeframe> : [Bar, Bar, ...]}
		rates = {}
		for tf in self.strategy.tfs:
			raw_rates = mt5.copy_rates_range(self.symbol, tf, self.start, self.end)
			df_rates = pd.DataFrame(raw_rates)

			# convert time in seconds into the 'datetime' format
			df_rates['time']=pd.to_datetime(df_rates['time'], unit='s')

			rates[tf] = [Bar(row, tf) for index, row in df_rates.iterrows()]

		print("\nBars gathered for each timeframe:")
		for k, v in rates.items():
			print(k, ":", len(v))

		# {<timeframe> : <index of the next bar to be fed>}
		tf_index = {tf: 0 for tf, arr in rates.items()}
		while True:
			if self.__all_bars_fed(tf_index, rates):
				return

			# Count of bars fed across all timeframes
			fed_tfs = self.__feed_next_bar(tf_index, rates)
			if len(fed_tfs) > 0:
				self.strategy.on_new_bar(fed_tfs)


	"""
	Private helper method. Returns True 
	if we are done feeding the bars into 
	the strategy, False otherwise.
	"""
	def __all_bars_fed(self, tf_index, rates):
		for tf, i in tf_index.items():
			if len(rates[tf]) != i:
				return False

		return True

	"""
	Private helper method. Feeds upcoming
	bar(s) to the strategy. Returns the 
	number of bars fed.
	"""
	def __feed_next_bar(self, tf_index, rates):
		# Gather next bars of all timeframes
		potential_bars = []
		for tf, index in tf_index.items():
			if len(rates[tf]) == index:
				continue
			potential_bars.append(rates[tf][index])

		fed_tfs = []
		# Feed the earliest (can be many if we're working on multiple timeframes)
		earliest_time = min(potential_bars, key = lambda bar: bar.close_time).close_time
		for bar in potential_bars:
			if bar.close_time == earliest_time:
				self.strategy.feed_bar(bar)
				fed_tfs.append(bar.tf)
				tf_index[bar.tf] += 1

		return fed_tfs


"""
Represents a single bar of any timeframe.
"""
class Bar:
	def __init__(self, df_row, timeframe):
		self.initialize(df_row['time'],
						  df_row['open'],
						  df_row['high'],
						  df_row['low'],
						  df_row['close'],
						  df_row['tick_volume'],
						  df_row['spread'],
						  df_row['real_volume'],
						  timeframe)

	def initialize(self, time, open_, high, low, close, tick_volume, spread, real_volume, timeframe):
		self.open_time = time
		self.open = open_ # python has a built-in 'open' function!!!
		self.high = high
		self.low = low
		self.close = close
		self.tick_volume = tick_volume
		self.spread = spread
		self.real_volume = real_volume
		self.tf = timeframe
		if timeframe == mt5.TIMEFRAME_D1:
			self.close_time = self.open_time + timedelta(days=1)
		elif timeframe == mt5.TIMEFRAME_H8:
			self.close_time = self.open_time + timedelta(hours=8)
		elif timeframe == mt5.TIMEFRAME_H4:
			self.close_time = self.open_time + timedelta(hours=4)
		elif timeframe == mt5.TIMEFRAME_H1:
			self.close_time = self.open_time + timedelta(hours=1)
		elif timeframe == mt5.TIMEFRAME_M30:
			self.close_time = self.open_time + timedelta(minutes=30)
		elif timeframe == mt5.TIMEFRAME_M15:
			self.close_time = self.open_time + timedelta(minutes=15)
		elif timeframe == mt5.TIMEFRAME_M5:
			self.close_time = self.open_time + timedelta(minutes=5)
		elif timeframe == mt5.TIMEFRAME_M1:
			self.close_time = self.open_time + timedelta(minutes=1)
		else:
			print("Unimplemented TF:", timeframe)
			quit()


	def __str__(self):
		return str({'O': round(self.open, 5),
					'H': round(self.high, 5),
					'L': round(self.low, 5),
					'C': round(self.close, 5),
					'spread': self.spread,
					'time': self.time,
					'timeframe': self.tf})

	def get_oc_range(self):
		return abs(self.open - self.close)

	def get_hl_range(self):
		return abs(self.high - self.low)

"""
Represents an open position.
"""
class Position:
	def __init__(self, _type, entry_price, entry_time):
		self.type = _type
		self.entry_price = entry_price
		self.entry_time = entry_time


"""
Represents a completed trade.
"""
class Trade:
	def __init__ (self, entry_time, entry_price, exit_price, _type):
		self.entry_time = entry_time
		self.entry_price = entry_price
		self.exit_price = exit_price
		self.profit = exit_price - entry_price
		self.type = _type
		if _type == "sell":
			self.profit *= -1