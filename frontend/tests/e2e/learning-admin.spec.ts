import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";

async function write(
  request: APIRequestContext,
  path: string,
  method: string,
  data: unknown = {},
) {
  const csrf = (await (await request.get("/api/v1/auth/csrf")).json()).data
    .csrf_token;
  return request.fetch("/api/v1" + path, {
    method,
    data,
    headers: { "X-CSRFToken": csrf },
  });
}
async function learner(page: Page, phone: string, nickname = "学习验收") {
  expect(
    (
      await write(page.request, "/auth/register", "POST", {
        phone,
        nickname,
        password: "Learning123",
        confirm_password: "Learning123",
      })
    ).status(),
  ).toBe(201);
  await signIn(page, phone, "Learning123");
}
async function signIn(page: Page, phone: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("手机号", { exact: true }).fill(phone);
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登录学习坊" }).click();
  await expect(page).toHaveURL("http://127.0.0.1:5174/");
}

test("lessons, video resume, quiz retry, bilingual answers and completion", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await learner(page, "13800000101");
  await page.goto("/courses/1");
  await page.getByRole("button", { name: "加入学习", exact: true }).click();
  await page.getByRole("link", { name: "开始学习", exact: true }).click();
  await expect(page).toHaveURL(/learn\/1\/1$/);
  await expect(page.locator(".markdown-text")).toContainText("第一个页面");
  const video = page.locator("video");
  await expect
    .poll(() => video.evaluate((v: HTMLVideoElement) => v.readyState))
    .toBeGreaterThanOrEqual(1);
  await video.evaluate((v: HTMLVideoElement) => {
    v.currentTime = 3;
    v.dispatchEvent(new Event("pause"));
  });
  await expect
    .poll(async () => {
      const r = await page.request.get("/api/v1/courses/1/lessons/1");
      return (await r.json()).data.lesson.progress.video_position;
    })
    .toBeGreaterThanOrEqual(3);
  await page.reload();
  await expect
    .poll(() =>
      page.locator("video").evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBeGreaterThanOrEqual(2.8);
  for (let id = 1; id <= 4; id++) {
    if (id > 1) await page.goto(`/learn/1/${id}`);
    await page.getByRole("button", { name: "标记完成", exact: true }).click();
    await expect(
      page.getByText(`已完成 ${id} / 4 课时`, { exact: true }),
    ).toBeVisible();
  }
  await page.goto("/my-learning");
  await expect(page.getByText("待完成测验", { exact: true })).toBeVisible();
  await page.getByRole("link", { name: "结课测验", exact: true }).click();
  await expect(page.locator(".quiz-question")).toHaveCount(3);
  for (let i = 0; i < 3; i++)
    await page
      .locator(".quiz-question")
      .nth(i)
      .locator('input[value="a"]')
      .check();
  await page.getByRole("button", { name: "Switch to English" }).click();
  await expect(
    page.getByRole("button", { name: "Submit answers" }),
  ).toBeVisible();
  for (let i = 0; i < 3; i++)
    await expect(
      page.locator(".quiz-question").nth(i).locator('input[value="a"]'),
    ).toBeChecked();
  await page.getByRole("button", { name: "切换为中文" }).click();
  await page.getByRole("button", { name: "提交答案" }).click();
  await expect(page.locator(".result-summary")).toContainText("尚未通过");
  await page.getByRole("button", { name: "重新作答" }).click();
  for (let i = 0; i < 3; i++)
    await page
      .locator(".quiz-question")
      .nth(i)
      .locator(`input[value="${"abc"[i]}"]`)
      .check();
  await page.getByRole("button", { name: "提交答案" }).click();
  await expect(page.locator(".result-summary")).toContainText("测验通过");
  await expect(page.locator(".answer-review")).toHaveCount(3);
  await expect(page.locator(".history-list li")).toHaveCount(2);
  await page.goto("/my-learning");
  await expect(page.getByText("课程已完成", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "退出登录", exact: true }).click();
  await expect(
    page.getByRole("link", { name: "登录", exact: true }),
  ).toBeVisible();
  await signIn(page, "13800000101", "Learning123");
  await page.goto("/my-learning");
  await expect(page.getByText("课程已完成", { exact: true })).toBeVisible();
  expect(errors).toEqual([]);
});

