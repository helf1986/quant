def get_symbols(ex='huobipro'):

    if ex == 'huobipro':
        data = hb.get_symbols()
        keys = range(len(data['data']))
        values = data['data']
        symbol_info = pd.DataFrame.from_dict(dict(zip(keys, values)), orient='index')

        return symbol_info


def get_ticks(symbol_list, begin_time, end_time):
    '''
    提取指定时间段的历史Tick数据，支持单个代码提取或多个代码组合提取。
    :param symbol_list: string	证券代码, 带交易所代码以确保唯一，如SHSE.600000，同时支持多只代码
    :param begin_time: string	开始时间, 如2015-10-30 09:30:00
    :param end_time: string	结束时间, 如2015-10-30 15:00:00
    :return: Tick列表
    '''
    pass


def get_bars(symbol_list, bar_type, begin_time, end_time):
    '''
    提取指定时间段的历史Bar数据，支持单个代码提取或多个代码组合提取。
    :param symbol_list: 证券代码, 带交易所代码以确保唯一，如SHSE.600000，同时支持多只代码
    :param bar_type: bar周期，以秒为单位，比如60即1分钟bar
    :param begin_time: 开始时间, 如2015-10-30 09:30:00
    :param end_time: 结束时间, 如2015-10-30 15:00:00
    :return:
    '''
    pass


def get_hist(ex='huobipro', symbol = 'btcusd', field=['close'], begin = None, end=None):
    '''
    获取数字货币历史行情数据
    :param ex: 交易所名称
    :param symbol: 代码
    :param field: 字段
    :param begin: 开始时间
    :param end: 结束时间
    :return: 行情数据
    '''

    # 连接数据库
    client = MongoClient('localhost', 27017)
    coin_db = client['coindb']
    collection = coin_db['coin_market']

    mkt_data = collection.find({ "coin": symbol, "time": {"$gte": begin}, "time": {"$lte": end}})

    result = {}
    for each in mkt_data:
        result[each['time']] = each

    result_pd = pd.DataFrame.from_dict(result, orient='index')
    result_pd = result_pd.drop(['_id', 'id', 'count', 'time', 'ts'],axis=1)

    return result_pd


def get_tick(ex='huobipro', symbol = 'btcusd'):
    '''
    从交易所接口获取实时行情数据
    :param ex:
    :param symbol:
    :param field:
    :return:
    '''


    if ex == 'huobipro':
        data = hb.get_ticker(symbol=symbol)
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['ts']/1000))
        tick = data['tick']
        tick_df = pd.DataFrame.from_dict({ts: tick}, orient='index')

    return tick_df


def get_balance(ex='huobipro', acct_id=None):
    '''
    获取账户持仓情况
    :param ex: 交易所名称
    :param acct_id: 账户ID
    :return:
    '''
    if ex == 'huobipro':
        data = hb.get_balance(acct_id=acct_id)

        if data['status'] == 'ok':
            balance = data['data']['list']
            data_df = pd.DataFrame.from_dict(dict(zip(range(len(balance)), balance))).T
            data_df.index = data_df['currency']
            data_new = pd.DataFrame([], index=np.unique(data_df['currency']), columns=['trade', 'frozen'])
            data_new['trade'] = data_df[data_df['type']=='trade']['balance']
            data_new['frozen'] = data_df[data_df['type'] == 'frozen']['balance']
            data_new = data_new.astype('float')
            return data_new
        else:
            return None
