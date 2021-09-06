# Ahmet Oguzlu
# https://www.mql5.com

from datetime import datetime
import MetaTrader5 as mt5
import BarStructureStrategy as bss
import pytz
import utils
import BarStructures as structs
import matplotlib.pyplot as plt
import pandas as pd

if not mt5.initialize():
	print("Failed to initialize!")
	quit()

if not mt5.login(44226735): # Demo Account with 10k balance
	print("Failed to login to Demo Account!")
	quit()

# utils.display_account_info()

tfs = [mt5.TIMEFRAME_D1,
		mt5.TIMEFRAME_H8,
		#mt5.TIMEFRAME_H4,
		#mt5.TIMEFRAME_H1,
		#mt5.TIMEFRAME_M30,
		#mt5.TIMEFRAME_M15,
		#mt5.TIMEFRAME_M5,
		#mt5.TIMEFRAME_M1,
		]

all_results = []
counter = 0
# 0 for buy, 1 for sell
for i in range(2):
	for struct in structs.funcs_list:
		for tf in tfs:
			for wait_count in range(2,4):
				print("Progress:", counter / (2*3*len(structs.funcs_list)))
				counter += 1

				tf_to_struct = {tf: [None, None]}
				tf_to_struct[tf][i] = struct

				strat = bss.BarStructureStrategy(tf_to_struct,
												wait_count)

				timezone = pytz.timezone("Etc/UTC") # Forex.com servers are on GMT+3
				t_from = datetime(2001, 1, 1, tzinfo=timezone)
				t_to = datetime(2021, 1, 1, tzinfo=timezone)

				# print("Beginning test:")
				# print("Start date:", t_from)
				# print("End date:", t_to)
				# print("Wait count:", wait_count)
				# begin_time = datetime.now()
				strat.test("EURUSD", t_from, t_to, calc_weekly=True, display=False)
				# print("\nTest completed.")
				# end_time = round((datetime.now() - begin_time).total_seconds(), 2)
				# print("Time elapsed:", end_time, "seconds\n\n")

				config = {}
				config['type'] = "buy" if i == 0 else "sell"
				config['struct'] = struct.__name__
				config['wait_count'] = wait_count
				config['timeframe'] = tf

				all_results.append({"config": config,
									"general_stats": strat.analyzer.stats,
									"weekly_stats": strat.analyzer.weekly})

				# plt.plot(strat.analyzer.balances)
				# plt.show()

df = pd.DataFrame(utils.all_results_to_df_dict(all_results))
df_html = df.to_html()

# write html to file
file = open("test_results.html", "w")
file.write(df_html)
file.close()


print("Shutting down connection.")
mt5.shutdown()
print("Script ended.")