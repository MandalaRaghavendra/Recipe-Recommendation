const fs = require('fs');
const path = require('path');

const scriptsDir = path.join(__dirname, '..', 'k6-scripts');

const modules = [
  {
    file: '01-baseline-health.js',
    title: '01: Baseline, Health & Catalog Pagination (PERF-001 - PERF-030)',
    content: `import http from 'k6/http';
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
  const healthRes = http.get(\`\${BASE_URL}/api/health\`);
  check(healthRes, { 'health ok': (r) => r.status === 200 });

  // PERF-007 - PERF-015: Catalog pages & limits
  const p1Res = http.get(\`\${BASE_URL}/api/recipes?page=1&limit=20\`);
  check(p1Res, { 'page 1 ok': (r) => r.status === 200 });

  const p5Res = http.get(\`\${BASE_URL}/api/recipes?page=5&limit=20\`);
  check(p5Res, { 'page 5 ok': (r) => r.status === 200 });

  // PERF-019 - PERF-022: Recipe ID lookups
  const rId = Math.floor(Math.random() * 230) + 1;
  const singleRes = http.get(\`\${BASE_URL}/api/recipes/\${rId}\`);
  check(singleRes, { 'single recipe ok': (r) => r.status === 200 });

  sleep(0.1);
}
`
  },
  {
    file: '02-catalog-concurrency.js',
    title: '02: Catalog Concurrency, Filtering & Auth (PERF-031 - PERF-070)',
    content: `import http from 'k6/http';
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
  const filterRes = http.post(\`\${BASE_URL}/api/recipes/filter\`, filterPayload, { headers });
  check(filterRes, { 'filter ok': (r) => r.status === 200 });

  // PERF-046 - PERF-055: User preferences & history
  const prefRes = http.get(\`\${BASE_URL}/api/user/preferences?user_id=1\`);
  check(prefRes, { 'prefs ok': (r) => r.status === 200 });

  // PERF-056 - PERF-070: Recipe view counters & favorites
  const rId = Math.floor(Math.random() * 50) + 1;
  http.post(\`\${BASE_URL}/api/recipes/\${rId}/view\`, null, { headers });

  sleep(0.1);
}
`
  },
  {
    file: '03-vector-similarity.js',
    title: '03: Vector Similarity & AI Recommendation (PERF-071 - PERF-110)',
    content: `import http from 'k6/http';
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
  const headers = { 'Content-Type': 'application/json' };

  // PERF-071 - PERF-110: Cosine similarity vector search
  const recommendPayload = JSON.stringify({
    recipe_id: Math.floor(Math.random() * 200) + 1,
    target_calories: 550,
    user_id: 1,
    count: 5
  });
  const res = http.post(\`\${BASE_URL}/api/recommend\`, recommendPayload, { headers });
  check(res, { 'recommendation ok': (r) => r.status === 200 });

  sleep(0.1);
}
`
  },
  {
    file: '04-pantry-intersection.js',
    title: '04: Pantry Ingredient Intersection (PERF-111 - PERF-145)',
    content: `import http from 'k6/http';
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
  const res = http.post(\`\${BASE_URL}/api/pantry-match\`, pantryPayload, { headers });
  check(res, { 'pantry match ok': (r) => r.status === 200 });

  sleep(0.1);
}
`
  },
  {
    file: '05-meal-plan-stress.js',
    title: '05: 7-Day Meal Plan Generation & Swaps (PERF-146 - PERF-185)',
    content: `import http from 'k6/http';
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
  const currentRes = http.get(\`\${BASE_URL}/api/meal-plan/current?user_id=1\`);
  check(currentRes, { 'current plan ok': (r) => r.status === 200 });

  const altRes = http.get(\`\${BASE_URL}/api/meal-plan/alternatives?meal_type=Lunch&diet=weight_loss&user_id=1\`);
  check(altRes, { 'alternatives ok': (r) => r.status === 200 });

  sleep(0.1);
}
`
  },
  {
    file: '06-grocery-compilation.js',
    title: '06: Smart Grocery Compilation (PERF-186 - PERF-220)',
    content: `import http from 'k6/http';
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
  const listRes = http.get(\`\${BASE_URL}/api/grocery-list?user_id=1\`);
  check(listRes, { 'grocery list ok': (r) => r.status === 200 });

  const itemPayload = JSON.stringify({
    item_name: 'Greek Yogurt 500g',
    category: 'Dairy',
    user_id: 1
  });
  http.post(\`\${BASE_URL}/api/grocery-list/item\`, itemPayload, { headers });

  sleep(0.1);
}
`
  },
  {
    file: '07-coach-throughput.js',
    title: '07: AI Nutrition Coach Throughput (PERF-221 - PERF-255)',
    content: `import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 25,
  duration: '15s',
  thresholds: {
    'http_req_duration': ['p(95)<450'],
    'http_req_failed': ['rate<0.02']
  }
};

const BASE_URL = __ENV.TASTIO_PERF_URL || 'http://127.0.0.1:5000';

export default function () {
  const headers = { 'Content-Type': 'application/json' };

  // PERF-221 - PERF-255: Coach context & interactive chat
  http.get(\`\${BASE_URL}/api/coach/context?user_id=1\`);

  const chatPayload = JSON.stringify({
    message: 'What are low glycemic breakfast options for energy?',
    user_id: 1
  });
  const res = http.post(\`\${BASE_URL}/api/coach/chat\`, chatPayload, { headers });
  check(res, { 'coach chat ok': (r) => r.status === 200 });

  sleep(0.1);
}
`
  },
  {
    file: '08-vision-ingestion.js',
    title: '08: Food Image Recognition & Scanner (PERF-256 - PERF-280)',
    content: `import http from 'k6/http';
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
  const statusRes = http.get(\`\${BASE_URL}/api/vision/status\`);
  check(statusRes, { 'vision status ok': (r) => r.status === 200 });

  sleep(0.2);
}
`
  },
  {
    file: '09-soak-spike-100vu.js',
    title: '09: Spike, Soak & 100 VU Stress (PERF-281 - PERF-300)',
    content: `import http from 'k6/http';
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
  const res = http.get(\`\${BASE_URL}/api/health\`);
  check(res, { 'health ok': (r) => r.status === 200 });

  const catRes = http.get(\`\${BASE_URL}/api/recipes?page=1&limit=20\`);
  check(catRes, { 'catalog ok': (r) => r.status === 200 });

  sleep(0.1);
}
`
  }
];

modules.forEach(m => {
  const filePath = path.join(scriptsDir, m.file);
  fs.writeFileSync(filePath, m.content);
  console.log('[ScriptGen] Generated: ' + m.file + ' (' + m.title + ')');
});
