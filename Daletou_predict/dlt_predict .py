import requests
from bs4 import BeautifulSoup as bs
import threading
import queue
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.header import Header

class get_history(threading.Thread):
    def __init__(self,task_q,result_q):
        super().__init__()
        self.task_queue=task_q
        self.result_queue=result_q


    def run(self):
        while True:
            if not self.task_queue.empty():
                page=self.task_queue.get()
                one_result=self.crawl(page)
                self.result_queue.put(one_result)
                self.task_queue.task_done()
                #print('Page {} is finished'.format(page))
            else:
                break


    def crawl(self,page):
        url = 'http://www.lottery.gov.cn/historykj/history_{}.jspx?_ltype=dlt'.format(page)
        headers = {
            'user-agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 75.0.3770.142Safari / 537.36',
            'Upgrade-Insecure-Requests': '1',
            'Host': 'www.lottery.gov.cn'
        }
        r = requests.get(url, headers=headers)
        text = bs(r.text, 'lxml')
        result = text.find_all('div', class_='result')
        result = result[0].find_all('tbody')
        result = result[0].find_all('td')
        result_list = []
        for item in result:
            result_list.append(item.get_text())
        one_page=[]
        one_page.append([result_list[19]] + result_list[0:8])
        for i in range(1, 20):
            open_data = result_list[19 + (20 * i)]
            number_list = result_list[20 + (20 * (i - 1)):21 + (20 * (i - 1)) + 7]
            one_page.append([open_data] + number_list)
        return one_page


# Data collecting

print("Data collecting...")
task_queue=queue.Queue()
result_queue=queue.Queue()
for i in range(1,94):
    task_queue.put(i)

crawl=get_history(task_queue,result_queue)
crawl.setDaemon(True)
crawl.start()

task_queue.join()
print("Data collection is finished.")

# Data extracting
result=[]
while not result_queue.empty():
    for one in result_queue.get():
        one_line=''
        for item in one:
            one_line+=item
        result.append(one_line)

data=np.zeros((len(result),7))
for i in range(len(result)):
    for j in range(6):
        data[i][j]=int(result[i][-14+2*j:-12+2*j])
    data[i][6]=int(result[i][-2:])

# Build HMM
FdataCount=dict()
for i in range(2,len(data)):
    pprev=data[i-2][0]
    prev=data[i-1][0]
    pred=data[i][0]
    if pprev not in FdataCount:
        FdataCount[pprev]=dict()
    if prev not in FdataCount[pprev]:
        FdataCount[pprev][prev]=dict()
    if pred not in FdataCount[pprev][prev]:
        FdataCount[pprev][prev][pred]=0
    FdataCount[pprev][prev][pred]+=1

Fprobs=dict()
for pprev,prev in FdataCount.items():
    for prev,pred in prev.items():
        values = []
        probabilities = []
        sumall = 0
        for pred,count in pred.items():
            values.append(pred)
            probabilities.append(count)
            sumall += count
        for i in range(0, len(probabilities)):
            probabilities[i] /= float(sumall)
        if pprev not in Fprobs:
            Fprobs[pprev]=dict()
        Fprobs[pprev][prev] = (values, probabilities)

OdataCount=dict()
for i in range(1,len(data)):
    for j in range(1,5):
        pprev=data[i][j-1]
        prev=data[i-1][j]
        pred=data[i][j]
        if pprev not in OdataCount:
            OdataCount[pprev]=dict()
        if prev not in OdataCount[pprev]:
            OdataCount[pprev][prev]=dict()
        if pred not in OdataCount[pprev][prev]:
            OdataCount[pprev][prev][pred]=0
        OdataCount[pprev][prev][pred]+=1

Oprobs=dict()
for pprev,prev in OdataCount.items():
    for prev,pred in prev.items():
        values = []
        probabilities = []
        sumall = 0
        for pred,count in pred.items():
            values.append(pred)
            probabilities.append(count)
            sumall += count
        for i in range(0, len(probabilities)):
            probabilities[i] /= float(sumall)
        if pprev not in Oprobs:
            Oprobs[pprev]=dict()
        Oprobs[pprev][prev] = (values, probabilities)

SdataCount=dict()
for i in range(2,len(data)):
    pprev=data[i-2][5]
    prev=data[i-1][5]
    pred=data[i][5]
    if pprev not in SdataCount:
        SdataCount[pprev]=dict()
    if prev not in SdataCount[pprev]:
        SdataCount[pprev][prev]=dict()
    if pred not in SdataCount[pprev][prev]:
        SdataCount[pprev][prev][pred]=0
    SdataCount[pprev][prev][pred]+=1

Sprobs=dict()
for pprev,prev in SdataCount.items():
    for prev,pred in prev.items():
        values = []
        probabilities = []
        sumall = 0
        for pred,count in pred.items():
            values.append(pred)
            probabilities.append(count)
            sumall += count
        for i in range(0, len(probabilities)):
            probabilities[i] /= float(sumall)
        if pprev not in Sprobs:
            Sprobs[pprev]=dict()
        Sprobs[pprev][prev] = (values, probabilities)

SOdataCount=dict()
for i in range(1,len(data)):
    for j in range(6,7):
        pprev=data[i][j-1]
        prev=data[i-1][j]
        pred=data[i][j]
        if pprev not in SOdataCount:
            SOdataCount[pprev]=dict()
        if prev not in SOdataCount[pprev]:
            SOdataCount[pprev][prev]=dict()
        if pred not in SOdataCount[pprev][prev]:
            SOdataCount[pprev][prev][pred]=0
        SOdataCount[pprev][prev][pred]+=1

SOprobs=dict()
for pprev,prev in SOdataCount.items():
    for prev,pred in prev.items():
        values = []
        probabilities = []
        sumall = 0
        for pred,count in pred.items():
            values.append(pred)
            probabilities.append(count)
            sumall += count
        for i in range(0, len(probabilities)):
            probabilities[i] /= float(sumall)
        if pprev not in SOprobs:
            SOprobs[pprev]=dict()
        SOprobs[pprev][prev] = (values, probabilities)

def findMaxProb(value,prob):
    maxv=999
    maxp=0
    for i in range(len(value)):
        if prob[i]>maxp:
            maxv=value[i]
    return maxv

def predict():
    last=findMaxProb(Fprobs[data[-2][0]][data[-1][0]][0],Fprobs[data[-2][0]][data[-1][0]][1])
    prediction=[]
    prediction.append(last)
    for i in range(4):
        last=findMaxProb(Oprobs[last][data[-1][i+1]][0],Oprobs[last][data[-1][i+1]][1])
        prediction.append(last)
    last2=findMaxProb(Sprobs[data[-2][5]][data[-1][5]][0],Sprobs[data[-2][5]][data[-1][5]][1])
    prediction.append(last2)
    last3=findMaxProb(SOprobs[last2][data[-1][6]][0],Oprobs[last2][data[-1][6]][1])
    prediction.append(last3)
    print(prediction)
    return prediction



from_addr = '*****@email.com'
password = '******'
 
to_addr = '*********'
 
smtp_server = 'smtp.qq.com'
msg = MIMEText(str(predict()),'plain','utf-8')
 

msg['From'] = Header(from_addr)
msg['To'] = Header(to_addr)
msg['Subject'] = Header('本期大乐透预测')
 
server = smtplib.SMTP_SSL(smtp_server)
server.connect(smtp_server,465)
server.login(from_addr, password)
server.sendmail(from_addr, to_addr, msg.as_string())
server.quit()