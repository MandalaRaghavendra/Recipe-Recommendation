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

  // PERF-031 - PERF-045: Multi-filter queries
  const filterPayload = JSON.stringify({
    cuisine: 'Indian',
    diet: 'Vegetarian',
    meal_type: 'Dinner',
    max_calories: 500
  });
  const filterRes = http.post(`${BASE_URL}/api/recipes/filter`, filterPayload, { headers });
  check(filterRes, { 'filter ok': (r) => r.status === 200 });

  // PERF-046 - PERF-055: User preferences & history
  const prefRes = http.get(`${BASE_URL}/api/user/preferences?user_id=1`);
  check(prefRes, { 'prefs ok': (r) => r.status === 200 });

  // PERF-056 - PERF-070: Recipe view counters & favorites
  const rId = Math.floor(Math.random() * 50) + 1;
  http.post(`${BASE_URL}/api/recipes/${rId}/view`, null, { headers });

  sleep(0.1);
}
