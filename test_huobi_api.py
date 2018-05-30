from common.HuobiClient import HuobiClient
import pandas as pd
import numpy as np
import time

from common.settings import HBP_SECRET_KEY, HBP_ACCESS_KEY


client = HuobiClient(api_key=HBP_ACCESS_KEY, api_secret=HBP_SECRET_KEY)
accounts = client.get_accounts()
# spot_id = 2828146
# margin_id = 3105263

spot_id = 3413401
margin_id = 3417614



res = client.get_balance(acct_id=margin_id)

