from machine import Pin,I2C
from mfrc522 import MFRC522
from pico_i2c_lcd import I2cLcd
import time 
import utime
import urequests
import _thread
import ufirebase as firebase
try:
  import urequests as requests
except:
  import requests
  
import network
import gc
 
buz=Pin(1,Pin.OUT) 
def buzzing():
    buz.high()
    utime.sleep_ms(170)
    buz.low()
    time.sleep(1)
  
i2c = I2C(1, sda=Pin(18), scl=Pin(19), freq=40000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
firebase.setURL("")

ssid = ''
password = ''
 

def connect_wifi(ssid, password):
  station = network.WLAN(network.STA_IF)
  station.active(True)
  station.connect(ssid, password)
  while station.isconnected() == False:
    pass
  print('Connection successful')
  print(station.ifconfig())

connect_wifi(ssid, password)
lcd.clear()
lcd.move_to(0,0)
lcd.putstr("WiFi connected")
time.sleep(2)
lcd.clear()
lcd.move_to(3,0)
lcd.putstr('Press NEW')

col_list=[8,9,10,11]
row_list=[12,13,14,15]
for x in range(0,4):
    row_list[x]=Pin(row_list[x], Pin.OUT)
    row_list[x].value(1)
for x in range(0,4):
    col_list[x] = Pin(col_list[x], Pin.IN, Pin.PULL_UP)
    
key_map=[["1","4","7",":"],\
        ["2","5","8","0"],\
        ["3","6","9","#"],\
        ["A","B","C","D"]]

def Keypad4x4Read(cols,rows):
  for r in rows:
    r.value(0)
    result=[cols[0].value(),cols[1].value(),cols[2].value(),cols[3].value()]
    if min(result)==0:
      key=key_map[int(rows.index(r))][int(result.index(0))]
      r.value(1) # manages key keept pressed
      return(key)
    r.value(1)
def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1

account_sid = ''
auth_token = ''
recipient_num = ''
sender_num = ''

def send_sms(recipient, sender,
             message, auth_token, account_sid):
      
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = "To={}&From={}&Body={}".format(recipient,sender,message)
    url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(account_sid)
    
    print("Sending SMS")
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr('Sending SMS')
    
    response = requests.post(url,
                             data=data,
                             auth=(account_sid,auth_token),
                             headers=headers)
    
    if response.status_code == 201:
        print("SMS sent!")
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr('SMS sent!')
        time.sleep(5)
        lcd.clear()
        lcd.move_to(3,0)
        lcd.putstr('Press NEW')
    else:
        print("Error sending SMS: {}".format(response.text))
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr("SMS can't be sent")
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr("Re-enter mobile no:")
        mobile()
    #response.close()

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=0)
pay=Pin(3,Pin.IN,Pin.PULL_UP)    
rem=Pin(2,Pin.IN,Pin.PULL_UP)
reset=Pin(16,Pin.IN,Pin.PULL_UP)
buz=Pin(1,Pin.OUT) 
    
def clr_line(text):
    lcd.move_to(0,1)
    lcd.putstr('                ')
    lcd.move_to(0,1)
    lcd.putstr(text)
    
def scroll_text(text):
    while True:
        text = text + ' ' * 2 # Add spaces to the end for smooth scrolling
        for i in range(len(text) - 16 + 1):
            lcd.putstr(text[i:i+16])  # Display 16 characters at a time
            time.sleep_us(1)
            
def mobile():
    s=[]
    phone=0
    while True:
        key=Keypad4x4Read(col_list, row_list)
        if key != None:
            utime.sleep_ms(100)
            if key!='D':
                if key=='A': # A - Delete
                    s=s[:-1]
                    clr_line(listToString(s))
                else:
                    s.append(key)
                    lcd.move_to(0,1)
                    lcd.putstr(listToString(s))
                    
            else:
                phone=s
                phone=listToString(phone)
                mob=f'+91{phone}'
                lcd.clear()
                lcd.move_to(0,0)
                lcd.putstr('Scan the Product')
                buzzing()
                recipient_num=mob
                break
        
    
            
