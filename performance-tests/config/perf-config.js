// perf-config.js - Enterprise Configuration for Tastio Performance & Load Testing
const path = require('path');

const fs = require('fs');
const winBin = path.join(__dirname, '..', 'bin', 'k6.exe');
const defaultK6 = (process.platform === 'win32' && fs.existsSync(winBin)) ? winBin : 'k6';

module.exports = {
  baseUrl: process.env.TASTIO_PERF_URL || 'http://127.0.0.1:5000',
  paths: {
    k6Bin: process.env.K6_BIN || defaultK6,
    reportsDir: path.join(__dirname, '..', 'reports'),
    dataDir: path.join(__dirname, '..', 'data'),
    scriptsDir: path.join(__dirname, '..', 'k6-scripts'),
    excelReport: path.join(__dirname, '..', 'reports', 'perf-test-report.xlsx'),
    jsonMetrics: path.join(__dirname, '..', 'reports', 'k6-summary.json')
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],         // Error rate must be under 1%
    http_req_duration: ['p(95)<350', 'p(99)<700'], // 95% of requests under 350ms, 99% under 700ms
    http_reqs: ['rate>=100']                // Minimum throughput 100 RPS under 100 VUs
  },
  profiles: {
    baseline_1vu: {
      vus: 1,
      duration: '10s',
      name: '1 VU Baseline Calibration'
    },
    ramp_10vu: {
      vus: 10,
      duration: '15s',
      name: '10 VUs Warm-Up'
    },
    step_25vu: {
      vus: 25,
      duration: '20s',
      name: '25 VUs Step Load'
    },
    step_50vu: {
      vus: 50,
      duration: '30s',
      name: '50 VUs Moderate Load'
    },
    peak_100vu: {
      vus: 100,
      duration: '60s',
      name: '100 VUs 1-Minute Target Stress Test'
    }
  },
  apdex: {
    t: 100, // Satisfied threshold: <= 100ms
    f: 400  // Tolerated threshold: <= 400ms
  }
};

