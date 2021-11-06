from flask import Flask, request,jsonify

app = Flask(__name__)
app.users = {}
app.id_count = 1 

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