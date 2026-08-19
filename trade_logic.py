from datetime import datetime,timedelta,time
import dukascopy_python as dk
import config as cfg
from telegram_functionality import send_telegram
import time as tm

def monitor_pair(pair_name, pair):
    pending_candle = None
    if pending_candle is not None:
        stream_start_time = pending_candle.name
    else:
        now = datetime.now()
        minute_floor = (now.minute // 15) * 15
        stream_start_time = now.replace(minute=minute_floor, second=0, microsecond=0)
    while True:
        try:
            data_stream =dk.live_fetch(
                pair,
                15,
                dk.TIME_UNIT_MIN,
                cfg.OFFER_SIDE,
                stream_start_time,
                cfg.END,
                False
            )

            

            #CHECK if DATA is SENT
            for new_data in data_stream:

                if new_data is None:
                    continue
                if new_data.empty:
                    continue

                # DATA
                current_candle = new_data.iloc[-1]
                timestamp = current_candle.name 

                #SEND only IN-SESSION SIGNALS
                if timestamp.date() in cfg.HOLIDAYS or not (cfg.SESSION_STARTTIME<=timestamp.time()<=cfg.SESSION_ENDTIME):
                    continue

                #First Loop Logic
                if pending_candle is None:
                    pending_candle = current_candle
                    print(f"🏁 {pair_name}: Tracking 15m candle starting at {timestamp.strftime('%H:%M')}")
                    continue

                #UPDATE DATA
                if timestamp == pending_candle.name :
                    pending_candle = current_candle

                #WHEN DATA CHANGES CHECK FINAL CANDLE
                elif timestamp > pending_candle.name:

                    final_c = pending_candle
                    
                    o = final_c['open']
                    c = final_c['close']
                    h = final_c['high']
                    l = final_c['low']
                    final_candle_time = (final_c.name + timedelta(hours=1)).strftime('%d.%m %H:%M')

                    is_green = c > o
                    if is_green and (o == l):
                        send_telegram(f"📈 🟢 Wickless Candle on {pair_name} at {final_candle_time}")
                    
                    elif not is_green and (o == h):
                        send_telegram(f"📉 🔴 Wickless Candle on {pair_name} at {final_candle_time}")
                    if is_green:
                        send_telegram(f"Normal 🟢 Candle on {pair_name} O:{o} H:{h} C:{c} L:{l} ")
                    else:
                        send_telegram(f"Normal 🔴 Candle on {pair_name} O:{o} H:{h} C:{c} L:{l} ")

                    pending_candle = current_candle
                    print(f"⏳ {pair_name}: Started new block {timestamp.strftime('%H:%M')}...")
        except Exception as e:
            print(f"⚠️ Stream crashed on {pair_name}: {e}", e)
            tm.sleep(3)
            continue