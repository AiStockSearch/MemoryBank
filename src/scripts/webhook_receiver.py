from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print('Получено событие:', data)
    # Здесь можно добавить интеграцию с CI/CD, Slack и т.д.
    return '', 204

if __name__ == '__main__':
    app.run(port=9000) 