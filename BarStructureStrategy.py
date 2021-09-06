"""
Implements a simgple strategy for exploration.
"""
import StrategySuite as ss

class BarStructureStrategy(ss.Strategy):
	def __init__(self, tf_to_struct, wait_count, reverse=False):
		super().__init__(list(tf_to_struct.keys()))

		# <timeframe> : [<buy_cond>, <sell_cond>]
		self.tf_to_struct = tf_to_struct

		self.wait_count = wait_count
		self.reverse = reverse # Reverses buys and sells

		# How many smallerTF (STF) bars have passed since entry
		self.post_entry_bar_count = 0

		# TF of the active position
		self.pos_tf = None

	def on_new_bar(self, new_tfs):

		# Single open position at a time
		if len(self.positions) > 0:
			if self.pos_tf in new_tfs:
				self.post_entry_bar_count += 1

				if self.post_entry_bar_count == self.wait_count:
					exit = self.bars[self.pos_tf][-1].close
					if self.positions[0].type == "sell":
						pass
						# exit += stf_bars[-1].spread*0.00001
						# exit += self.bars[self.pos_tf][-1].spread*0.000002
					if self.positions[0].type == "buy":
						pass
						# exit -= self.bars[self.pos_tf][-1].spread*0.00001
						# exit -= self.bars[self.pos_tf][-1].spread*0.000002

					self.close_position(self.positions[0], exit)
					self.pos_tf = None
					self.post_entry_bar_count = 0

			return

		for tf in new_tfs:
			# Do nothing if there aren't enough bars
			if len(self.bars[tf]) < 10:
				continue

			buy_func, sell_func = self.tf_to_struct[tf]
			buy, sell = None, None
			if buy_func != None:
				buy = buy_func(self.bars[tf][-10:])
			if sell_func != None:
				sell = sell_func(self.bars[tf][-10:])

			if buy or sell:
				_type = None

				# NOTE: Will buy if both are satisfied
				if buy:
					_type = "buy" if not self.reverse else "sell"
				elif sell:
					_type = "sell" if not self.reverse else "buy"

				self.open_position(_type, self.bars[tf][-1].close, self.bars[tf][-1].close_time)
				self.pos_tf = tf