import time
import urllib.request
import datetime
from threading import Thread
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
 #declarations 
flow1=37 #main tank
flow21=35 #washbasin
flow22=15 #shower
ir=13 #ir sensor
minimum=0.5
GPIO.setup(flow1,GPIO.IN)
GPIO.setup(flow21,GPIO.IN)
GPIO.setup(flow22,GPIO.IN)
GPIO.setup(ir,GPIO.IN)
i=0
j=0
    
def wasteage() :
     #slow flowrate
    if flow(flow21)<minimum or flow(flow22)<minimum :
        msg(1)
           #leakage
    if flow(flow1)>(flow(flow21)+flow(flow22)) :
        msg(2)
    if flow(flow21)<0.2 :
        if flow(flow1)>flow(flow22) :
            msg(3)
    if flow(flow22)<0.2 :
        if flow(flow1)>flow(flow21) :
            msg(4)
def msg(y) : #options for app
    co=urllib.request.urlopen('https://api.thingspeak.com/update?api_key=KOK15FO9CD4REIXM&field1=%f'%y)
    co.read()
    co.close()
def datat() : #function for saving data in csv file
    a=flow(flow21)
    b=flow(flow22)
    '''co=urllib.request.urlopen('https://api.thingspeak.com/update?api_key=KOK15FO9CD4REIXM&field2={0}&field3={1}'.format(a,b))
    co.read()
    co.close()'''
    with open("/home/pi/rohit/so.csv","a") as log :
        k=datetime.datetime.now()
        log.write("{0},{1},{2}\n".format(a,b,k))
        
def checkshower() : #function for checking conditions at shower 
    
    if flow(flow22) >0.1 :
        k=datetime.datetime.now()+datetime.timedelta(minutes=15)
        while flow(flow22) >0.1 :
            if datetime.datetime.now()==k :
                msg(5)
                return
def washbasin() :  #function for checking conditions at washbasin
    if flow(flow21) >0.1 :
        if GPIO.input(ir) == False :
            k=datetime.datetime.now()+datetime.timedelta(seconds=40)
            while  GPIO.input(ir) ==False :
                time.sleep(1000)
                if datetime.datetime.now()==k :
                    msg(6)
                    return
            
            
            
    
def flow(a) :   #function for calculating flow rate
    rate_cnt=0
    tot_cnt=0
    minutes=0
    constant=0.10
    time_new=0.0
    stop_time=0.0
    gpio_last=2
    print("water app of %u"%a)
    for sec_mult in range(0,1) :
            time_new=time.time()+3
            rate_cnt=0
            while time.time() <= time_new :
                gpio_cur = GPIO.input(a)
                if gpio_cur !=  gpio_last :
                    rate_cnt += 1
                    tot_cnt += 1
                else :
                    rate_cnt = rate_cnt
                    tot_cnt = tot_cnt
                gpio_last = gpio_cur
                minutes += 1           
    print('\nLiters / min ',round(rate_cnt*constant,4))
    print('Total Liters ',round(tot_cnt * constant,4))
    print('Time (min & clock)',minutes, '\t',time.asctime(time.localtime(time.time())),'\n')
    z=round(rate_cnt*constant,4)
    if a==flow21 :
        co=urllib.request.urlopen('https://api.thingspeak.com/update?api_key=KOK15FO9CD4REIXM&field2=%f'%z)
    else :
        co=urllib.request.urlopen('https://api.thingspeak.com/update?api_key=KOK15FO9CD4REIXM&field3=%f'%z)
    co.read()
    co.close()
        
    return round(tot_cnt * constant,4);
            
           
        #thteads declarations 
while True :
    t1=Thread(wasteage())
    t2=Thread(checkshower())
    t3=Thread(washbasin())
    t4=Thread(datat())
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    
    
    
    
        
