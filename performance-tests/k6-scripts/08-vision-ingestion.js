import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 20,
  duration: '15s',
  thresholds: {
    'http_req_duration': ['p(95)<500'],
    'http_req_failed': ['rate<0.02']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  // PERF-256 - PERF-280: Vision engine status & sample recognition
  const statusRes = http.get(`${BASE_URL}/api/vision/status`);
  check(statusRes, { 'vision status ok': (r) => r.status === 200 });

  sleep(0.2);
}
