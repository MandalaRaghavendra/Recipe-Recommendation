import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 25,
  duration: '15s',
  thresholds: {
    'http_req_duration': ['p(95)<450'],
    'http_req_failed': ['rate<0.02']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  const headers = { 'Content-Type': 'application/json' };

  // PERF-221 - PERF-255: Coach context & interactive chat
  http.get(`${BASE_URL}/api/coach/context?user_id=1`);

  const chatPayload = JSON.stringify({
    message: 'What are low glycemic breakfast options for energy?',
    user_id: 1
  });
  const res = http.post(`${BASE_URL}/api/coach/chat`, chatPayload, { headers });
  check(res, { 'coach chat ok': (r) => r.status === 200 });

  sleep(0.1);
}
