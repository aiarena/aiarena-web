import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should display the correct title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/AI Arena/); 
  });

  test('should navigate to About page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=About us'); 
    await expect(page).toHaveURL('/about/');
    await expect(page.locator('h1')).toContainText('What is AI Arena?');
  });
});