test("administrator creates bilingual content, validates publishing and preserves withdrawn learning", async ({
  page,
  browser,
}) => {
  test.setTimeout(90000);
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("dialog", (dialog) => dialog.accept());
  await signIn(page, "13900000000", "TestAdmin123");
  await page.goto("/admin");
  await expect(page.locator(".stats-grid")).toBeVisible();
  await page.goto("/admin/categories");
  await page.getByRole("button", { name: "新增分类" }).click();
  await page.getByLabel("标识（小写英文和短横线）").fill("practice");
  await page.getByLabel("中文名称").fill("练习课程");
  await page.getByLabel("英文名称").fill("Practice");
  await page.getByRole("button", { name: "保存", exact: true }).click();
  await expect(
    page.getByRole("cell", { name: "Practice", exact: true }),
  ).toBeVisible();
  await page.goto("/admin/courses");
  await page.getByRole("button", { name: "新建课程" }).click();
  await page.getByLabel("标识（小写英文和短横线）").fill("acceptance-course");
  await page
    .getByRole("textbox", { name: "中文标题", exact: true })
    .fill("验收课程");
  await page
    .getByRole("textbox", { name: "英文标题", exact: true })
    .fill("Acceptance course");
  await page
    .getByRole("combobox", { name: "分类", exact: true })
    .selectOption({ label: "练习课程" });
  await page.getByRole("button", { name: "保存", exact: true }).click();
  await expect(page).toHaveURL(/admin\/courses\/\d+\/edit/);
  const courseId = Number(new URL(page.url()).pathname.split("/")[3]);
  await page.getByRole("button", { name: "发布课程", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("至少需要一个有效课时");
  await page.getByLabel("中文简介").fill("用于验证完整的学习和管理流程。");
  await page
    .getByLabel("英文简介")
    .fill("A course for validating the full workflow.");
  await page.getByLabel("中文目标（每行一条）").fill("理解基本概念");
  await page.getByLabel("英文目标（每行一条）").fill("Understand the basics");
  await page.getByRole("button", { name: "保存", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("已保存");
  await page.getByRole("button", { name: "章节与课时", exact: true }).click();
  await page.getByRole("button", { name: "添加章节", exact: true }).click();
  await page
    .getByRole("textbox", { name: "中文标题", exact: true })
    .fill("第一章");
  await page
    .getByRole("textbox", { name: "英文标题", exact: true })
    .fill("Chapter one");
  await page.getByRole("button", { name: "保存", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "第一章", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "添加课时", exact: true }).click();
  await page
    .getByRole("textbox", { name: "中文标题", exact: true })
    .fill("第一课");
  await page
    .getByRole("textbox", { name: "英文标题", exact: true })
    .fill("First lesson");
  await page
    .getByLabel("中文正文（Markdown）")
    .fill("# 课文\n\n这是一段完整的课时正文。");
  await page
    .getByLabel("英文正文（Markdown）")
    .fill("# Lesson\n\nThis is a complete lesson.");
  await page.getByRole("button", { name: "预览课文" }).click();
  await expect(page.locator(".editor-preview")).toContainText("完整的课时正文");
  await page.getByRole("button", { name: "保存", exact: true }).click();
  await expect(page.locator(".lesson-row")).toContainText("第一课");
  await page.getByRole("button", { name: "结课测验", exact: true }).click();
  await page.getByRole("button", { name: "保存", exact: true }).click();
  for (let i = 1; i <= 3; i++) {
    await page.getByRole("button", { name: "添加题目", exact: true }).click();
    await page.getByLabel("中文题干").fill(`题目${i}`);
    await page.getByLabel("英文题干").fill(`Question ${i}`);
    for (const id of ["a", "b", "c"]) {
      await page
        .getByLabel(`中文选项 ${id}`, { exact: true })
        .fill(`选项${id}`);
      await page
        .getByLabel(`英文选项 ${id}`, { exact: true })
        .fill(`Option ${id}`);
    }
    await page.getByLabel("正确选项").selectOption("b");
    await page.getByLabel("中文解析").fill("B 是正确选项。");
    await page.getByLabel("英文解析").fill("B is correct.");
    if (i === 2) {
      await page.getByRole("button", { name: "Switch to English" }).click();
      await expect(page.getByLabel("Chinese question")).toHaveValue("题目2");
      await page.getByRole("button", { name: "切换为中文" }).click();
    }
    await page
      .locator(".inline-editor")
      .getByRole("button", { name: "保存", exact: true })
      .click();
    await expect(page.locator(".inline-editor")).toHaveCount(0);
  }
  await page.getByRole("button", { name: "发布课程", exact: true }).click();
  await expect(page.locator(".status-chip")).toHaveText("已发布");
  const context = await browser.newContext({
    locale: "zh-CN",
    baseURL: "http://127.0.0.1:5174",
  });
  const student = await context.newPage();
  await student.goto("/");
  // A separate browser context has its own session and enrollment.
  await learner(student, "13800000102", "停用验收学员");
  await student.goto(`/courses/${courseId}`);
  await student.getByRole("button", { name: "加入学习", exact: true }).click();
  await student.getByRole("link", { name: "开始学习", exact: true }).click();
  await expect(student.locator(".markdown-text")).toContainText(
    "完整的课时正文",
  );
  await page.getByRole("button", { name: "下架课程", exact: true }).click();
  await expect(page.locator(".status-chip")).toHaveText("已下架");
  await student.reload();
  await expect(student.getByRole("alert")).toContainText("课程不存在或已下架");
  await student.goto("/my-learning");
  await expect(student.getByText("课程已下架，学习记录保留")).toBeVisible();
  await page.goto("/admin/users");
  await page.getByLabel("搜索昵称或手机号").fill("停用验收学员");
  await page.getByRole("button", { name: "搜索", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(1);
  await expect(page.getByRole("cell", { name: /\*\*\*\*/ })).toBeVisible();
  await page.getByRole("button", { name: "停用", exact: true }).click();
  await expect(
    page.getByRole("cell", { name: "已停用", exact: true }),
  ).toBeVisible();
  await student.reload();
  await expect(student).toHaveURL(/login\?redirect=/);
  await context.close();
  expect(errors).toEqual([]);
});

test("student cannot open admin pages or other students results", async ({
  page,
}) => {
  await learner(page, "13800000103");
  await page.goto("/admin/courses");
  await expect(page).toHaveURL(/forbidden$/);
  await expect(
    page.getByRole("heading", { name: "这里需要管理员权限" }),
  ).toBeVisible();
  expect((await page.request.get("/api/v1/admin/users")).status()).toBe(403);
  expect((await page.request.get("/api/v1/me/quiz-attempts/1")).status()).toBe(
    404,
  );
});

for (const width of [375, 768, 1440]) {
  test(`learning and admin remain usable at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await signIn(page, "13800000101", "Learning123");
    for (const path of [
      "/learn/1/1",
      "/courses/1/quiz",
      "/my-learning",
      "/settings",
    ]) {
      await page.goto(path);
      await expect(page.locator("h1")).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        path,
      ).toBe(false);
    }
    await page.getByRole("button", { name: "Switch to English" }).click();
    for (const path of [
      "/learn/1/1",
      "/courses/1/quiz",
      "/my-learning",
      "/settings",
    ]) {
      await page.goto(path);
      await expect(page.locator("h1")).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        path + " English",
      ).toBe(false);
    }
    await page.getByRole("button", { name: "切换为中文" }).click();
    await page.getByRole("button", { name: "退出登录", exact: true }).click();
    await expect(
      page.getByRole("button", { name: "退出登录", exact: true }),
    ).toHaveCount(0);
    await expect(page).toHaveURL("http://127.0.0.1:5174/");
    await signIn(page, "13900000000", "TestAdmin123");
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
    }
    await page.getByRole("button", { name: "Switch to English" }).click();
    for (const path of [
      "/admin",
      "/admin/courses",
      "/admin/courses/1/edit",
      "/admin/categories",
      "/admin/users",
    ]) {
      await page.goto(path);
      await expect(
        page.getByRole("heading", { name: "Administration", exact: true }),
      ).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        path + " English",
      ).toBe(false);
    }
    await page.getByRole("button", { name: "切换为中文" }).click();
    expect(errors).toEqual([]);
  });
}
