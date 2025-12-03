from flask import Flask, jsonify, request
from flask_cors import CORS
import akinator
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Store game sessions in memory
sessions = {}

# HTML template as string
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Akinator - The Mind Reader Game">
    <title>Akinator - Mind Reader Game</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .logo {
            font-size: 50px;
            margin-bottom: 15px;
        }
        h1 {
            color: #667eea;
            font-size: 28px;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #888;
            font-size: 14px;
        }
        .game-section {
            display: none;
        }
        .game-section.active {
            display: block;
            animation: fadeIn 0.3s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .start-description {
            color: #666;
            font-size: 16px;
            line-height: 1.8;
            margin: 20px 0 30px;
        }
        .question {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            font-size: 20px;
            font-weight: 500;
            text-align: center;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s ease;
        }
        .question-counter {
            background: #f0f0f0;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 12px;
            color: #666;
            margin-bottom: 20px;
            text-align: center;
        }
        .buttons-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 15px;
        }
        .btn {
            padding: 15px 20px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
        }
        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .btn-yes { background: #4CAF50; color: white; grid-column: 1; }
        .btn-no { background: #f44336; color: white; grid-column: 2; }
        .btn-idk { background: #ff9800; color: white; grid-column: 1; }
        .btn-probably { background: #2196F3; color: white; grid-column: 2; }
        .btn-probably-not { background: #9C27B0; color: white; grid-column: 1 / -1; }
        .btn-back { background: #e0e0e0; color: #333; width: 100%; }
        .btn-start, .btn-play-again {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 100%;
            font-size: 16px;
            padding: 18px;
            margin-top: 20px;
        }
        .result-image {
            width: 150px;
            height: 150px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 60px;
        }
        .result-name {
            font-size: 28px;
            color: #333;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .result-message {
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: none;
            border-left: 4px solid #c62828;
        }
        .error-message.show {
            display: block;
        }
        @media (max-width: 600px) {
            .container { padding: 25px; }
            h1 { font-size: 24px; }
            .buttons-group { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="game-section active" id="startSection">
            <div class="header">
                <div class="logo">🧠</div>
                <h1>Akinator</h1>
                <p class="subtitle">The Mind Reader Game</p>
            </div>
            <div class="start-section">
                <p class="start-description">
                    Think of a character or person and I'll try to guess who you're thinking of!
                </p>
                <button class="btn btn-start" onclick="startGame()">🎮 Start Game</button>
            </div>
        </div>

        <div class="game-section" id="gameSection">
            <div class="error-message" id="errorMessage"></div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="question-counter">
                Question <span id="questionNum">1</span>
            </div>
            <div class="question" id="questionText">Loading...</div>
            <div class="buttons-group">
                <button class="btn btn-yes" onclick="answer('yes')" id="btnYes">👍 Yes</button>
                <button class="btn btn-no" onclick="answer('no')" id="btnNo">👎 No</button>
                <button class="btn btn-idk" onclick="answer('idk')" id="btnIdk">🤔 Don't Know</button>
                <button class="btn btn-probably" onclick="answer('probably')" id="btnProbably">✓ Probably</button>
                <button class="btn btn-probably-not" onclick="answer('probably_not')" id="btnProbablyNot">✗ Probably Not</button>
            </div>
            <button class="btn btn-back" onclick="goBack()" id="btnBack">← Go Back</button>
        </div>

        <div class="game-section" id="resultSection">
            <div class="result-section">
                <div class="result-image" id="resultImage">🎭</div>
                <div class="result-name" id="resultName">Character Name</div>
                <div class="result-message" id="resultMessage">Did I guess correctly?</div>
                <button class="btn btn-play-again" onclick="playAgain()">🔄 Play Again</button>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        let sessionId = null;
        let currentQuestionNumber = 0;

        async function startGame() {
            try {
                showError('');
                disableAnswerButtons(true);
                const response = await fetch(`${API_BASE}/api/start`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                const data = await response.json();
                if (data.success) {
                    sessionId = data.session_id;
                    currentQuestionNumber = data.question_number;
                    document.getElementById('questionText').textContent = data.question;
                    document.getElementById('questionNum').textContent = data.question_number;
                    updateProgressBar();
                    showSection('gameSection');
                    disableAnswerButtons(false);
                } else {
                    showError('Failed: ' + data.error);
                }
            } catch (error) {
                showError('Connection error: ' + error.message);
                console.error(error);
            }
        }

        async function answer(response) {
            try {
                showError('');
                disableAnswerButtons(true);
                const fetchResponse = await fetch(`${API_BASE}/api/answer`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, answer: response})
                });
                const data = await fetchResponse.json();
                if (data.success) {
                    if (data.finished) {
                        displayResult(data);
                    } else {
                        currentQuestionNumber = data.question_number;
                        document.getElementById('questionText').textContent = data.question;
                        document.getElementById('questionNum').textContent = data.question_number;
                        updateProgressBar();
                        disableAnswerButtons(false);
                    }
                } else {
                    showError('Error: ' + data.error);
                    disableAnswerButtons(false);
                }
            } catch (error) {
                showError('Error: ' + error.message);
                disableAnswerButtons(false);
            }
        }

        async function goBack() {
            try {
                showError('');
                disableAnswerButtons(true);
                const response = await fetch(`${API_BASE}/api/back`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId})
                });
                const data = await response.json();
                if (data.success) {
                    currentQuestionNumber = data.question_number;
                    document.getElementById('questionText').textContent = data.question;
                    document.getElementById('questionNum').textContent = data.question_number;
                    updateProgressBar();
                    disableAnswerButtons(false);
                } else {
                    showError('Error: ' + data.error);
                    disableAnswerButtons(false);
                }
            } catch (error) {
                showError('Error: ' + error.message);
                disableAnswerButtons(false);
            }
        }

        function displayResult(data) {
            document.getElementById('resultName').textContent = data.name;
            document.getElementById('resultMessage').innerHTML = `I think you are thinking of <strong>${data.name}</strong>! Am I right? 🎉`;
            const resultImageDiv = document.getElementById('resultImage');
            if (data.photo && data.photo.startsWith('http')) {
                resultImageDiv.innerHTML = `<img src="${data.photo}" alt="${data.name}" style="width:100%;height:100%;border-radius:15px;object-fit:cover;">`;
            } else {
                resultImageDiv.textContent = '🎭';
            }
            showSection('resultSection');
        }

        function playAgain() {
            startGame();
        }

        function showSection(sectionId) {
            document.querySelectorAll('.game-section').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
        }

        function updateProgressBar() {
            const progress = (currentQuestionNumber / 20) * 100;
            document.getElementById('progressFill').style.width = Math.min(progress, 100) + '%';
        }

        function disableAnswerButtons(disabled) {
            document.getElementById('btnYes').disabled = disabled;
            document.getElementById('btnNo').disabled = disabled;
            document.getElementById('btnIdk').disabled = disabled;
            document.getElementById('btnProbably').disabled = disabled;
            document.getElementById('btnProbablyNot').disabled = disabled;
            document.getElementById('btnBack').disabled = disabled;
        }

        function showError(message) {
            const errorEl = document.getElementById('errorMessage');
            if (message) {
                errorEl.textContent = message;
                errorEl.classList.add('show');
            } else {
                errorEl.classList.remove('show');
            }
        }
    </script>
</body>
</html>"""

# ============================================
# SERVE HTML
# ============================================

@app.route('/', methods=['GET'])
def serve_index():
    """Serve the main HTML file"""
    return HTML_TEMPLATE, 200, {'Content-Type': 'text/html'}


# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/start', methods=['POST', 'GET', 'OPTIONS'])
def start_game():
    """Start a new game session"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        aki = akinator.Akinator()
        aki.start_game()
        
        session_id = str(len(sessions) + 1)
        sessions[session_id] = {
            'aki': aki,
            'history': [],
            'question_count': 1
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'question': str(aki),
            'question_number': 1
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to start game: {str(e)}'
        }), 500


@app.route('/api/answer', methods=['POST', 'OPTIONS'])
def answer_question():
    """Submit an answer to the current question"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        session_id = data.get('session_id')
        answer = data.get('answer')
        
        if not session_id or session_id not in sessions:
            return jsonify({'success': False, 'error': 'Invalid session ID'}), 400
        
        if not answer:
            return jsonify({'success': False, 'error': 'No answer provided'}), 400
        
        answer_map = {
            'yes': 'yes',
            'no': 'no',
            'idk': 'idk',
            'probably': 'probably',
            'probably_not': 'probably not'
        }
        
        if answer not in answer_map:
            return jsonify({'success': False, 'error': 'Invalid answer'}), 400
        
        session_data = sessions[session_id]
        aki = session_data['aki']
        
        session_data['history'].append(answer)
        
        try:
            aki.answer(answer_map[answer])
        except akinator.InvalidChoiceError:
            return jsonify({'success': False, 'error': 'Invalid answer choice'}), 400
        
        if aki.finished:
            return jsonify({
                'success': True,
                'finished': True,
                'name': aki.name_proposition,
                'photo': aki.photo if hasattr(aki, 'photo') else None,
                'message': f'I think you are thinking of {aki.name_proposition}!'
            }), 200
        else:
            session_data['question_count'] += 1
            return jsonify({
                'success': True,
                'finished': False,
                'question': str(aki),
                'question_number': aki.step + 1
            }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500


@app.route('/api/back', methods=['POST', 'OPTIONS'])
def go_back():
    """Go back one question"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({'success': False, 'error': 'Invalid session ID'}), 400
        
        session_data = sessions[session_id]
        aki = session_data['aki']
        
        try:
            aki.back()
            if session_data['history']:
                session_data['history'].pop()
            session_data['question_count'] -= 1
            
        except akinator.CantGoBackAnyFurther:
            return jsonify({'success': False, 'error': 'Cannot go back any further'}), 400
        
        return jsonify({
            'success': True,
            'question': str(aki),
            'question_number': aki.step + 1
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)