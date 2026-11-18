'use strict';
// Test-only host adaptation: the restricted Mac process cannot query host uptime.
// The upstream dock tests override uptime explicitly for boot-window scenarios.
// This preload changes only this Node process, never Mac settings or TV behavior.
require('os').uptime = function () { return 3600; };
