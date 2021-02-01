import requests
import urllib3
import pymongo


def get_request_by_episode(episode):
    params = {
        'method': 'getLottoNumber',
        'drwNo': episode
    }

    # verify=False SSL 무시
    req = requests.get('https://www.dhlottery.co.kr/common.do', params=params, verify=False)
    result = req.json()
    return result


def return_last_episode_in_db():
    # db connection
    conn = pymongo.MongoClient('localhost')
    db = conn.lotto_db
    collection = db.lotto

    # db에 저장된 마지막 회차 받아오기
    last_insert_episode = collection.find().sort('drwNo', -1).limit(1)

    # db 도큐먼트가 하나라도 있는지 확인
    try:
        last_episode = last_insert_episode.next()['drwNo']
    except StopIteration:
        last_episode = 0
    finally:
        conn.close()

    return last_episode


def insert_episode_to_db():
    # db connection
    conn = pymongo.MongoClient('localhost')
    db = conn.lotto_db
    collection = db.lotto

    # db에 저장된 마지막 회차보다 1큰 수 부터 받아온다
    count = return_last_episode_in_db() + 1
    while 1:
        # 회차별 get request
        lotto_result = get_request_by_episode(count)
        # 로또 정보가 있는지 확인
        if lotto_result['returnValue'] != 'success':
            break

        # db에 추가할 회차가 이미 저장되어 있는지 확인
        count_result = collection.count_documents({'drwNo': count})
        if count_result < 1:
            # db insert
            collection.insert_one(lotto_result)
            print(lotto_result)
        count = count + 1

    conn.close()


if __name__ == '__main__':
    # Warning log 없애기
    urllib3.disable_warnings()
    # db insert 절차 진행
    insert_episode_to_db()

# 출처 : https://myjamong.tistory.com/58 [로또 분석] 로또API 이용 pymongo로 당첨 정보 수집 :: 마이자몽