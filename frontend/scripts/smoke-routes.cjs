#!/usr/bin/env node
/* eslint-disable no-console */
const routes = ['/', '/agenda', '/clientes', '/contratos', '/campanhas', '/viva', '/whatsapp', '/whatsapp/conversas'];
const baseUrl = process.env.FRONTEND_BASE_URL || 'http://localhost:3000';

async function run() {
  let failed = false;
  for (const route of routes) {
    const url = `${baseUrl}${route}`;
    try {
      const response = await fetch(url);
      const body = await response.text();
      const moduleMissing = body.includes("Cannot find module './");
      if (!response.ok || moduleMissing) {
        failed = true;
        console.error(`[FAIL] ${route} status=${response.status} moduleMissing=${moduleMissing}`);
        continue;
      }
      console.log(`[OK] ${route} status=${response.status}`);
    } catch (error) {
      failed = true;
      console.error(`[FAIL] ${route} error=${String(error)}`);
    }
  }

  if (failed) {
    console.error('\nRoute smoke failed. If running Next dev, reset cache with: npm run dev:reset');
    process.exit(1);
  }
}

run();
