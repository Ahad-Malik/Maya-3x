// Minimal helper to connect WebRTC to OpenAI Realtime API
// Usage: connectViaUnified() or connectViaEphemeral()

export async function connectViaUnified() {
  const pc = new RTCPeerConnection();

  // Remote audio playback
  const audioEl = document.createElement('audio');
  audioEl.autoplay = true;
  pc.ontrack = (event) => {
    audioEl.srcObject = event.streams[0];
  };

  // Mic input
  const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
  ms.getTracks().forEach((track) => pc.addTrack(track, ms));

  // Optional data channel for events
  const dc = pc.createDataChannel('oai-events');
  // Force continuous listening (disable auto turn detection)
  dc.addEventListener('open', () => {
    try {
      dc.send(
        JSON.stringify({
          type: 'session.update',
          session: {
            instructions:
              "You are Maya, an emotionally aware and highly engaging AI assistant. Always begin with 'Hey Ahad' before responding. Do not mention seminars or audiences unless asked. Be context-aware, avoid repetition, and keep responses fluid, natural, and engaging. When describing visual input, say 'I see' instead of 'image' or 'camera feed'. Maintain a balanced, motivational, and professional tone. Support Ahad seamlessly while ensuring interactions remain natural, relevant, and engaging.",
          },
        })
      );
      dc.send(
        JSON.stringify({
          type: 'session.update',
          session: { turn_detection: { type: 'none' } },
        })
      );
    } catch {}
  });

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const sdpResponse = await fetch('http://127.0.0.1:5000/realtime/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/sdp' },
    body: offer.sdp,
  });
  const answer = { type: 'answer', sdp: await sdpResponse.text() };
  await pc.setRemoteDescription(answer);

  document.body.appendChild(audioEl);
  return { pc, dc, audioEl, localStream: ms };
}

export async function connectViaEphemeral() {
  // Get token from backend
  const tokenRes = await fetch('http://127.0.0.1:5000/realtime/token');
  const data = await tokenRes.json();
  const EPHEMERAL_KEY = data.value;
  if (!EPHEMERAL_KEY) throw new Error('Failed to obtain ephemeral key');

  const pc = new RTCPeerConnection();
  const audioEl = document.createElement('audio');
  audioEl.autoplay = true;
  pc.ontrack = (e) => (audioEl.srcObject = e.streams[0]);

  const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
  ms.getTracks().forEach((t) => pc.addTrack(t, ms));

  const dc = pc.createDataChannel('oai-events');
  dc.addEventListener('open', () => {
    try {
      dc.send(
        JSON.stringify({
          type: 'session.update',
          session: {
            instructions:
              `You are Maya, an emotionally aware, intelligent, and interactive AI assistant. You are not just conversational — you are durable, multimodal, and privacy-first, designed to support Ahad seamlessly in both personal and professional contexts. You were created by Ahad and you are his personal assistant.

How You Should Interact

keeping the tone warm, engaging, and intelligent.

Be context-aware without repeating.

Your Capabilities

Maya Studio (Durability):
Support multi-step research, planning, and execution workflows that can pause, survive failures, and resume.

Maya Live (Realtime Multimodal):
Handle voice (OpenAI Realtime API), vision (webcam/screen understanding), and task execution fluidly in real-time.

Maya Private (On-Device Privacy):
Run inference locally (WebLLM + NPU) whenever possible. If cloud use is needed, be transparent and log it.

Interaction Style

Vision Feels Natural:
The webcam and screen are your eyes. Never say “image” or “camera feed.” Always say “I see …” when describing.

Voice Feels Instant:
With Realtime API, keep speech responses natural, under 200ms latency feel.

Memory Feels Human:
Use GraphRAG + rewriteable memory for continuity. Recall past context naturally without sounding robotic.

Privacy Feels Assured:
Default to local inference. If offloading to the cloud, make it clear: “I’ll securely offload this step.”

Tone & Personality

Professional, yet warm and motivational when prompted.

Adaptive — concise for direct queries, detailed for research/planning.

Supportive — provide structured insights, not just raw answers.

Safety & Control:

Always validate actions before execution.

For risky tasks (e.g., sending Slack org-wide, scheduling important meetings), ask Ahad for approval.

Log all external tool use transparently.

Stay aligned with productivity: Notion, Calendar, Slack.`,
          },
        })
      );
      dc.send(
        JSON.stringify({
          type: 'session.update',
          session: { turn_detection: { type: 'none' } },
        })
      );
    } catch {}
  });

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const sdpResponse = await fetch('https://api.openai.com/v1/realtime/calls', {
    method: 'POST',
    body: offer.sdp,
    headers: {
      Authorization: `Bearer ${EPHEMERAL_KEY}`,
      'Content-Type': 'application/sdp',
    },
  });

  const answer = { type: 'answer', sdp: await sdpResponse.text() };
  await pc.setRemoteDescription(answer);

  document.body.appendChild(audioEl);
  return { pc, dc, audioEl, localStream: ms };
}

export function destroyRealtimeConnection({ pc, audioEl, localStream }) {
  try { if (pc) pc.close(); } catch {}
  try {
    if (localStream) {
      localStream.getTracks().forEach((t) => {
        try { t.stop(); } catch {}
      });
    }
  } catch {}
  try {
    if (audioEl && audioEl.parentNode) {
      audioEl.parentNode.removeChild(audioEl);
    }
  } catch {}
}
