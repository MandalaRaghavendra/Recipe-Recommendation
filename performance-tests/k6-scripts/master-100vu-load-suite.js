// master-100vu-load-suite.js - Comprehensive 100 VU 1-Minute Multi-Endpoint Load Suite for Tastio
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// Custom Enterprise Metrics
const healthLatency = new Trend('tastio_health_latency_ms');
const catalogLatency = new Trend('tastio_catalog_latency_ms');
const searchLatency = new Trend('tastio_search_latency_ms');
const recommendLatency = new Trend('tastio_recommend_latency_ms');
const pantryLatency = new Trend('tastio_pantry_latency_ms');
const mealPlanLatency = new Trend('tastio_mealplan_latency_ms');
const groceryLatency = new Trend('tastio_grocery_latency_ms');
const coachLatency = new Trend('tastio_coach_latency_ms');
const visionLatency = new Trend('tastio_vision_latency_ms');

const errorRate = new Rate('tastio_error_rate');
const successfulRequests = new Counter('tastio_successful_reqs');
const failedRequests = new Counter('tastio_failed_reqs');

// Test Configuration: 100 VUs for 1 minute (60s)
export const options = {
  stages: [
    { duration: '10s', target: 50 },  // Ramp up to 50 VUs
    { duration: '10s', target: 100 }, // Ramp up to 100 VUs
    { duration: '35s', target: 100 }, // Maintain 100 VUs full peak load
    { duration: '5s', target: 0 }     // Graceful ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<450', 'p(99)<850'], // 95% requests < 450ms, 99% < 850ms
    'tastio_error_rate': ['rate<0.02'],              // Error rate under 2%
    'http_req_failed': ['rate<0.02'],
    'tastio_health_latency_ms': ['p(95)<50'],
    'tastio_catalog_latency_ms': ['p(95)<150'],
    'tastio_recommend_latency_ms': ['p(95)<300'],
    'tastio_mealplan_latency_ms': ['p(95)<350']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

// Pre-loaded realistic data feeds
const searchKeywords = ['chicken', 'biryani', 'paneer', 'dosa', 'salad', 'smoothie', 'rice', 'curry'];
const cuisines = ['Indian', 'Italian', 'Mexican', 'Asian', 'Mediterranean'];
const dietTypes = ['Vegetarian', 'Non-Vegetarian', 'High-Protein', 'Low-Carb'];

export default function () {
  const vuId = __VU;
  const iter = __ITER;
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': `Tastio-k6-LoadTest/1.0 (VU ${vuId})`
    },
    timeout: '10s'
  };

  // User Journey Flow across Subsystems

  // 1. Health & Status Probe (PERF-001 - PERF-006)
  group('01_Health_Baseline', function () {
    const res = http.get(`${BASE_URL}/api/health`, params);
    const passed = check(res, {
      'health status is 200': (r) => r.status === 200,
      'health payload indicates healthy': (r) => r.json('status') === 'healthy'
    });
    healthLatency.add(res.timings.duration);
    if (passed) {
      successfulRequests.add(1);
      errorRate.add(0);
    } else {
      failedRequests.add(1);
      errorRate.add(1);
    }
  });

  sleep(0.1);

  // 2. Recipe Catalog & Discovery (PERF-007 - PERF-022)
  group('02_Catalog_Discovery', function () {
    const page = (iter % 5) + 1;
    const res = http.get(`${BASE_URL}/api/recipes?page=${page}&limit=20`, params);
    const passed = check(res, {
      'recipes status is 200': (r) => r.status === 200,
      'recipes list is returned': (r) => {
        const json = r.json();
        return Array.isArray(json) || (json && Array.isArray(json.recipes));
      }
    });
    catalogLatency.add(res.timings.duration);
    if (passed) {
      successfulRequests.add(1);
      errorRate.add(0);
    } else {
      failedRequests.add(1);
      errorRate.add(1);
    }

    // Single Recipe Lookup
    const recipeId = (iter % 230) + 1;
    const detailRes = http.get(`${BASE_URL}/api/recipes/${recipeId}`, params);
    check(detailRes, {
      'recipe detail status is 200': (r) => r.status === 200
    });
  });

  sleep(0.1);

  // 3. Search & Multi-Criteria Filtering (PERF-023 - PERF-050)
  group('03_Search_Filters', function () {
    const keyword = searchKeywords[iter % searchKeywords.length];
    const cuisine = cuisines[iter % cuisines.length];
    const diet = dietTypes[iter % dietTypes.length];

    const filterPayload = JSON.stringify({
      search: keyword,
      cuisine: cuisine,
      diet: diet,
      max_calories: 600
    });

    const res = http.post(`${BASE_URL}/api/recipes/filter`, filterPayload, params);
    const passed = check(res, {
      'filter status is 200': (r) => r.status === 200
    });
    searchLatency.add(res.timings.duration);
    if (passed) {
      successfulRequests.add(1);
      errorRate.add(0);
    } else {
      failedRequests.add(1);
      errorRate.add(1);
    }
  });

  sleep(0.1);

  // 4. Vector AI Semantic Recommendation (PERF-071 - PERF-110)
  group('04_Vector_Recommendation', function () {
    const recommendPayload = JSON.stringify({
      recipe_id: (iter % 50) + 1,
      target_calories: 500,
      user_id: 1,
      count: 5
    });

    const res = http.post(`${BASE_URL}/api/recommend`, recommendPayload, params);
    const passed = check(res, {
      'recommend status is 200': (r) => r.status === 200
    });
    recommendLatency.add(res.timings.duration);
    if (passed) {
      successfulRequests.add(1);
      errorRate.add(0);
    } else {
      failedRequests.add(1);
      errorRate.add(1);
    }
  });

  sleep(0.1);

  // 5. Pantry Matching / What Can I Cook (PERF-111 - PERF-145)
  group('05_Pantry_Matching', function () {
    const pantryPayload = JSON.stringify({
      ingredients: ['chicken', 'rice', 'onion', 'garlic', 'tomato'],
      max_missing: 3,
      sort_by: 'match_percentage'
    });

    const res = http.post(`${BASE_URL}/api/pantry-match`, pantryPayload, params);
    const passed = check(res, {
      'pantry match status is 200': (r) => r.status === 200
    });
    pantryLatency.add(res.timings.duration);
    if (passed) {
      successfulRequests.add(1);
      errorRate.add(0);
    } else {
      failedRequests.add(1);
      errorRate.add(1);
    }
  });

  sleep(0.1);

  // 6. 7-Day Meal Plan Engine (PERF-146 - PERF-185)
  group('06_Meal_Plan_Engine', function () {
    // Current meal plan retrieval
    const currentRes = http.get(`${BASE_URL}/api/meal-plan/current?user_id=1`, params);
    const passedCurrent = check(currentRes, {
      'current meal plan status is 200': (r) => r.status === 200
    });
    mealPlanLatency.add(currentRes.timings.duration);

    // Alternatives lookup for slot swapping
    const altRes = http.get(`${BASE_URL}/api/meal-plan/alternatives?meal_type=Breakfast&diet=weight_loss&user_id=1`, params);
    check(altRes, {
      'alternatives status is 200': (r) => r.status === 200
    });

    if (passedCurrent) {
      successfulRequests.add(1);
      errorRate.add(0);
    } else {
      failedRequests.add(1);
      errorRate.add(1);
    }
  });

  sleep(0.1);

  // 7. Smart Grocery List Operations (PERF-186 - PERF-220)
  group('07_Grocery_Operations', function () {
    // Fetch grocery list
    const getRes = http.get(`${BASE_URL}/api/grocery-list?user_id=1`, params);
    const passed = check(getRes, {
      'grocery list status is 200': (r) => r.status === 200
    });
    groceryLatency.add(getRes.timings.duration);

    // Add custom item
    if (iter % 4 === 0) {
      const itemPayload = JSON.stringify({
        item_name: `Perf Grocery Item ${iter}`,
        category: 'Produce',
        user_id: 1
      });
      http.post(`${BASE_URL}/api/grocery-list/item`, itemPayload, params);
    }

    if (passed) {
      successfulRequests.add(1);
      errorRate.add(0);
    } else {
      failedRequests.add(1);
      errorRate.add(1);
    }
  });

  sleep(0.1);

  // 8. AI Nutrition Coach Chat Stream (PERF-221 - PERF-255)
  group('08_Coach_Chat', function () {
    if (iter % 3 === 0) {
      const coachPayload = JSON.stringify({
        message: 'What is a balanced breakfast for weight loss?',
        user_id: 1
      });
      const res = http.post(`${BASE_URL}/api/coach/chat`, coachPayload, params);
      const passed = check(res, {
        'coach chat status is 200': (r) => r.status === 200
      });
      coachLatency.add(res.timings.duration);
      if (passed) {
        successfulRequests.add(1);
        errorRate.add(0);
      } else {
        failedRequests.add(1);
        errorRate.add(1);
      }
    }
  });

  sleep(0.1);

  // 9. Vision Ingestion Status & Analytics (PERF-256 - PERF-280)
  group('09_Vision_Analytics', function () {
    const visionRes = http.get(`${BASE_URL}/api/vision/status`, params);
    check(visionRes, {
      'vision status is 200': (r) => r.status === 200
    });
    visionLatency.add(visionRes.timings.duration);

    const analyticsRes = http.get(`${BASE_URL}/api/analytics/nutrition?user_id=1`, params);
    check(analyticsRes, {
      'analytics status is 200': (r) => r.status === 200
    });
  });

  sleep(0.2);
}

