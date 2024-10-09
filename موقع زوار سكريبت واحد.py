from flask import Flask, render_template_string, request, jsonify
import requests
import threading

app = Flask(__name__)

FREE_FIRE_API_KEY = 'infoplayertrial_61029305'
FREE_FIRE_API_URL = 'https://drxzsecurityapi.info/api/player/info/{region}/{uid}?key={api_key}'

# تعريف كلمة السر
USERNAME = 'admin'  # يمكنك تغيير اسم المستخدم
PASSWORD = 'password123'  # تغيير كلمة السر هنا

cookies = {
    '_ga': 'GA1.1.2123120599.1674510784',
    '_fbp': 'fb.1.1674510785537.363500115',
    '_ga_7JZFJ14B0B': 'GS1.1.1674510784.1.1.1674510789.0.0.0',
    'source': 'mb',
    'region': 'MA',
    'language': 'ar',
    'datadome': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
    'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',
}

headers = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://shop2game.com',
    'Referer': 'https://shop2game.com/app/100067/idlogin',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
    'accept': 'application/json',
    'content-type': 'application/json',
}

def get_player_info(player_id):
    json_data = {
        'app_id': 100067,
        'login_id': f'{player_id}',
        'app_server_id': 0,
    }

    res = requests.post('https://shop2game.com/api/auth/player_id_login', cookies=cookies, headers=headers, json=json_data)

    if res.status_code == 200:
        response = res.json()
        name = response.get('nickname', 'Unknown')
        region = response.get('region', 'Unknown')
        return {'name': name, 'region': region}
    else:
        return {'error': f"فشل في جلب المعلومات. كود الحالة: {res.status_code}"}

def fetch_player_info(region, uid):
    url = FREE_FIRE_API_URL.format(region=region, uid=uid, api_key=FREE_FIRE_API_KEY)
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def send_request(region, uid, successful_results, failed_results, count, lock):
    result = fetch_player_info(region, uid)
    with lock:
        if result:
            successful_results.append(count)
        else:
            failed_results.append(count)

def send_multiple_requests(region, uid, view_count, progress_callback):
    threads = []
    successful_results = []
    failed_results = []
    lock = threading.Lock()

    for count in range(1, view_count + 1):
        thread = threading.Thread(target=send_request, args=(region, uid, successful_results, failed_results, count, lock))
        threads.append(thread)
        thread.start()
        progress_callback(count, view_count)

    for thread in threads:
        thread.join()

    return successful_results, failed_results

@app.route('/')
def home():
    return render_template_string(html_content)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username == USERNAME and password == PASSWORD:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'})

@app.route('/send', methods=['POST'])
def send():
    player_id = request.form['player_id']
    view_count = int(request.form['view_count'])
    
    if view_count > 20:  # تعديل الحد الأقصى ليكون 20 زيارة فقط
        return jsonify({'error': 'الحد الأقصى لعدد الزيارات هو 20. يرجى كتابة عدد أقل.'})
    
    player_info = get_player_info(player_id)

    if 'error' in player_info:
        return jsonify({'error': player_info['error']})
    
    region = player_info['region'].lower()
    uid = player_id

    successful_results, failed_results = [], []
    
    def progress_callback(count, total):
        percentage = (count / total) * 100
        print(f"تم إرسال زيارة رقم {count} من {total} ({percentage:.2f}%)")

    successful_results, failed_results = send_multiple_requests(region, uid, view_count, progress_callback)

    total_success = len(successful_results)
    total_failed = len(failed_results)
    final_message = f"🌟 تحية طيبة! تم إرسال جميع الزيارات: {view_count} زيارة إلى اللاعب {player_info['name']}."

    return jsonify({
        'player_name': player_info['name'],
        'total_success': total_success,
        'total_failed': total_failed,
        'final_message': final_message
    })

