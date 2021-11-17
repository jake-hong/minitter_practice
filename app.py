from flask import Flask, request,jsonify
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
from model import get_user, insert_user, insert_tweet, insert_follow, insert_unfollow, get_timeline

#  Default JSON encoder 는 set을 JSON으로 변환할 수 없음. 
# 커스텀 인코더를 작성하여 set을 list로 변환하고, jSON으로 변환 가능하게 해준다. 
class CustomJSONEncoder(JSONEncoder):
    def default(self, object) :
        if isinstance(object,set):
            return list(object)

        return JSONEncoder.default(self,object)

def create_app(test_config = None):
    app = Flask(__name__)
    
    app.json_encoder =CustomJSONEncoder
    
    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    
    database = create_engine(app.config['DB_URL'], encoding='utf-8',max_overflow = 0)
    app.database = database
    
    # 로그인
    @app.route('/sign_up', methods = ['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = insert_user(new_user)
        new_user = get_user(new_user_id)

        return jsonify(new_user)

    # 300자 글 올리기
    @app.route('/tweet', methods = ['POST'])
    def tweet():
        user_tweet = request.json
        tweet = user_tweet['tweet']

        # if user_id not in app.users:
        #     return '사용자가 존재하지 않습니다', 400

        if len(tweet) > 300:
            return '300자가 초과됐습니다',400

        insert_tweet(user_tweet)

        return '트윗이 작성되었습니다',200

    @app.route('/follow', methods = ['POST'])
    def follow():
        payload = request.json
        insert_follow(payload)

        return '',200 

    @app.route('/unfollow',methods = ['POST'])
    def unfollow():
        payload = request.json
        insert_unfollow(payload)

        return '',200 

    @app.route('/timeline/<int:user_id>',methods=['GET'])
    def timeline(user_id):
        return jsonify({
            'user_id' : user_id,
            'timeline': get_timeline(user_id)
        })
    
    return app 

