from pytonconnect import TonConnect

import config
from replenishment.tc_storage import TcStorage


def get_connector(user_id: int):
    return TonConnect(config.MANIFEST_URL, storage=TcStorage(user_id))
