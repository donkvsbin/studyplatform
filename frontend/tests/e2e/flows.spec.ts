import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

async function createAIUser(page: Page, phone: string) {
  const csrf = await page.request.get("/api/v1/auth/csrf");
  const token = (await csrf.json()).data.csrf_token;
  const response = await page.request.post("/api/v1/auth/register", {
    headers: { "X-CSRFToken": token },
    data: {
      phone,
      nickname: "AI tester",
      password: "Acceptance123",
      confirm_password: "Acceptance123",
      locale: "en",
    },
  });
  expect(response.status()).toBe(201);
}

test("register, log in, enroll, refresh, change language and log out", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/my-learning");
  await expect(page).toHaveURL(/login\?redirect=/);
  await page.getByRole("link", { name: "立即注册" }).click();
  await page.getByLabel("怎么称呼你").fill("验收学员");
  await page.getByLabel("手机号", { exact: true }).fill("13812345678");
  await page.getByLabel("密码", { exact: true }).fill("Acceptance123");
  await page.getByLabel("确认密码").fill("Acceptance123");
  await page.getByRole("button", { name: "创建免费账号" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "注册成功，请登录你的账号。",
  );
  await page.getByLabel("手机号", { exact: true }).fill("13812345678");
  await page.getByLabel("密码", { exact: true }).fill("Acceptance123");
  await page.getByRole("button", { name: "登录学习坊" }).click();
  await expect(page).toHaveURL(/my-learning$/);
  await expect(page.getByText("你的学习旅程，正要开始")).toBeVisible();
  await page.goto("/courses/1");
  await page.getByRole("button", { name: "加入学习", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("已加入");
  await page.reload();
  await expect(page.getByRole("link", { name: "已加入学习" })).toBeVisible();
  await page.getByRole("link", { name: "已加入学习" }).click();
  await expect(page.locator(".course-card")).toHaveCount(1);
  await page.getByRole("button", { name: "Switch to English" }).click();
  await expect(
    page.getByRole("heading", { name: "Web Foundations" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Web Foundations" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(
    page.getByRole("link", { name: "Log in", exact: true }),
  ).toBeVisible();
  await page.goto("/settings");
  await expect(page).toHaveURL(/login\?redirect=/);
  expect(errors).toEqual([]);
});

test("catalog search, filters, empty state and bilingual details", async ({
  page,
}) => {
  await page.goto("/courses");
  await expect(page.locator(".course-card")).toHaveCount(3);
  await page.getByRole("button", { name: "Python 编程", exact: true }).click();
  await expect(page.locator(".course-card")).toHaveCount(1);
  await expect(
    page.getByRole("heading", { name: "Python 入门" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "清除筛选" }).click();
  await page.getByRole("searchbox").fill("不存在的课程");
  await page.getByRole("button", { name: "搜索", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "还没有找到这门课" }),
  ).toBeVisible();
  await page.goto("/courses/1");
  await expect(page.locator(".chapter-panel")).toHaveCount(2);
  await page.getByRole("button", { name: "Switch to English" }).click();
  await expect(
    page.getByRole("heading", { name: "Web Foundations", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("How a web page is built", { exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Web Foundations", exact: true }),
  ).toBeVisible();
});

test("AI missing-key state is clear and does not fabricate answers", async ({
  page,
}) => {
  await createAIUser(page, "13812345679");
  await page.goto("/login?redirect=/assistant?course=1");
  await page.getByLabel("手机号", { exact: true }).fill("13812345679");
  await page.getByLabel("密码", { exact: true }).fill("Acceptance123");
  await page.getByRole("button", { name: "登录学习坊" }).click();
  await expect(page).toHaveURL(/assistant\?course=1/);
  await expect(
    page.getByText("Your study buddy is not connected yet"),
  ).toBeVisible();
  await expect(page.locator(".chat-context")).toContainText("Web Foundations");
  await expect(
    page.getByRole("button", { name: "Send question" }),
  ).toBeDisabled();
  await expect(page.getByLabel("Your learning question")).toBeDisabled();
});

test("AI chat success, safe markdown and retry keep question text", async ({
  page,
}) => {
  await createAIUser(page, "13812345680");
  await page.route("**/api/v1/assistant/status**", (route) =>
    route.fulfill({ json: { data: { configured: true } } }),
  );
  await page.goto("/login?redirect=/assistant");
  await page.getByLabel("手机号", { exact: true }).fill("13812345680");
  await page.getByLabel("密码", { exact: true }).fill("Acceptance123");
  await page.getByRole("button", { name: "登录学习坊" }).click();
  await expect(page.getByLabel("Your learning question")).toBeEnabled();
  let calls = 0;
  await page.route("**/api/v1/assistant/chat**", (route) => {
    calls++;
    return calls === 1
      ? route.fulfill({ status: 504, json: { error: { code: "ai_timeout" } } })
      : route.fulfill({
          json: {
            data: {
              answer:
                "A **variable** names a value.\n\n<script>window.injected=true</script>",
            },
          },
        });
  });
  await page.getByLabel("Your learning question").fill("What is a variable?");
  await page.getByRole("button", { name: "Send question" }).click();
  await expect(page.getByRole("alert")).toContainText("timed out");
  await expect(page.getByLabel("Your learning question")).toHaveValue(
    "What is a variable?",
  );
  await page.getByRole("button", { name: "Send question" }).click();
  await expect(page.locator(".message.assistant")).toContainText("variable");
  expect(await page.evaluate(() => Object.hasOwn(window, "injected"))).toBe(
    false,
  );
  await page.getByRole("button", { name: "New conversation" }).click();
  await expect(page.locator(".message")).toHaveCount(0);
});

test("profile and password settings have real behavior", async ({ page }) => {
  await createAIUser(page, "13812345681");
  await page.goto("/login?redirect=/settings");
  await page.getByLabel("手机号", { exact: true }).fill("13812345681");
  await page.getByLabel("密码", { exact: true }).fill("Acceptance123");
  await page.getByRole("button", { name: "登录学习坊" }).click();
  await expect(
    page.getByRole("heading", { name: "Your profile" }),
  ).toBeVisible();
  await page.getByLabel("What should we call you?").fill("Updated learner");
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect(page.getByRole("status")).toHaveText("Saved");
  await page.reload();
  await expect(page.getByLabel("What should we call you?")).toHaveValue(
    "Updated learner",
  );
  await page.getByLabel("Current password").fill("Acceptance123");
  await page
    .getByLabel("New password", { exact: true })
    .fill("NewAcceptance123");
  await page.getByLabel("Confirm password").fill("NewAcceptance123");
  await page.getByRole("button", { name: "Change password" }).click();
  await expect(page).toHaveURL(/login\?changed=1/);
  await page.getByLabel("Phone number", { exact: true }).fill("13812345681");
  await page.getByLabel("Password", { exact: true }).fill("NewAcceptance123");
  await page.getByRole("button", { name: "Log in to LearnHub" }).click();
  await expect(page).toHaveURL("http://127.0.0.1:5174/");
  await page.route("**/api/v1/me/enrollments**", (route) =>
    route.fulfill({
      status: 401,
      json: { error: { code: "unauthenticated" } },
    }),
  );
  await page.goto("/my-learning");
  await expect(page).toHaveURL(/login\?redirect=/);
});

for (const width of [375, 768, 1440]) {
  test(`responsive pages at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    for (const path of [
      "/",
      "/courses",
      "/courses/1",
      "/login",
      "/register",
      "/assistant",
      "/not-found",
    ]) {
      await page.goto(path);
      await expect(page.locator("h1")).toBeVisible();
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      );
      expect(overflow, `${path} overflow at ${width}px`).toBe(false);
    }
    expect(errors).toEqual([]);
  });
}