// Export detailed summary for reporting and metrics processing
export function handleSummary(data) {
  return {
    'd:/recipie/Recipe-Recommendation/performance-tests/reports/k6-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: false })
  };
}

function textSummary(data, options) {
  const reqs = data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0;
  const rate = data.metrics.http_reqs ? data.metrics.http_reqs.values.rate.toFixed(2) : 0;
  const duration = data.metrics.http_req_duration ? data.metrics.http_req_duration.values : {};
  const failRate = data.metrics.http_req_failed ? (data.metrics.http_req_failed.values.rate * 100).toFixed(2) : 0;

  return `
========================================================================
             TASTIO 100 VU 1-MINUTE LOAD TEST EXECUTION SUMMARY
========================================================================
Total HTTP Requests:      ${reqs}
Throughput (Reqs/Sec):    ${rate} RPS
Average Latency:          ${duration.avg ? duration.avg.toFixed(2) : 'N/A'} ms
Median Latency (p50):     ${duration.med ? duration.med.toFixed(2) : 'N/A'} ms
90th Percentile (p90):    ${duration['p(90)'] ? duration['p(90)'].toFixed(2) : 'N/A'} ms
95th Percentile (p95):    ${duration['p(95)'] ? duration['p(95)'].toFixed(2) : 'N/A'} ms
99th Percentile (p99):    ${duration['p(99)'] ? duration['p(99)'].toFixed(2) : 'N/A'} ms
Error Rate:               ${failRate} %
Virtual Users (Peak):     100 VUs
Duration:                 60 Seconds
========================================================================
`;
}

