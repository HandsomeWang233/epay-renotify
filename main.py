import requests as req
import json
import hashlib

epay_url = "https://epay.com/"  # 不带/
pid = "1000"  # 商户id
key = "123"  # 商户密钥
notify_url = "https://abc.com/notify.php"  # 通知地址
header = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; V2023A; wv) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/62.0.3202.84 Mobile Safari/537.36 VivoBrowser/8.7.10.1'
}
out_trade_no = str(input("输入out_trade_no: "))   # 不带/


# 计算sign
def get_sign(params):
    global key
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    param_str = '&'.join(['{}={}'.format(key, value) for key, value in sorted_params])
    sign_str = param_str + key
    md5 = hashlib.md5()
    md5.update(sign_str.encode('utf-8'))
    sign = md5.hexdigest()
    return sign


def get_order():
    global param
    page = 1
    respond = req.get(f"{epay_url}/api.php?act=order&pid={pid}&key={key}&out_trade_no={out_trade_no}", headers=header)
    back_data = respond.content.decode('utf-8')
    order_data = json.loads(back_data)
    trade_no = order_data['trade_no']
    pay_type = order_data['type']
    money = order_data['money']
    epay_status = order_data['status']  # 1支付成功，0未支付
    param = {
        'trade_no': trade_no,
        'out_trade_no': out_trade_no,
        'money': money,
        'name': "product",
        'pid': pid,
        'type': pay_type,
        'trade_status': "TRADE_SUCCESS"
    }  # 用于计算sign进行补单
    return epay_status, trade_no, money, pay_type


def re_notify(trade_no, trade, pay_type, money, sign):
    respond = req.get(
        f"{notify_url}/?pid={pid}&trade_no={trade_no}&out_trade_no={trade}&type={pay_type}&name=product&money={money}&trade_status=TRADE_SUCCESS&sign={sign}&sign_type=MD5")
    if respond.content == "success":
        return True


def main():
    epay_status, trade_no, money, pay_type = get_order()
    sign = get_sign(param)
    if re_notify(trade_no, out_trade_no, pay_type, money, sign):
        print("补单成功")
    else:
        print("失败")


main()