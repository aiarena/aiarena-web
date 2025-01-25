import { test, expect } from '@playwright/test';

test.describe('Unauthenticated redirect', () => {
  test('should redirct to root and display correct title', async ({ page }) => {
    await page.goto('/profile/');
    await expect(page).toHaveTitle(/AI Arena/);
  });
});