def main():
    message=''
    dict={}
    s=[]
    phone=0
    counter=0
    account_sid = ''
    auth_token = ''
    recipient_num = ''
    sender_num = ''
    firebase.setURL("")
    mobile()
    while True:
        # Remove  item form cart
        if rem.value()==0:
            reader.init()
            (stat, tag_type) = reader.request(reader.REQIDL)
            if stat == reader.OK:
                (stat, uid) = reader.SelectTagSN()
                if stat == reader.OK:
                    buzzing()
                    card = int.from_bytes(bytes(uid),"little",False)
                    Card=str(card)
            #get data from fb
                    firebase.get(f"/Sheet1/{Card}/PRODUCT/",'data1', bg=0, id=0)
                    firebase.get(f"/Sheet1/{Card}/PRICE/",'data2', bg=0, id=0)
                    product=firebase.data1 
                    price=firebase.data2
                    del dict[product]
                    counter-=(price)
                    lcd.clear()
                    lcd.move_to(0,0)
                    lcd.putstr(f'{product} removed')
                    lcd.move_to(0,1)
                    lcd.putstr(f'Total:{counter}')
                    print(counter)
                    [print(i,':',j) for i, j in dict.items()]
        else:
            # Add item to the cart
            reader.init() 
            (stat, tag_type) = reader.request(reader.REQIDL)
            if stat == reader.OK:
                (stat, uid) = reader.SelectTagSN()
                if stat == reader.OK:
                    buzzing()
                    card = int.from_bytes(bytes(uid),"little",False)
                    Card=str(card)
            #get data from fb
                    firebase.get(f"/Sheet1/{Card}/PRODUCT/",'data1', bg=0, id=0)
                    firebase.get(f"/Sheet1/{Card}/PRICE/",'data2', bg=0, id=0)
                    product=firebase.data1 
                    price=firebase.data2
                    dict[product]=price
                    counter=counter+price
                    txt=f'{product}:{price}'
                    lcd.clear()
                    lcd.move_to(0,0)
                    lcd.putstr(f'{product}:{price}')
                    lcd.move_to(0,1)
                    lcd.putstr(f'Total:{counter}')
                    [print(i,':',j) for i, j in dict.items()]
            if pay.value()==0:
                break
            
    print('Total price:',counter)
    dict['Total ']=counter
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr(f'Total price: {counter}')
    lcd.move_to(0,1)
    lcd.putstr('Place smart card')
    firebase.setURL("/")
    while True:
        reader.init()
        (stat, tag_type) = reader.request(reader.REQIDL)
        if stat == reader.OK:
            (stat, uid) = reader.SelectTagSN()
            if stat == reader.OK:
                buz.high()
                utime.sleep_ms(170)
                buz.low()
                time.sleep(1)
                card = int.from_bytes(bytes(uid),"little",False)
                Card=str(card)
                firebase.get(str(Card),'data', bg=0, id=0)
                points=firebase.data
                if points<=0:
                    print('Insufficient amount')
                    lcd.clear()
                    lcd.move_to(0,0)
                    lcd.putstr('Insufficient amount')
                    lcd.move_to(0,1)
                    lcd.putstr('Recharge S-card')
                else:
                    points-=counter
                    firebase.put(str(Card),points,bg=0,id=0)
                    print('Amount paid')
                    lcd.clear()
                    lcd.move_to(0,0)
                    lcd.putstr('Amount paid')
                    message=''
                    for key,value in dict.items():
                        s=f"{key}:{value}"
                        message=message+'\n'+s
                    message=message
                    print(message)
                    time.sleep(2)
                    send_sms(recipient_num, sender_num, message, auth_token, account_sid)
                    break
    
while True:
    if reset.value()==0:
        lcd.clear()
        lcd.move_to(2,0)
        lcd.putstr('---Clear---')
        time.sleep(1)
        lcd.move_to(0,0)
        lcd.putstr('Enter Ph.no:')
        main()

    
    
            
              

        
    

