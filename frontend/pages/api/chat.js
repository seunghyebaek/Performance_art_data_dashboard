// pages/api/chat.js
'use client';
import { useRef, useState } from 'react';

export default function ChatBox() {
  const chatboxRef = useRef(null);
  const [input, setInput] = useState('');

  const appendMessage = (sender, text) => {
    const message = document.createElement('div');
    message.style.marginBottom = '0.5rem';
    message.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatboxRef.current.appendChild(message);
    chatboxRef.current.scrollTop = chatboxRef.current.scrollHeight;
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    appendMessage('🙋‍♀️ You', input);
    const message = input;
    setInput('');

    try {
      const res = await fetch('/api/clu/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: message }),
      });
      if (!res.ok) throw new Error('서버 응답 오류');
      const data = await res.json();

      const botReply = `🤖 ${data.response}`;
      appendMessage('🤖 Bot', botReply);
    } catch (err) {
      console.error(err);
      appendMessage('🤖 Bot', '⚠️ 오류가 발생했습니다.');
    }
  };

  return (
    <div>
      <div
        ref={chatboxRef}
        style={{ maxHeight: '300px', overflowY: 'auto', marginBottom: '1rem' }}
      />
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>보내기</button>
    </div>
  );
}
