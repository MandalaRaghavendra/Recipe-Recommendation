import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '15s',
  thresholds: {
    'http_req_duration': ['p(95)<350'],
    'http_req_failed': ['rate<0.02']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  const headers = { 'Content-Type': 'application/json' };

  // PERF-071 - PERF-110: Cosine similarity vector search
  const recommendPayload = JSON.stringify({
    recipe_id: Math.floor(Math.random() * 200) + 1,
    target_calories: 550,
    user_id: 1,
    count: 5
  });
  const res = http.post(`${BASE_URL}/api/recommend`, recommendPayload, { headers });
  check(res, { 'recommendation ok': (r) => r.status === 200 });

  sleep(0.1);
}
