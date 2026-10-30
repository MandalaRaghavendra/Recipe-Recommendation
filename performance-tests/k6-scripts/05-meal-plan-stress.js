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
  // PERF-146 - PERF-185: Current meal plan & slot alternative retrieval
  const currentRes = http.get(`${BASE_URL}/api/meal-plan/current?user_id=1`);
  check(currentRes, { 'current plan ok': (r) => r.status === 200 });

  const altRes = http.get(`${BASE_URL}/api/meal-plan/alternatives?meal_type=Lunch&diet=weight_loss&user_id=1`);
  check(altRes, { 'alternatives ok': (r) => r.status === 200 });

  sleep(0.1);
}
