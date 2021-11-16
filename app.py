from flask import Flask, request,jsonify
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text

def create_app(test_config = None):
    app = Flask(__name__)
    
    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    
    database = create_engine(app.config['db_url'], encoding='utf-8',max_overflow = 0)
    app.database = database
    
    return app 

#  Default JSON encoder 는 set을 JSON으로 변환할 수 없음. 
# 커스텀 인코더를 작성하여 set을 list로 변환하고, jSON으로 변환 가능하게 해준다. 
class CustomJSONEncoder(JSONEncoder):
    def default(self, object) :
        if isinstance(object,set):
            return list(object)
        return JSONEncoder.default(self,object)

app = Flask(__name__)
app.users = {}
app.id_count = 1
app.json_encoder =CustomJSONEncoder

# 로그인
@app.route('/sign_up', methods = ['POST'])
def sign_up():
    new_user = request.json
    new_user['id'] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count = app.id_count + 1

    return jsonify(new_user)

# 300자 글 올리기
app.tweets = []

@app.route('/tweet', methods = ['POST'])
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet = payload['tweet']

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400

    if len(tweet) > 300:
        return '300자가 초과했습니다',400

    user_id = int(payload['id'])
    app.tweets.append({
        'user_id' : user_id,
        'tweet' : tweet
    })
    return '트윗이 작성되었습니다',200

@app.route('/follow', methods = ['POST'])
def follow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['follow'])
    
    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다', 400
    
    user = app.users[user_id]
    user.setdefault('follow',set()).add(user_id_to_follow)

    return jsonify(user) 

@app.route('/unfollow',methods = ['POST'])
def unfollow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['unfollow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow',set()).discard(user_id_to_follow)

    return jsonify(user)

@app.route('/timeline/<int:user_id>',methods=['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return '사용자가 존재하지 않습니다',400
    
    follow_list = app.users[user_id].get('follow',set())
    follow_list.add(user_id)
    timeline =[tweet for tweet in app.tweets if tweet['user_id'] in follow_list]
    
    return jsonify({
        'user_id' : user_id,
        'timeline': timeline
    })