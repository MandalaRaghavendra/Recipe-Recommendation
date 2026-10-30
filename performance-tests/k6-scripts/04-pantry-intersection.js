import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '15s',
  thresholds: {
    'http_req_duration': ['p(95)<300'],
    'http_req_failed': ['rate<0.02']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  const headers = { 'Content-Type': 'application/json' };

  // PERF-111 - PERF-145: What can I cook pantry matching
  const pantryPayload = JSON.stringify({
    ingredients: ['chicken', 'rice', 'onion', 'garlic', 'tomato'],
    max_missing: 2,
    sort_by: 'match_percentage'
  });
  const res = http.post(`${BASE_URL}/api/pantry-match`, pantryPayload, { headers });
  check(res, { 'pantry match ok': (r) => r.status === 200 });

  sleep(0.1);
}
