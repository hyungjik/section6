# 로깅(logging)
import logging
import threading
import time

logging.basicConfig(
    level=logging.DEBUG,  # FATAL, INFO, ERROR 등 있음 운영일때는 주로 fatal, error로 개발중에는 info와 error로
    format='[%(levelname)s (%(threadName)-8s) %(message)s]'
)

def worker1():
    logging.debug('Starting')  # 메세지로 Starting이 들어감
    time.sleep(0.5)
    logging.debug('Exiting')

def worker2():
    logging.debug('Starting')  # 메세지로 Starting이 들어감
    time.sleep(0.5)
    logging.debug('Exiting')

# 데몬 쓰레드 : (옵션 생략 시 기본 쓰레드) 자주쓰진 않음
t1 = threading.Thread(name='service-1', target=worker1)  # threadName 지정해줌
t2 = threading.Thread(name='service-2', target=worker2, daemon=True)
t3 = threading.Thread(target=worker1, daemon=True)

if __name__ == "__main__":
    t1.start()
    t2.start()
    t3.start()

    # Join 메소드 호출로 쓰레드 종료시 까지 대기
    t1.join(100)  # join() 시간 동안 대기
    t2.join(100)
    print('t3 : isAlive() ', t3.isAlive()) # 쓰레드가 소멸상태인지 확인
    t3.join()
    print('t1 : isAlive() ', t1.isAlive()) # 쓰레드가 소멸상태인지 확인
