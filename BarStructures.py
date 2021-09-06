"""
Module of functions. Each function returns true if
the corresponding bar structure is in place.

Naming convention:
consec = consecutive
pull = pull back bar

Bars that are passed in are in chronological order.
"""

def no_struct(bars):
	return True

def consec_bull(bars, count):
	if len(bars) < count:
		return False
	for bar in bars[-count:]:
		if bar.close < bar.open:
			return False
	return True

def consec_bear(bars, count):
	if len(bars) < count:
		return False
	for bar in bars[-count:]:
		if bar.close > bar.open:
			return False
	return True

def consec_bull_bear(bars, bull_count, bear_count):
	if len(bars) < bull_count + bear_count:
		return False
	return consec_bull(bars[:-bear_count], bull_count) and consec_bear(bars, bear_count)

def consec_bear_bull(bars, bear_count, bull_count):
	if len(bars) < bull_count + bear_count:
		return False
	return consec_bear(bars[:-bull_count], bear_count) and consec_bull(bars, bull_count)

def engulfing_bull(bars):
	if len(bars) < 2:
		return False

	bear_bull = consec_bear_bull(bars, 1, 1)
	engulf = bars[-1].close > bars[-2].open

	return bear_bull and engulf

def engulfing_bear(bars):
	if len(bars) < 2:
		return False

	bull_bear = consec_bull_bear(bars, 1, 1)
	engulf = bars[-1].close < bars[-2].open

	return bull_bear and engulf

def bottom_pin(bars):
	if len(bars) < 1:
		return False

	bear = consec_bear(bars, 1)
	body = bars[-1].get_oc_range()
	wick = bars[-1].get_hl_range()

	body += 0.00001 # in case body is 0.0, we add a point

	pin = wick/body > 3
	
	return bear and pin

def top_pin(bars):
	if len(bars) < 1:
		return False

	bull = consec_bull(bars, 1)
	body = bars[-1].get_oc_range()
	wick = bars[-1].get_hl_range()

	body += 0.00001 # in case body is 0.0, we add a point

	pin = wick/body > 3
	
	return bull and pin

def breaking_high(bars, ret_high=False):
	if len(bars) < 2:
		if ret_high:
			return False, 0
		return False 

	high = bars[0].open
	seen_bearish = False # no high, if there is no drop

	for bar in bars[:-1]:
		if bar.close > high:
			high = bar.close
			seen_bearish = False
		seen_bearish = seen_bearish or consec_bear([bar], 1)

	bu_break = consec_bull(bars, 1) and bars[-1].close > high

	retval = bu_break and seen_bearish

	if ret_high:
		return retval, high

	return retval

def breaking_high_pull(bars, pull_count):
	brk, high = breaking_high(bars, ret_high=True)
	if pull_count > 0:
		pullback = consec_bear(bars, pull_count) and bars[-1].close > high
	else:
		pullback = True

	return brk and pullback

def breaking_low(bars, ret_low=False):
	if len(bars) < 2:
		if ret_low:
			return False, 0
			
		return False 

	low = bars[0].open
	seen_bullish = False # no low, if there is no jump

	for bar in bars[:-1]:
		if bar.close < low:
			low = bar.close
			seen_bullish = False
		seen_bullish = seen_bullish or consec_bull([bar], 1)

	be_break = consec_bear(bars, 1) and bars[-1].close < low

	retval = be_break and seen_bullish

	if ret_low:
		return retval, low

	return retval

def breaking_low_pull(bars, pull_count):
	brk, low = breaking_low(bars, ret_low=True)
	if pull_count > 0:
		pullback = consec_bull(bars, pull_count) and bars[-1].close < low
	else:
		pullback = True

	return brk and pullback


funcs_list = [no_struct,
				engulfing_bull,
				engulfing_bear,
				bottom_pin,
				top_pin]