import sensor, time, image, pyb, lcd, uos,utime
from pyb import UART

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # or sensor.GRAYSCALE
sensor.set_framesize(sensor.B128X128) # or sensor.QQVGA (or others)
sensor.skip_frames(10) # Let new settings take affect.
sensor.skip_frames(time = 2000)
lcd.init()
uart = UART(3,9600)
uart.init(9600, bits=8, parity=None, stop=1)

user_num = 2 #图像库中不同人数，一共6人
user_img = 15 #每人有20张样本图片
num=0
max_dif=9000
alldir=None
warn_num=0
RED_LED_PIN = 1
BLUE_LED_PIN = 3
pperson=None
warning_cnt=0
function=0
img=None


def openmv_receive():
    if uart.any():
        c = uart.read()
        c=c.decode('utf-8')
        return c

def receive_handle():
    global function
    data=openmv_receive()
    print(data)
    if(data=="1"):
        function=1
        time.sleep_ms(1500)
        warning_cnt=0
        data=openmv_receive()
    if(data=="2"):
        function=2
        time.sleep_ms(1500)
        warning_cnt=0
        data=openmv_receive()
    if(data=="open"):
        pyb.LED(BLUE_LED_PIN).on()   #蓝灯亮，代表开门
        time.sleep_ms(500)
        pyb.LED(BLUE_LED_PIN).off()  #红灯灭拍照结束
    if(data!="1" and data!="2" and data!=None):
        if(function==1):
            add_user(data)
        if(function==2):
            delete_user(data)
        function=0

def search_dir():
    global alldir,user_num,warn_num
    alldir=uos.listdir("pic")
    user_num=len(alldir)
    warn_num = sum(1 for s in alldir if "warn" in s)

def min(pmin,a,s):
    global pperson
    if a<pmin:
        pmin=a
        pperson=s
    return pmin,pperson

def match_person():
    global img
    global alldir,user_num,user_img,uart,max_dif,warning_cnt,warn_num
    cnt_list=[0]*user_num
    for i in range(1,11):
        cur_user,pmin=lbp_match()
        cnt_list[alldir.index(cur_user)]+=1
    if(max(cnt_list)>=7 and pmin<max_dif):
        final_user=alldir[cnt_list.index(max(cnt_list))]
        print(final_user)
        uart.write(final_user)
        if(final_user!="noperson" and "warn" not in final_user):
            pyb.LED(BLUE_LED_PIN).on()
            time.sleep_ms(2000)
            pyb.LED(BLUE_LED_PIN).off()
        warning_cnt=0
        utime.sleep(1)
    else:
        warning_cnt+=1
        if(warning_cnt==5):
            uart.write("warning")
            print("warning")
            add_user("warn_%d"%(warn_num+1))
            warn_num+=1
            utime.sleep(1)
            warning_cnt=0

def lbp_match():
    global img
    img = sensor.snapshot()
    d0 = img.find_lbp((0, 0, img.width(), img.height()))
    lcd.display(img)
    global user_img,user_num,alldir
    pmin=999999
    for person in alldir:
        dist = 0
        for i in range(2, user_img+1):
            img = image.Image("pic/%s/%d.pgm"%(person, i))
            d1 = img.find_lbp((0, 0, img.width(), img.height()))
            dist += image.match_descriptor(d0, d1)
        #print("Average dist for subject %s: %d"%(person, dist/user_img))
        pmin,person = min(pmin, dist/user_img,person)#特征差异度越小，被检测人脸与此样本更相似更匹配。
        #print(pmin)
    #print(person) # num为当前最匹配的人的编号。
    return person,pmin

def add_user(user):
    print("!!!")
    global user_img,user_num,alldir
    n=user_img
    uos.mkdir("pic/%s"%(user))
    alldir.append(user)
    pyb.LED(RED_LED_PIN).on()   #红灯亮起，拍照开始
    for i in range(1,16):
       sensor.snapshot().save("pic/%s/%s.pgm" % (user, n) )
       n-=1
       sensor.skip_frames(time = 200)#每隔0.3秒拍照一次
    pyb.LED(RED_LED_PIN).off()  #红灯灭拍照结束
    user_num+=1

def delete_user(user):
    global user_num,alldir
    #uos.rmdir("pic/%s"%(user))
    alldir.remove(user)
    print(alldir)
    user_num-=1

search_dir()

while(True):
    receive_handle()
    match_person()
