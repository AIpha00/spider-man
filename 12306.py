# coding: utf-8
# author: AIpha
# version: 1.0
'''
    此程序谨为学习研究使用，禁止商用。若需要转载或有任何问题需要提问，
    请联系邮箱：AIphalv0010@gmail.com
'''


import requests
import time
import re
import base64
import os
import json
from prettytable import PrettyTable
from datetime import datetime
from urllib import parse


session = requests.session()
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}
noSeat            = 'WZ' #无座
firstClassSeat    = 'M'  #一等座
secondClassSeat   = 'O'  #二等座
advancedSoftBerth = '6'  #高级软卧 A6
hardBerth         = '3'  #硬卧 A3
softBerth         = '4'  #软卧 A4
moveBerth         = 'F'  #动卧
hardSeat          = '1'  #硬座 A1
businessSeat      = '9'  #商务座 A9





def get_captcha():
    # 获取12306验证码图片的base64编码
    tmp = int(time.time() * 1000)
    create_captcha_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&%d' % tmp
    response = session.get(create_captcha_url, headers=headers)
    images = re.findall(r'"image":"(.*?)"', response.text)
    # captcha_url = 'data:image/jpg;base64,{}'.format(images[0])
    # res_captcha = requests.get(captcha_url)
    return images[0]


def save_captcha(captcha):
    # 将验证码用base64解码并保存
    if captcha:
        with open('./captcha.jpg', 'wb') as f:
            f.write(base64.b64decode(captcha))


def login(login_url):
    # 登陆模块
    # 12306登陆接口检查是否登陆，若无这个请求登陆的POST请求无法接收服务器响应
    uamtk_static_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk-static'
    data_uam = {
        'appid': 'otn',
    }
    uamtk_res = session.post(url=uamtk_static_url, data=data_uam, headers=headers).json()
    if uamtk_res['result_code'] == '1':
        print('-----用户未登陆----')
    captcha_res = input('请输入验证码对应坐标:')
    # # username = input('请输入用户名：')
    # # password = input('请输入密码：')
    # 将验证码图片进行切分
    coordinates = {'1': '35,35',  '2': '105,35',  '3': '175,35', '4': '245,35',
                   '5': '35,105', '6': '105,105', '7': '175,105', '8': '245,105'}
    rightImgCoordinates = []
    for i in captcha_res.split(','):
        rightImgCoordinates.append(coordinates[i])
    captcha_res = ','.join(rightImgCoordinates)

    data = {
        'username': 18084076919,
        'password': '960722tr',
        'answer': captcha_res,
        'appid': 'otn',
    }
    data_check_captcha = {
        'answer': captcha_res,
        'rand': 'sjrand',
        'login_site': 'E',
    }
    # 验证码验证
    check_captcha_url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
    check_captcha = session.get(url=check_captcha_url, params=data_check_captcha, headers=headers).json()
    print(check_captcha)
    if check_captcha['result_code'] == '4':
        print('--------验证码校验成功--------')
    else:
        print('------验证码输入错误请重新输入------')
        return
    res_login = session.post(url=login_url, data=data, headers=headers).json()
    if res_login['result_code'] != 0:
        print('----用户名或密码错误，请重新输入---')
    uamtk_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'

    uamtk = session.post(url=uamtk_url, data=data_uam, headers=headers).json()
    new_tk = uamtk['newapptk']
    uamauthclient = 'https://kyfw.12306.cn/otn/uamauthclient'
    clientdata = {
        'tk': new_tk,
    }
    my12306 = session.post(url=uamauthclient, data=clientdata, headers=headers).json()

    init12306Api = 'https://kyfw.12306.cn/otn/index/initMy12306Api'
    initmy12306 = session.post(url=init12306Api, headers=headers).json()
    print(initmy12306)
    # 进行登陆验证判断
    if my12306['username']:
        username = my12306['username']
    # check_login = session.post('https://kyfw.12306.cn/otn/login/conf')
        print('-----恭喜{}大佬成功登陆12306铁路购票系统-----'.format(username))
        return username
    # if res_login != '':
    #     print('登陆失败请重新开始，我不会帮你重启软件的自己重启程序好好输密码!')
    # if check_login:
    #     print('-----恭喜成功登陆12306铁路购票系统-----')
    #     buy_ticket()
    # else:
    #     print('登陆失败请重新开始，我不会帮你重启软件的自己重启程序好好输密码!')




