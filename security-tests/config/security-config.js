// security-config.js - Enterprise Configuration for Tastio Security Assessment
const path = require('path');

module.exports = {
  baseUrl: process.env.TASTIO_SECURITY_URL || 'http://127.0.0.1:5000',
  paths: {
    backendDir: path.join(__dirname, '..', '..', 'backend'),
    mobileDir: path.join(__dirname, '..', '..', 'mobile-app'),
    reportsDir: path.join(__dirname, '..', 'reports'),
    mainExcelReport: path.join(__dirname, '..', 'reports', 'security-test-report.xlsx'),
    findingsExcel: path.join(__dirname, '..', 'reports', 'findings.xlsx'),
    inventoryExcel: path.join(__dirname, '..', 'reports', 'endpoint-inventory.xlsx'),
    securityReviewMd: path.join(__dirname, '..', 'reports', 'security-review.md'),
    executiveSummaryMd: path.join(__dirname, '..', 'reports', 'executive-summary.md'),
    dependencyReportMd: path.join(__dirname, '..', 'reports', 'dependency-report.md')
  },
  severityLevels: {
    CRITICAL: { color: '991B1B', weight: 4 },
    HIGH: { color: 'C2410C', weight: 3 },
    MEDIUM: { color: 'B45309', weight: 2 },
    LOW: { color: '0369A1', weight: 1 },
    INFO: { color: '475569', weight: 0 }
  }
};

