from rehive import Rehive
from flask import Flask, request


app = Flask(__name__)
rehive = Rehive('3fa887e364f8bab29a2f0d942b86268d884af20b2b802b00735d108904c95f26')


TX_STORE = dict()


@app.route("/")
def main():
    if not request.method == 'POST':
        return 'FOOL!'

    pull_request = request.args.get('pull_request').get('id')
    action = request.args.get('action')
    merged = request.args.get('merged')
    username = request.args.get('user').get('login')

    user = rehive.admin.user.get('{}@rehive.com'.format(username))

    if user.status_code == 404:
        user = rehive.admin.user.create(
            email='{}@rehive.com'.format(username)
        )

    if not TX_STORE.get(username):
        TX_STORE[username] = dict()

    if action == 'opened':
        tx = rehive.admin.transactions.create_credit(
            user=user, amount=1, status='pending', reference=pull_request
        ).get('id')
        TX_STORE[username][pull_request] = tx
    elif action == 'closed':
        if merged:
            rehive.admin.transactions.confirm(
                TX_STORE[username][pull_request]
            )
        else:
            rehive.admin.transactions.fail(
                TX_STORE[username][pull_request]
            )

        del TX_STORE[username][pull_request]
