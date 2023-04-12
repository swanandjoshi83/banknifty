import requests
import pandas as pd
import time
import json
while True:
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8'}
    session = requests.Session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)

    spot_data = session.get(url, headers=headers, cookies=cookies).json()

    spot = spot_data['records']['data'][0]['PE']['underlyingValue']
    data = []
    response = session.get(url,headers=headers,cookies=cookies).json()
    rawdata = pd.DataFrame(response)
    rawop = pd.DataFrame(rawdata['filtered']['data']).fillna(0)
    for i in range(1,len(rawop)):
        calloi = callcoi = cltp = putoi = putcoi = pltp = 0
        stp = rawop['strikePrice'][i]
        if(rawop['CE'][i]==0):
            calloi = callcoi = callvol = 0
        else:
            calloi = rawop['CE'][i]['openInterest']
            callcoi = rawop['CE'][i]['changeinOpenInterest']
            callvol = rawop['CE'][i]['totalTradedVolume']
            cltp = rawop['CE'][i]['lastPrice']
            cltp_chg = rawop['CE'][i]['change']
        if(rawop['PE'][i] == 0):
            putoi = putcoi = putvol = 0
        else:
            putoi = rawop['PE'][i]['openInterest']
            putcoi = rawop['PE'][i]['changeinOpenInterest']
            putvol = rawop['PE'][i]['totalTradedVolume']
            pltp = rawop['PE'][i]['lastPrice']
            pltp_chg = rawop['PE'][i]['change']
        opdata = {
            'Call Openi': calloi, 'Call ChgOpeni': callcoi, 'Call LTP': cltp, 'Call per.chg': cltp_chg, 'Call Volume': callvol, 'Strike Price': stp,
            'Put Openi': putoi, 'Put ChgOpeni': putcoi, 'Put LTP': pltp, 'Put per.chg': pltp_chg, 'Put Volume': putvol, 'Spot': spot
        } 
        data.append(opdata)
    optionchain = pd.DataFrame(data)
    optionchain.to_csv('sorted_data.csv')
    print('Data received and stored')
    cookies = dict(request.cookies)
    response = requests.get(url, headers=headers).text
    data = json.loads(response)

    exp_list = data['records']['expiryDates']
    exp_date = exp_list[1]
    spot_data = session.get(url, headers=headers, cookies=cookies).json()
    spot = spot_data['records']['data'][1]['PE']['underlyingValue']

    ce = {}
    pe = {}
    n = 0
    m = 0

    for i in data['records']['data']:
        if i['expiryDate'] == exp_date:
            ce[n] = i['CE']
            n = n + 1
            pe[m] = i['PE']
            m = m + 1

    ce_def = pd.DataFrame.from_dict(ce).transpose()
    ce_def.columns += " Call"
    pe_def = pd.DataFrame.from_dict(pe).transpose()
    pe_def.columns += " Put"
    df = pd.concat([ce_def, pe_def], axis=1)

    # Save data to CSV file
    df.to_csv('option_data.csv', index=False)
    # Read CSV file
    # Read CSV file
    df = pd.read_csv('option_data.csv')

    # Merge Strike Price columns
    df['Strike Price'] = df['strikePrice Call'].fillna(df['strikePrice Put'])

    # Keep desired columns
    columns = ['openInterest Call', 'changeinOpenInterest Call', 'lastPrice Call', 'change Call', 'totalTradedVolume Call',
            'Strike Price', 'openInterest Put', 'changeinOpenInterest Put', 'lastPrice Put', 'change Put', 'totalTradedVolume Put',
                'underlyingValue Put']
    df = df[columns]

    # Rename columns
    df.columns = ['Call Openi', 'Call ChgOpeni', 'Call LTP', 'Call per.chg', 'Call Volume', 'Strike Price', 'Put Openi', 'Put ChgOpeni', 'Put LTP', 'Put per.chg', 'Put Volume', 'Spot']

    # Write to CSV file
    df.to_csv('nextsorted_data.csv', index=False)
    time.sleep(30)
        
