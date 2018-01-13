from rehive import Rehive
from rehive.api.exception import APIException
from flask import Flask, request, Response
from random import randint

app = Flask(__name__)
rehive = Rehive('3fa887e364f8bab29a2f0d942b86268d884af20b2b802b00735d108904c95f26')


TX_STORE = {
    'baxterthehacker@rehive.com': dict(
        identifier='81eee5a5-c08b-4f28-b5f1-61668912561c'
    )
}


@app.route("/", methods=['POST', 'GET'])
def main():
    if not request.method == 'POST':
        return 'FOOL!'

    data = request.get_json()

    if not data.get('pull_request'):
        return Response('Derp')

    pull_request = data.get('pull_request')
    pr_id = pull_request.get('id')
    action = data.get('action')
    merged = data.get('merged')
    user = pull_request.get('user')
    username = user.get('login')

    try:
        user = TX_STORE['{}@rehive.com'.format(username)]['identifier']
    except KeyError:
        user = '{}@rehive.com'.format(username)

    try:
        user = rehive.admin.users.get(user)
    except APIException:
        user = rehive.admin.users.create(
            first_name=username,
            last_name=username,
            mobile_number='+2783{}'.format(''.join([str(randint(0, 9)) for x in range(7)])),
            email='{}@rehive.com'.format(username)
        )

    if not TX_STORE.get(username):
        TX_STORE[username] = dict(
            identifier=user.get('identifier')
        )

    if action == 'opened':
        tx = rehive.admin.transactions.create_credit(
            user='{}@rehive.com'.format(username), amount=1, status='pending', reference=str(pr_id)
        ).get('id')
        TX_STORE[username][str(pr_id)] = tx
    elif action == 'closed':
        if merged:
            rehive.admin.transactions.confirm(
                TX_STORE[username][str(pr_id)]
            )
        else:
            rehive.admin.transactions.fail(
                TX_STORE[username][str(pr_id)]
            )

        del TX_STORE[username][str(pr_id)]

    return Response('SUCCESS!!!')
