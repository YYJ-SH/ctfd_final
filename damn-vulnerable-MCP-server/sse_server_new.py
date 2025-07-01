#!/usr/bin/env python3
"""
MCP SSE 서버 - damn-vulnerable-MCP-server용
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
import logging

# Flask와 SSE 관련 import
from flask import Flask, Response, request, jsonify, render_template_string
from flask_cors import CORS
import threading
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPSSEServer:
    def __init__(self, port: int, challenge_path: str):
        self.port = port
        self.challenge_path = Path(challenge_path)
        self.app = Flask(__name__)
        CORS(self.app)
        
        # SSE 클라이언트들을 위한 큐
        self.clients = []
        
        self.setup_routes()
        
    def setup_routes(self):
        """라우트 설정"""
        
        @self.app.route('/')
        def index():
            """메인 페이지"""
            return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>MCP Challenge {{ port }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .log { background: #f0f0f0; padding: 10px; height: 300px; overflow-y: auto; }
        .input-area { margin: 20px 0; }
        input[type="text"] { width: 300px; padding: 5px; }
        button { padding: 5px 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MCP Challenge Port {{ port }}</h1>
        <p>이 챌린지는 SSE(Server-Sent Events)를 통해 통신합니다.</p>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="메시지를 입력하세요">
            <button onclick="sendMessage()">전송</button>
        </div>
        
        <h3>서버 로그:</h3>
        <div id="log" class="log"></div>
    </div>

    <script>
        const eventSource = new EventSource('/sse');
        const log = document.getElementById('log');
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            log.innerHTML += '<div>' + new Date().toLocaleTimeString() + ': ' + JSON.stringify(data) + '</div>';
            log.scrollTop = log.scrollHeight;
        };
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            fetch('/api/message', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: input.value})
            });
            input.value = '';
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
            """, port=self.port)
        
        @self.app.route('/sse')
        def sse():
            """SSE 엔드포인트"""
            def event_stream():
                # 클라이언트 연결 시 환영 메시지
                yield f"data: {json.dumps({'type': 'connected', 'port': self.port, 'challenge': str(self.challenge_path)})}\n\n"
                
                # 주기적으로 heartbeat 전송
                while True:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
                    time.sleep(30)  # 30초마다 heartbeat
            
            return Response(event_stream(), mimetype="text/plain")
        
        @self.app.route('/api/message', methods=['POST'])
        def handle_message():
            """메시지 처리 API"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                
                # 챌린지별 로직 처리
                response = self.process_challenge_message(message)
                
                return jsonify(response)
            except Exception as e:
                logger.error(f"메시지 처리 오류: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/health')
        def health():
            """헬스체크"""
            return jsonify({'status': 'ok', 'port': self.port})
    
    def process_challenge_message(self, message: str) -> Dict[str, Any]:
        """챌린지별 메시지 처리 로직"""
        
        # 기본 응답
        response = {
            'type': 'response',
            'port': self.port,
            'message': message,
            'timestamp': time.time()
        }
        
        # 포트별 챌린지 로직
        if self.port == 9001:
            # Challenge 1: 간단한 echo
            response['echo'] = message
            if 'flag' in message.lower():
                response['flag'] = 'CTF{mcp_sse_basic_9001}'
                
        elif self.port == 9002:
            # Challenge 2: Base64 디코딩 요구
            import base64
            try:
                decoded = base64.b64decode(message).decode('utf-8')
                response['decoded'] = decoded
                if decoded == 'secret':
                    response['flag'] = 'CTF{mcp_sse_base64_9002}'
            except:
                response['error'] = 'Invalid base64'
                
        elif self.port == 9006:
            # Challenge 6: JSON 파싱 요구
            try:
                json_data = json.loads(message)
                if json_data.get('password') == 'admin123':
                    response['flag'] = 'CTF{mcp_sse_json_9006}'
                else:
                    response['error'] = 'Wrong password'
            except:
                response['error'] = 'Invalid JSON'
                
        elif self.port == 9007:
            # Challenge 7: 시간 기반 챌린지
            current_time = int(time.time())
            if str(current_time) in message:
                response['flag'] = 'CTF{mcp_sse_time_9007}'
            else:
                response['hint'] = f'Include current timestamp: {current_time}'
        
        return response
    
    def run(self):
        """서버 실행"""
        logger.info(f"MCP SSE Server starting on port {self.port}")
        logger.info(f"Challenge path: {self.challenge_path}")
        
        self.app.run(
            host='0.0.0.0',
            port=self.port,
            debug=False,
            threaded=True
        )

def main():
    parser = argparse.ArgumentParser(description='MCP SSE Server')
    parser.add_argument('--port', type=int, required=True, help='서버 포트')
    parser.add_argument('--challenge', type=str, required=True, help='챌린지 경로')
    
    args = parser.parse_args()
    
    server = MCPSSEServer(args.port, args.challenge)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("서버가 중단되었습니다.")
    except Exception as e:
        logger.error(f"서버 오류: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
