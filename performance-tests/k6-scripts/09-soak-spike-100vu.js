import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5s', target: 20 },
    { duration: '5s', target: 100 }, // Spike to 100 VUs
    { duration: '15s', target: 100 },
    { duration: '5s', target: 0 }
  ],
  thresholds: {
    'http_req_duration': ['p(95)<550'],
    'http_req_failed': ['rate<0.02']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  // PERF-281 - PERF-300: High concurrency mixed soak
  const res = http.get(`${BASE_URL}/api/health`);
  check(res, { 'health ok': (r) => r.status === 200 });

  const catRes = http.get(`${BASE_URL}/api/recipes?page=1&limit=20`);
  check(catRes, { 'catalog ok': (r) => r.status === 200 });

  sleep(0.1);
}
