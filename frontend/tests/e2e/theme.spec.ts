import { test, expect, type Page } from "@playwright/test";
import { resolve } from "node:path";

async function toggleTheme(page: Page) {
  await page.locator(".theme-trigger").click();
}

async function login(page: Page, phone: string, password: string) {
  const csrf = await page.request.get("/api/v1/auth/csrf");
  const token = (await csrf.json()).data.csrf_token;
  const response = await page.request.post("/api/v1/auth/login", {
    headers: { "X-CSRFToken": token },
    data: { phone, password },
  });
  expect(response.ok()).toBe(true);
  // Each viewport uses the same temporary admin; reset its saved language
  // so the preceding viewport's English check cannot change this fixture.
  const freshCsrf = (await (await page.request.get("/api/v1/auth/csrf")).json())
    .data.csrf_token;
  expect(
    (
      await page.request.patch("/api/v1/me", {
        headers: { "X-CSRFToken": freshCsrf },
        data: { locale: "zh-CN" },
      })
    ).ok(),
  ).toBe(true);
}

async function snapshot(page: Page, name: string) {
  if (process.env.QA_SCREENSHOTS === "1")
    await page.screenshot({
      path: resolve(`../.tools/qa-theme-icon/${name}.png`),
      fullPage: true,
      animations: "disabled",
    });
}

test("a single header login entry leads to login and registration with the destination preserved", async ({
  page,
}) => {
  await page.goto("/");
  const header = page.locator(".site-header");
  await expect(
    header.getByRole("link", { name: "登录", exact: true }),
  ).toHaveCount(1);
  await expect(header.getByRole("link", { name: /注册/ })).toHaveCount(0);
  await header.getByRole("link", { name: "登录", exact: true }).click();
  await expect(page).toHaveURL(/\/login$/);
  await page
    .locator(".auth-tabs")
    .getByRole("link", { name: "立即注册" })
    .click();
  await expect(page.getByLabel("怎么称呼你")).toBeVisible();
  await page.goto("/login?redirect=/courses/1/quiz");
  await page
    .locator(".auth-tabs")
    .getByRole("link", { name: "立即注册" })
    .click();
  expect(new URL(page.url()).searchParams.get("redirect")).toBe(
    "/courses/1/quiz",
  );
  await page
    .locator(".auth-tabs")
    .getByRole("link", { name: "登录", exact: true })
    .click();
  expect(new URL(page.url()).searchParams.get("redirect")).toBe(
    "/courses/1/quiz",
  );
});

