import time

from flask import Flask, jsonify

from config import AMOUNT_LIMITS_CONFIG

app = Flask(__name__)

limits = dict(sorted(AMOUNT_LIMITS_CONFIG.items()))
max_limit = max(AMOUNT_LIMITS_CONFIG)


class requests:
    _storage = []

    @classmethod
    def register(cls, amount):
        cls._storage.append((amount, time.time()))

    @classmethod
    def purge(cls):
        actual_time = time.time() - max_limit
        for i, (_, _time) in enumerate(cls._storage):
            if _time >= actual_time:
                cls._storage = cls._storage[i:]
                return

    @classmethod
    def verify(cls, new_amount):
        cls.purge()
        for interval in filter(lambda i: new_amount > limits[i], limits):
            return f'{limits[interval]}/{interval}'
        sums, now = {interval: 0 for interval in limits}, time.time()
        for _amount, _time in cls._storage:
            dt = now - _time
            for interval, limit in limits.items():
                if dt < interval:
                    sums[interval] += _amount
                    if sums[interval] + new_amount > limit:
                        return f'{limit}/{interval}'


@app.route('/request/<int:amount>')
def request(amount):
    limit = requests.verify(amount)
    if limit:
        result = {'error': f'amount limit exceeded ({limit}sec)'}
    else:
        result = {'result': 'OK'}
        requests.register(amount)
    return jsonify(result)
