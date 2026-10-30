import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 25,
  duration: '15s',
  thresholds: {
    'http_req_duration': ['p(95)<150'],
    'http_req_failed': ['rate<0.01']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  // PERF-001 - PERF-006: Health checks
  const healthRes = http.get(`${BASE_URL}/api/health`);
  check(healthRes, { 'health ok': (r) => r.status === 200 });

  // PERF-007 - PERF-015: Catalog pages & limits
  const p1Res = http.get(`${BASE_URL}/api/recipes?page=1&limit=20`);
  check(p1Res, { 'page 1 ok': (r) => r.status === 200 });

  const p5Res = http.get(`${BASE_URL}/api/recipes?page=5&limit=20`);
  check(p5Res, { 'page 5 ok': (r) => r.status === 200 });

  // PERF-019 - PERF-022: Recipe ID lookups
  const rId = Math.floor(Math.random() * 230) + 1;
  const singleRes = http.get(`${BASE_URL}/api/recipes/${rId}`);
  check(singleRes, { 'single recipe ok': (r) => r.status === 200 });

  sleep(0.1);
}
