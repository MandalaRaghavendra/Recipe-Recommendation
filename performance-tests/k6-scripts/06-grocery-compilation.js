import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '15s',
  thresholds: {
    'http_req_duration': ['p(95)<250'],
    'http_req_failed': ['rate<0.02']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  const headers = { 'Content-Type': 'application/json' };

  // PERF-186 - PERF-220: Grocery checklist retrieval & custom item addition
  const listRes = http.get(`${BASE_URL}/api/grocery-list?user_id=1`);
  check(listRes, { 'grocery list ok': (r) => r.status === 200 });

  const itemPayload = JSON.stringify({
    item_name: 'Greek Yogurt 500g',
    category: 'Dairy',
    user_id: 1
  });
  http.post(`${BASE_URL}/api/grocery-list/item`, itemPayload, { headers });

  sleep(0.1);
}