html_content = '''
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Fire visits website</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body {
            background-color: #2d2d2d;
            color: #ffffff;
            font-family: 'Tahoma', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            min-height: 100vh;
            text-align: center;
        }

        h1 {
            color: #007bff; /* تغيير اللون إلى الأزرق */
            font-size: 2rem;
            margin-bottom: 20px;
        }

        form {
            background-color: #3e3e3e;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
            max-width: 300px;
            width: 100%;
            margin-bottom: 20px;
        }

        input[type="text"], input[type="number"], input[type="password"] {
            width: 90%;
            padding: 8px;
            margin: 10px 0;
            border: none;
            border-radius: 5px;
            background-color: #ffffff;
            color: #333;
            font-size: 0.9rem;
        }

        button {
            background-color: #007bff; /* تغيير اللون إلى الأزرق */
            color: #ffffff; /* لون النص */
            padding: 8px;
            border: none;
            border-radius: 5px;
            font-size: 0.9rem;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #0056b3; /* تغيير اللون الأزرق عند التحويم */
        }

        #results {
            font-size: 1rem;
            margin-top: 20px;
            display: none;
        }

        .progress-bar {
            background-color: #444;
            border-radius: 5px;
            margin: 20px 0;
            width: 90%;
            height: 20px;
        }

        .progress {
            background-color: #007bff; /* تغيير لون شريط التقدم إلى الأزرق */
            height: 100%;
            border-radius: 5px;
            width: 0;
            transition: width 0.4s ease;
        }

        footer {
            margin-top: 30px;
            font-size: 1rem;
            color: #007bff; /* لون أزرق للحقوق */
        }

        .white-text-box {
            color: #ffffff;
            font-size: 1rem;
            margin-bottom: 20px;
        }

        .result-text {
            font-size: 1rem;
            margin-bottom: 10px;
        }

        .blue-text {
            color: #007bff;
        }
    </style>
</head>
<body>
    <h1>Free Fire visits website</h1>

    <form id="loginForm">
        <label for="username">Host :</label>
        <input type="text" id="username" name="username" required>
        <label for="password">Port :</label>
        <input type="password" id="password" name="password" required>
        <button type="submit">تسجيل الدخول</button>
    </form>

    <form id="playerForm" style="display: none;">
        <label for="player_id">أدخل معرف اللاعب :</label>
        <input type="text" id="player_id" name="player_id" required>
        <label for="view_count">عدد الزيارات :</label>
        <input type="number" id="view_count" name="view_count" min="1" max="20" required>
        <button type="submit">إرسال</button>
    </form>

    <div class="progress-bar" style="display: none;">
        <div class="progress"></div>
    </div>

    <div id="results"></div>

    <footer>
        <p>&copy; Developer : rbgx_moxado</p>
    </footer>

    <script>
        $('#loginForm').on('submit', function(e) {
            e.preventDefault();
            const username = $('#username').val();
            const password = $('#password').val();

            $.post('/login', { username: username, password: password }, function(data) {
                if (data.success) {
                    $('#loginForm').hide();
                    $('#playerForm').show();
                } else {
                    alert(data.error);
                }
            });
        });

        $('#playerForm').on('submit', function(e) {
            e.preventDefault();
            const playerId = $('#player_id').val();
            const viewCount = $('#view_count').val();
            $('#results').hide();
            $('.progress-bar').show();

            let progress = 0;

            $.post('/send', { player_id: playerId, view_count: viewCount }, function(data) {
                let resultsHtml = `<div class="white-text-box">${data.player_name} : تم إرسال الزيارات إلى اللاعب  </div>`;
                resultsHtml += `<p class="result-text">${data.total_success} : عدد الزيارات الناجحة </p>`;
                
                resultsHtml += `<p class="result-text">👾   اذهب وتفقد حسابك اذا وصلك الزوار </p>`;

                $('#results').html(resultsHtml).show();
                $('.progress-bar').hide();
            });

            const interval = setInterval(function() {
                progress++;
                if (progress <= viewCount) {
                    const percentage = (progress / viewCount) * 100;
                    $('.progress').css('width', percentage + '%');
                } else {
                    clearInterval(interval);
                }
            }, 1000); // تحديث كل ثانية
        });
    </script>
</body>
</html>

'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
