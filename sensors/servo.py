import RPi.GPIO as GPIO
import time

# Ayarlar
servo_pin = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50) 
pwm.start(7)

# Mevcut konumu takip etmek için bir değişken
current_dc = 7.0

def yavas_hareket(hedef_dc, hiz=0.05):
    """
    hedef_dc: Gitmek istediğiniz DutyCycle değeri
    hiz: Her adım arasındaki bekleme süresi (küçüldükçe hızlanır)
    """
    global current_dc
    
    # Hedefe doğru küçük adımlarla ilerle (0.1 birimlik adımlar)
    adim = 0.1 if hedef_dc > current_dc else -0.1
    
    while abs(current_dc - hedef_dc) > 0.05:
        current_dc += adim
        pwm.ChangeDutyCycle(current_dc)
        time.sleep(hiz) # Bu süre ne kadar büyükse servo o kadar yavaş döner
    
    # Tam hedef noktasına sabitle
    pwm.ChangeDutyCycle(hedef_dc)
    current_dc = hedef_dc

try:
    for ii in range(0, 3):
        print("0 dereceye gidiyor (Yavaş)...")
        yavas_hareket(2.0, 0.01) # 0.02 saniye bekleme ile
        time.sleep(0.5)
        
        print("180 dereceye gidiyor (Daha Yavaş)...")
        yavas_hareket(12.0, 0.01) # 0.05 saniye bekleme ile daha da yavaş
        time.sleep(0.5)
        
        print("90 dereceye gidiyor...")
        yavas_hareket(7.0, 0.01)
        time.sleep(0.5)

except KeyboardInterrupt:
    pass

pwm.ChangeDutyCycle(0)
pwm.stop()
GPIO.cleanup()