def station_code():
    '''获取车站电码'''
    station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
    if os.path.exists('./stationcode.txt'):
        return
    res_station = session.get(url=station_url, headers=headers)
    stations = re.findall(r'([\u4e00-\u95fa5]+)\|([A-Z]+)', res_station.text)
    with open('./stationcode.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(dict(stations), ensure_ascii=False))


def getcodedict():
    with open('./stationcode.txt', 'r', encoding='utf-8') as file:
        dict = json.load(file)
        return dict


def query_ticket():
    '''查询车票信息接口'''
    uamtk_static_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk-static'
    data_uam = {
        'appid': 'otn',
    }
    uamtk_res = session.post(url=uamtk_static_url, data=data_uam, headers=headers).json()
    if uamtk_res['result_code'] == '1':
        print('-----用户未登陆----')
    codedict = getcodedict()
    query_url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'
    from_station = input('请输入出发地：')
    to_station = input('请输入目的地：')
    go_time = input('请输入出发日期：（请以“1990-11-11”为格式）')
    from_station_code = codedict[from_station]
    to_station_code = codedict[to_station]
    query_data = {
        'leftTicketDTO.train_date': go_time,
        'leftTicketDTO.from_station': from_station_code,
        'leftTicketDTO.to_station': to_station_code,
        'purpose_codes': 'ADULT',  # 购票类型
    }
    # 保存用户信息
    queryData = {
        'fromStation': from_station,
        'toStation': to_station,
        'trainDate': go_time,
        'fromStationCode': from_station_code,
        'toStationCode': to_station_code,
    }


    query_res = session.get(url=query_url, params=query_data, headers=headers)
    # print(query_res.json())
    traindicts = gettraininfo(query_res.json(), queryData)
    return queryData, traindicts  # 返回查询数据和车次信息

def gettraininfo(result, querydata):
    trainDict = {} # 车次信息字典
    trainDicts = [] # 用于订票
    trains = [] # 控制台打印

    results = result['data']['result']
    maps = result['data']['map']

    for item in results:
        trainInfo = item.split('|')
        if trainInfo[11] == 'Y':
            trainDict['secretStr'] = trainInfo[0]

            trainDict['trainNumber'] = trainInfo[2]  # 5l0000D35273

            trainDict['trainName'] = trainInfo[3]  # 车次名称，如D352

            trainDict['fromTelecode'] = trainInfo[6]  # 出发地电报码

            trainDict['toTelecode'] = trainInfo[7]  # 出发地电报码

            trainDict['fromStation'] = maps[trainInfo[6]]  # 上海

            trainDict['toStation'] = maps[trainInfo[7]]  # 成都

            trainDict['departTime'] = trainInfo[8]  # 出发时间

            trainDict['arriveTime'] = trainInfo[9]  # 到达时间

            trainDict['totalTime'] = trainInfo[10]  # 总用时

            trainDict['leftTicket'] = trainInfo[12]  # 余票

            trainDict['trainDate'] = trainInfo[13]  # 20180822

            trainDict['trainLocation'] = trainInfo[15]  # H2

            # 以下顺序貌似也不是一直固定的，我遇到过代表硬座的几天后代表其他座位了
            trainDict[businessSeat] = trainInfo[32]  # 商务座

            trainDict[firstClassSeat] = trainInfo[31]  # 一等座

            trainDict[secondClassSeat] = trainInfo[30]  # 二等座

            trainDict[advancedSoftBerth] = trainInfo[21]  # 高级软卧

            trainDict[softBerth] = trainInfo[23]  # 软卧

            trainDict[moveBerth] = trainInfo[33]  # 动卧

            trainDict[noSeat] = trainInfo[26]  # 无座

            trainDict[hardBerth] = trainInfo[28]  # 硬卧

            trainDict[hardSeat] = trainInfo[29]  # 硬座

            trainDict['otherSeat'] = trainInfo[22]  # 其他
            # 如果值为空，则将值修改为'--'
            for key in trainDict.keys():
                if trainDict[key] == '':
                    trainDict[key] = '--'


            train = [trainDict['trainName'] + '[ID]' if trainInfo[18] == '1' else trainDict['trainName'],
                     trainDict['fromStation'] + '\n' + trainDict['toStation'],
                     trainDict['departTime'] + '\n' + trainDict['arriveTime'],
                     trainDict['totalTime'], trainDict[businessSeat], trainDict[firstClassSeat],
                     trainDict[secondClassSeat], trainDict[advancedSoftBerth], trainDict[softBerth],
                     trainDict[moveBerth], trainDict[hardBerth], trainDict[hardSeat],
                     trainDict[noSeat],
                     trainDict['otherSeat']]

            # 直接使用append方法将字典添加到列表中，如果需要更改字典中的数据，那么列表中的内容也会发生改变，这是因为dict在Python里是object，不属于primitive
            # type（即int、float、string、None、bool)。这意味着你一般操控的是一个指向object（对象）的指针，而非object本身。下面是改善方法：使用copy()
            trains.append(train)
            trainDicts.append(trainDict.copy())  # 注意trainDict.copy()

    prettyPrint(trains, querydata)  # 按照一定格式打印
    return trainDicts


def prettyPrint(trains, querydata):
    '''打印车次信息使用prettyteble模块对信息进行规整并打印'''
    header = ["车次", "车站", "时间", "历时", "商务座", "一等座", "二等座", '高级软卧', "软卧", "动卧", "硬卧", "硬座", "无座", '其他']
    pt = PrettyTable(header)
    date = querydata['trainDate']
    title = '{}——>{}({} {}),共查询到{}个可购票的车次'.format(querydata['fromStation'], querydata['toStation'],
                                                  getDateFormat(date), getWeekDay(date), len(trains))
    pt.title = title
    pt.align["车次"] = "l"  # 左对齐
    for train in trains:
        pt.add_row(train)
    print(pt)


def getDateFormat(date):
    # date格式为2018-08-08
    dateList = date.split('-')
    if dateList[1].startswith('0'):
        month = dateList[1].replace('0', '')
    else:
        month = dateList[1]
    if dateList[2].startswith('0'):
        day = dateList[1].replace('0', '')
    else:
        day = dateList[2]
    return '{}月{}日'.format(month, day)


def getWeekDay(date):
    weekDayDict = {
        0: '周一',
        1: '周二',
        2: '周三',
        3: '周四',
        4: '周五',
        5: '周六',
        6: '周天',
        }
    day = datetime.strptime(date, '%Y-%m-%d').weekday()
    return weekDayDict[day]




def buy_ticket(username):
    '''购买车票方法'''
    querydata, trainDicts = query_ticket()
    seattype = input('请输入车票类型,WZ无座,F动卧,M一等座,O二等座,1硬座,3硬卧,4软卧,6高级软卧,9商务座:\n')
    i = 0
    for trainDict in trainDicts:
        if trainDict[seattype]== '有' or trainDict[seattype].isdigit():
            print('为您选择的车次为{},正在为您抢票中……'.format(trainDict['trainName']))
            submitOrderRequest(querydata,trainDict)
            getPassengerDTOs(seattype,username,trainDict)
            return
        else:
            i += 1
            if i >=len(trainDicts):  # 遍历所有车次后都未能查到座位，则打印错误信息
                print('Error:系统未能查询到{}座位类型存有余票'.format(seattype))
            continue

    # first_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
    # f_data = {
    #     '_json_att': '',
    # }
    # checkinfo = session.post(url=first_url, data=f_data, headers=headers)


def submitOrderRequest(querydata,trainDict):
    '''提交订单信息函数'''
    check_user = 'https://kyfw.12306.cn/otn/login/checkUser'
    check_data = {
        '_json_att': '',
    }
    check_user = session.post(url=check_user, data=check_data,headers=headers).json()

    if check_user['status']:
        submitorderrequest_url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        now_datetime = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        order_data = {
            'secretStr': parse.unquote(trainDict['secretStr']).replace('\n', ''),
            'train_date': querydata['trainDate'],
            'back_train_date': now_datetime,
            'tour_flag': 'dc',
            'purpose_codes': 'ADULT',
            'query_from_station_name': querydata['fromStation'],
            'query_to_station_name': querydata['toStation'],
            'undefined': '',
        }
        order_header = {
            'Content-Length': str(len(order_data)),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }

        order_dict = session.post(url=submitorderrequest_url, data=order_data, headers=order_header).json()
        print(order_dict)

        if order_dict['status']:
            print('提交预定车票订单请求成功')
        elif order_dict['messages'] != []:
            if order_dict['messages'][0] == '车票信息已过期，请重新查询最新车票信息':
                print('------请重新查询车票信息------')
        else:
            print('-----提交订单请求失败--------')
    else:
        print('登陆信息失效请重新登陆')


def getPassengerDTOs(seattype,username,trainDict):
    '''获取12306购票的token信息'''
    initdc_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
    s_data = {
        '_json_att': '',
    }

    initdc_res = session.post(url=initdc_url, data=s_data, headers=headers)
    try:
        repeatSubmitToken = re.findall(r"var globalRepeatSubmitToken = '(.*?)'", initdc_res.text)[0]
        keyCheckIsChange = re.findall(r"key_check_isChange':'(.*?)'", initdc_res.text)[0]
        # print('key_check_isChange:'+ keyCheckIsChange)
        # return repeatSubmitToken, keyCheckIsChange
    except:
        print('获取Token参数失败')
        return


    t_data = {
        '_json_att': '',
        'REPEAT_SUBMIT_TOKEN': repeatSubmitToken,
    }

    DTOs_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
    DTOs_res = session.post(url=DTOs_url, data=t_data, headers=headers)
    passengers = DTOs_res.json()['data']['normal_passengers']
    # print(passengers)
    # 获取车次队列信息
    for passenger in passengers:
        if passenger['passenger_name'] == username:
            # step 3: Check order
            checkorder_info(seattype, repeatSubmitToken, passenger)
            # step 4:获取队列
            getQueueCount(seattype, repeatSubmitToken, keyCheckIsChange, trainDict, passenger)
            return
        else:
            print('无法购票')


def checkorder_info(seattype, repeatsubmittoken,passenger):
    '''检查订单信息'''
    order_url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
    passenger_ticketstr = '{},{},{},{},{},{},{},N'.format(seattype, passenger['passenger_flag'],
                                                          passenger['passenger_type'],
                                                          passenger['passenger_name'],
                                                          passenger['passenger_id_type_code'],
                                                          passenger['passenger_id_no'],
                                                          passenger['mobile_no'])
    oldPassengerStr = '{},{},{},3_'.format(passenger['passenger_name'], passenger['passenger_id_type_code'],
                                           passenger['passenger_id_no'])

    checkorder_data = {
                           'cancel_flag': '2',
                           'bed_level_order_num': '000000000000000000000000000000',
                            'passengerTicketStr': passenger_ticketstr,
                            'oldPassengerStr': oldPassengerStr,
                            'tour_flag': 'dc',
                            'randCode':'',
                            'whatsSelect': 1,
                            '_json_att': '',
                            'REPEAT_SUBMIT_TOKEN': repeatsubmittoken,
    }

    order_res = session.post(url=order_url, data=checkorder_data, headers=headers)
    order_dict = order_res.json()
    print(order_dict)
    if order_dict['data']['submitStatus']:
        print('校验订单信息成功')
        if order_dict['data']['ifShowPassCode'] == 'Y':
            print('请重新验证')
            return True
        if order_dict['data']['ifShowPassCode'] == 'N':
            return False
    else:
        print('系统校验订单信息失败，请联系管理员')
        return False


def getQueueCount(seatType, repeatSubmitToken, keyCheckIsChange, trainDict, passenger):
    '''获取队列信息函数'''
    queue_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
    data = {
        '_json_att': '',
            'fromStationTelecode': trainDict['fromTelecode'],
            'leftTicket': trainDict['leftTicket'],
            'purpose_codes': '00',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken,
            'seatType': seatType,
            'stationTrainCode': trainDict['trainName'],
            'toStationTelecode': trainDict['toTelecode'],
            'train_date': getTrainDate(trainDict['trainDate']),
            'train_location': trainDict['trainLocation'],
            'train_no': trainDict['trainNumber'],
        }

    res = session.post(url=queue_url, data=data, headers=headers)

    if res.json()['status']:
        print('系统获取队列信息成功')
        confirmSingleForQueue(seatType, repeatSubmitToken, keyCheckIsChange, passenger, trainDict)

    else:
        print('系统获取队列信息失败')
        return


def confirmSingleForQueue(seatType, repeatSubmitToken, keyCheckIsChange, passenger, trainDict):
    '''获取提交订单信息并拿到返回值，到此订单完成程序结束'''
    confirm_url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
    passengerTicketStr = '{},{},{},{},{},{},{},N'.format(seatType, passenger['passenger_flag'],
                                                             passenger['passenger_type'],
                                                             passenger['passenger_name'],
                                                             passenger['passenger_id_type_code'],
                                                             passenger['passenger_id_no'],
                                                             passenger['mobile_no'])

    oldPassengerStr = '{},{},{},3_'.format(passenger['passenger_name'], passenger['passenger_id_type_code'],
                                               passenger['passenger_id_no'])

    data = {
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldPassengerStr,
            'randCode': '',
            'purpose_codes': '00',
            'key_check_isChange': keyCheckIsChange,
            'leftTicketStr': trainDict['leftTicket'],
            'train_location': trainDict['trainLocation'],
            'choose_seats': '',
            'seatDetailType': '000',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken,
        }

    res = session.post(url=confirm_url, data=data, headers=headers)
    print(res.json())
    if res.json()['data']['submitStatus']:
        print('已完成订票，请前往12306进行支付')
    else:
        print('订票失败,请稍后重试!')


def getTrainDate(dateStr):
        # 返回格式 Wed Aug 22 2018 00: 00:00 GMT + 0800 (China Standard Time)
        # 转换成时间数组
    timeArray = time.strptime(dateStr, "%Y%m%d")
    # 转换成时间戳
    timestamp = time.mktime(timeArray)
    # 转换成localtime
    timeLocal = time.localtime(timestamp)
    # 转换成新的时间格式
    GMT_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0800 (China Standard Time)'
    timeStr = time.strftime(GMT_FORMAT, timeLocal)
    return timeStr


if __name__ == '__main__':
    '''这里可以写成main函数形式
    后续可以增加循环以及多线程提升抢票的效率
    '''

    login_url = 'https://kyfw.12306.cn/passport/web/login'
    captcha = get_captcha()
    save_captcha(captcha)
    username = login(login_url)
    buy_ticket(username)