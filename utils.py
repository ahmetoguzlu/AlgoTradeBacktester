"""
Utilities for exploration. Specifically 
for operations with mt5 terminal.
"""
import MetaTrader5 as mt5

def check_connection():
	term_info = mt5.terminal_info()._asdict()

	if not term_info['connected']:
		print("Terminal isn't connected!")
		print("Quitting script.")
		mt5.shutdown() # Just in case
		quit()

def display_account_info():
	check_connection()

	acc_info = mt5.account_info()._asdict()

	print("\n\nAccount Info")
	print("-------------------------\n")
	for k in acc_info:
		print(k, ":", acc_info[k])

	print("\n\n")

def all_results_to_df_dict(all_results):
	if len(all_results) < 1:
		print("\nERROR: No results found!!\n")
		return

	df_dict = {}

	for k, v in all_results[0].items():
		for k2, v2 in v.items():
			df_dict[k2] = []

	flattened_results = []
	for result in all_results:
		f_res = {}
		for k,v in result.items():
			for k2, v2 in v.items():
				f_res[k2] = v2
		flattened_results.append(f_res)

	for result in flattened_results:
		for k, v in df_dict.items():
			if k in result:
				df_dict[k].append(result[k])
			else:
				df_dict[k].append("None")

	return df_dict