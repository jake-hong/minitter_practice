import config
import pytest
import json 
import bcrypt

from app import create_app 
from sqlalchemy import create_engine,text


database = create_engine(config.test_config['DB_URL'], encoding='utf-8',max_overflow=0)

def setup_function():
    ## Create a test user 
    hashed_password =bcrypt.hashpw(b'test1234',bcrypt.gensalt())
    new_users = {
        'id'      : 1, 
        'name'    : '홍성은',
        'email'   : 'hongse21@gmail.com',
        'profile' : 'test profile',
        'hashed_password' : hashed_password
    }, {
        'id'      : 2, 
        'name'    : 'jake',
        'email'   : 'jake21@gmail.com',
        'profile' : 'test profile',
        'hashed_password' : hashed_password
    }
    database.execute(text("""
    INSERT INTO users(
        id,
        name,
        email,
        profile,
        hashed_password
    ) VALUES (
        :id,
        :name,
        :email,
        :profile,
        :hashed_password
    )
    """),new_users)

    database.execute(text("""
        INSERT INTO tweets(
            user_id,
            tweet
        )VALUES(
            2,
            "hello world"
        )
    """))

def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    
@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api 

def test_login(api):
    resp = api.post(
        '/login',
        data =json.dumps({'email':'hongse21@gmail.com','password':'test1234'}),
        content_type = 'application/json'
    )
    assert b"access_token" in resp.data

def test_unauthorizes(api):
    resp =api.post(
        '/tweet',
        data = json.dumps({'tweet':'hello world'}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401
    
    resp =api.post(
        '/unfollow',
        data =json.dumps({'unfollow':2}),
        content_type ='application/json'
    )
    assert resp.status_code == 401

def test_tweet(api):
    ## 테스트 사용자 생성 
    # new_user = {
    #     'email' : 'hongse21@gmail.com',
    #     'password' : 'test1234',
    #     'name'     : '홍성은',
    #     'profile'  : 'test_profile'
    # }
    # resp = api.post(
    #     '/sign-up',
    #     data = json.dumps(new_user),
    #     content_type = 'application/json'
    # )
    # assert resp.status_code ==200 

    ## getthe id of the new user 
    # resp_json = json.loads(resp.data)
    # new_user_id = resp_json['id']

    ## 로그인 
    resp = api.post(
        '/login',
        data = json.dumps({'email' :'hongse21@gmail.com',
                        'password':'test1234'}),
        content_type = 'application/json'
    )

    resp_json = json.loads(resp.data)
    access_token = resp_json['access_token']

    ## tweet
    resp =api.post(
        '/tweet',
        data = json.dumps({'tweet':'hello world!'}),
        content_type ='application/json',
        headers = {'Authorization': access_token}
    )
    assert resp.status_code == 200 
    
    ## tweet 확인 
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data)

    assert resp.status_code == 200 
    assert tweets == {
        'user_id' :1,
        'timeline' : [
            {
                'user_id' : 1,
                'tweet' : 'hello world!'
            }
        ]
    }

def test_follow(api):
    #log in 
    resp =api.post(
        '/login',
        data =json.dumps({'email':'hongse21@gmail.com', 'password': 'test1234'}),
        content_type = 'application/json'
    )
    resp_json = json.loads(resp.data)
    access_token =resp_json['access_token']
    
    # tweet이 비어 있는지 확인 
    resp =api.get(f'/timeline/1')
    tweets = json.loads(resp.data)
    
    assert resp.status_code ==200
    assert tweets =={
        'user_id' : 1 ,
        'timeline' : []
    }

    # follow id = 2 
    resp = api.post(
        '/follow',
        data = json.dumps({'id': 1, 'follow_user_id':2}),
        content_type = 'application/json',
        headers = {'Authorization': access_token}
    )
    assert resp.status_code == 200

    # tweet 리턴 여부 확인 
    resp = api.get(f'/timeline/1')
    tweets =json.loads(resp.data)

    assert resp.status_code ==200
    assert tweets == {
        'user_id' : 1,
        'timeline' : [
            {
                'user_id':2, 
                'tweet':'hello world'
            }
        ]
    }

def test_unfollow(api):
    resp = api.post(
        '/login',
        data = json.dumps({'email':'hongse21@gmail.com', 'password':'test1234'}),
        content_type = 'application/json'
    )
    resp_json = json.loads(resp.data)
    access_token = resp_json['access_token']

    # follow id 확인 
    resp = api.post(
        '/follow',
        data = json.dumps({'id': 1, 'follow_user_id':2}),
        content_type = 'application/json',
        headers = {'Authorization': access_token}
    )
    assert resp.status_code == 200

    # tweet 리턴 여부 확인 

    resp = api.get(f'/timeline/1')
    tweets =json.loads(resp.data)

    assert tweets =={
        'user_id' :1,
        'timeline' :[
            {
                'user_id' : 2,
                'tweet' :'hello world'
            }
        ]
    }

    # unfollow 확인 

    resp =api.post(
        '/unfollow',
        data = json.dumps({'id':1, 'unfollow':2}),
        content_type = 'application/json',
        headers = {'Authorization':access_token}
    )
    assert resp.status_code == 200

    # tweet 리턴 여부 확인 
    resp = api.get(f'/timeline/1')
    tweets =json.loads(resp.data)

    assert resp.status_code == 200
    assert tweets =={
        'user_id' :1,
        'timeline' :[]
    }