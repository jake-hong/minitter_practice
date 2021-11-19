import config
import pytest
import json 
# import bcrypt

from app import create_app 
from sqlalchemy import create_engine,text


datbase = create_engine(config.test_config['DB_URL'], encoding='utf-8',max_overflow=0)


@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api 

def test_tweet(api):
    ## 테스트 사용자 생성 
    new_user = {
        'email' : 'hongse24@gmail.com',
        'password' : 'test1234',
        'name'     : '홍성은',
        'profile'  : 'test_profile'
    }
    resp = api.post(
        '/sign-up',
        data = json.dumps(new_user),
        content_type = 'application/json'
    )
    assert resp.status_code ==200 

    ## getthe id of the new user 
    resp_json = json.loads(resp.data)
    new_user_id = resp_json['id']

    ## 로그인 
    resp = api.post(
        '/login',
        data = json.dumps({'email' :'hongse24@gmail.com',
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
    resp = api.get(f'/timeline/{new_user_id}')
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
