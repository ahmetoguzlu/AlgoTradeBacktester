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

# if not mt5.login(44226735): # Demo Account with 10k balance
# 	print("Failed to login to Demo Account!")
# 	quit()

# utils.display_account_info()

for wait_count in [1]:
	f1 = lambda bars: structs.consec_bear(bars, 7)
	f2 = lambda bars: structs.consec_bull(bars, 7)

	strat = bss.BarStructureStrategy({mt5.TIMEFRAME_M30: [f1,f2]},
									wait_count)

	timezone = pytz.timezone("Etc/UTC") # Forex.com servers are on GMT+3
	t_from = datetime(2018, 1, 1, tzinfo=timezone)
	t_to = datetime(2021, 1, 1, tzinfo=timezone)

	print("Beginning test:")
	print("Start date:", t_from)
	print("End date:", t_to)
	print("Wait count:", wait_count)
	begin_time = datetime.now()
	strat.test("EURUSD", t_from, t_to, calc_weekly=True, display=True)
	print("\nTest completed.")
	end_time = round((datetime.now() - begin_time).total_seconds(), 2)
	print("Time elapsed:", end_time, "seconds\n\n")

	# plt.plot(strat.analyzer.balances)
	# plt.show()

print("Shutting down connection.")
mt5.shutdown()
print("Script ended.")