import argparse

from channel  import Channel
from receiver import GBN_Receiver
from sender   import GBN_Sender

from gui import gui_main

def main():
    channel = Channel()
    sender = GBN_Sender(channel)
    receiver = GBN_Receiver(channel)

    sender.connect_receiver(receiver)
    receiver.connect_sender(sender)

    sender.send()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GBN simulation")
    parser.add_argument('--no-gui', action='store_false', help="Run with GUI interface")

    args = parser.parse_args()

    if args.no_gui:
        gui_main()
    else:
        main()
