import threading as td
from dukascopy_python.instruments import *
from telegram_functionality import send_telegram
import trade_logic as tl
import config as cfg
from threading_function import threading


def main():

    #PROCESSES
    threads=[]
    send_telegram("🤖 Bot connected! Waiting for signals...")

    #For Every Pair run a Thread
    threading(threads)

    print(f"Bot is running on {len(threads)} pairs. Press Ctrl+C to stop.")

    try:
        while True:
            td.Event().wait(1)
    except KeyboardInterrupt:
        print("Stopping bot...")

if __name__ == "__main__":
    main()