test("icon toggles immediately, follows the system initially and resets on every new visit", async ({
  page,
  context,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  // A preference stored by the previous UI must not affect new visits.
  await context.addInitScript(() =>
    localStorage.setItem("learnhub-theme", "dark"),
  );
  await page.emulateMedia({ colorScheme: "light" });
  await page.goto("/");
  await expect(page.locator("html")).toHaveAttribute(
    "data-theme-preference",
    "system",
  );
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  const trigger = page.locator(".theme-trigger");
  await expect(trigger).toHaveText("");
  await expect(trigger.locator("svg")).toHaveCount(1);
  await expect(trigger).toHaveAccessibleName("切换为深色模式");
  await expect(page.locator(".course-card")).toHaveCount(3);
  await snapshot(page, "home-light-desktop");
  await page.emulateMedia({ colorScheme: "dark" });
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await snapshot(page, "home-dark-desktop");
  await toggleTheme(page);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await expect(page.getByRole("menu")).toHaveCount(0);
  await expect(trigger).toHaveAccessibleName("切换为深色模式");
  await page.emulateMedia({ colorScheme: "light" });
  await page.emulateMedia({ colorScheme: "dark" });
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  // Internal navigation keeps the current document's manual choice.
  await page
    .locator(".main-nav")
    .getByRole("link", { name: "课程列表", exact: true })
    .click();
  await expect(page).toHaveURL(/\/courses$/);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  expect(
    await page.evaluate(() => localStorage.getItem("learnhub-theme")),
  ).toBe("dark");
  expect(
    await page.evaluate(() => sessionStorage.getItem("learnhub-theme")),
  ).toBeNull();
  const other = await context.newPage();
  await other.emulateMedia({ colorScheme: "dark" });
  await other.goto("/");
  await expect(other.locator("html")).toHaveAttribute(
    "data-theme-preference",
    "system",
  );
  await expect(other.locator("html")).toHaveAttribute("data-theme", "dark");
  await other.close();
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute(
    "data-theme-preference",
    "system",
  );
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.emulateMedia({ colorScheme: "light" });
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await toggleTheme(page);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  // Opening a URL again also resets; it is not only a homepage behavior.
  await page.goto("/register");
  await expect(page.locator("html")).toHaveAttribute(
    "data-theme-preference",
    "system",
  );
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  expect(errors).toEqual([]);
});

test("icon button supports Enter and Space without clearing form input", async ({
  page,
}) => {
  await page.emulateMedia({ colorScheme: "light" });
  await page.goto("/register");
  await page.getByLabel("怎么称呼你").fill("主题验收");
  await page.getByLabel("手机号", { exact: true }).fill("13800000201");
  const trigger = page.locator(".theme-trigger");
  await trigger.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(trigger).toHaveAccessibleName("切换为浅色模式");
  await expect(trigger).toBeFocused();
  await page.keyboard.press("Space");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await expect(trigger).toHaveAccessibleName("切换为深色模式");
  await expect(page.getByLabel("怎么称呼你")).toHaveValue("主题验收");
  await expect(page.getByLabel("手机号", { exact: true })).toHaveValue(
    "13800000201",
  );
  await expect(page.getByRole("menu")).toHaveCount(0);
  await page.getByRole("button", { name: "Switch to English" }).click();
  await expect(trigger).toHaveAccessibleName("Switch to dark mode");
  await trigger.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(trigger).toHaveAccessibleName("Switch to light mode");
});

for (const width of [375, 768, 1440]) {
  test(`dark mode keeps public, learning and admin pages usable at ${width}px`, async ({
    page,
  }) => {
    test.setTimeout(60000);
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.setViewportSize({ width, height: 1000 });
    await page.emulateMedia({ colorScheme: "dark" });
    for (const path of ["/", "/courses", "/courses/1", "/login", "/register"]) {
      await page.goto(path);
      await expect(page.locator("h1")).toBeVisible();
      await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        path,
      ).toBe(false);
      if (path === "/") {
        await expect(page.locator(".course-card")).toHaveCount(3);
        await snapshot(page, `home-dark-${width}`);
      }
    }
    const csrf = await page.request.get("/api/v1/auth/csrf");
    const phone = `1380000${String(width).padStart(4, "0")}`;
    expect(
      (
        await page.request.post("/api/v1/auth/register", {
          headers: { "X-CSRFToken": (await csrf.json()).data.csrf_token },
          data: {
            phone,
            nickname: "主题验收",
            password: "ThemeTest123",
            confirm_password: "ThemeTest123",
            locale: "zh-CN",
          },
        })
      ).ok(),
    ).toBe(true);
    await login(page, phone, "ThemeTest123");
    await page.goto("/courses/1");
    await page.getByRole("button", { name: "加入学习", exact: true }).click();
    await expect(page.getByRole("status")).toContainText("已加入");
    for (const path of [
      "/learn/1/1",
      "/courses/1/quiz",
      "/my-learning",
      "/settings",
      "/assistant",
      "/results",
    ]) {
      await page.goto(path);
      await expect(page.locator("h1")).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        path,
      ).toBe(false);
      if (path === "/learn/1/1") {
        await expect(page.locator(".markdown-text")).toBeVisible();
        await snapshot(page, `lesson-dark-${width}`);
      }
    }
    await page.goto("/courses/1/quiz");
    const answer = page.locator('.quiz-question input[value="a"]').first();
    await answer.check();
    await toggleTheme(page);
    await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
    await expect(answer).toBeChecked();
    await toggleTheme(page);
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(answer).toBeChecked();
    await login(page, "13900000000", "TestAdmin123");
    for (const path of [
      "/admin",
      "/admin/courses",
      "/admin/courses/1/edit",
      "/admin/categories",
      "/admin/users",
    ]) {
      await page.goto(path);
      await expect(
        page.getByRole("heading", { name: "管理后台", exact: true }),
      ).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        path,
      ).toBe(false);
      if (path === "/admin/courses/1/edit")
        await snapshot(page, `admin-dark-${width}`);
    }
    await page.getByRole("button", { name: "Switch to English" }).click();
    await expect(
      page.getByRole("button", { name: "切换为中文" }),
    ).toBeEnabled();
    await page.goto("/");
    await expect(page.locator(".course-card")).toHaveCount(3);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      ),
    ).toBe(false);
    await snapshot(page, `home-dark-en-${width}`);
    expect(errors).toEqual([]);
  });
}
