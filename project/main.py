from typing import NoReturn

from app_interfaces.i_messages_source import IMessagesSource


def main() -> NoReturn:
    while True:
        command_source.wait_command()

    return


command_source: IMessagesSource = ...

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Goodbye!")
