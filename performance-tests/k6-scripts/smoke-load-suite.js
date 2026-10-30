// smoke-load-suite.js - Lightweight CI Smoke Performance Suite for Tastio
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '10s',
  thresholds: {
    'http_req_duration': ['p(95)<450'],
    'http_req_failed': ['rate<0.02']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  const params = {
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    timeout: '5s'
  };

  // 1. Health check
  const healthRes = http.get(`${BASE_URL}/api/health`, params);
  check(healthRes, { 'health status is 200': (r) => r.status === 200 });

  // 2. Catalog check
  const catRes = http.get(`${BASE_URL}/api/recipes?page=1&limit=10`, params);
  check(catRes, { 'catalog status is 200': (r) => r.status === 200 });

  // 3. Search check
  const filterPayload = JSON.stringify({ search: 'biryani', cuisine: 'Indian' });
  const searchRes = http.post(`${BASE_URL}/api/recipes/filter`, filterPayload, params);
  check(searchRes, { 'search status is 200': (r) => r.status === 200 });

  // 4. Recommendation check
  const recPayload = JSON.stringify({ recipe_id: 1, user_id: 1, count: 3 });
  const recRes = http.post(`${BASE_URL}/api/recommend`, recPayload, params);
  check(recRes, { 'recommend status is 200': (r) => r.status === 200 });

  sleep(0.5);
}

export function handleSummary(data) {
  const summaryPath = __ENV.K6_SUMMARY_PATH || './reports/k6-summary.json';
  return {
    [summaryPath]: JSON.stringify(data, null, 2)
  };
}

