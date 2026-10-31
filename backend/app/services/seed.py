"""Original LearnHub bilingual content. No accounts or private user data."""

from ..extensions import db
from ..models import Category, Course, Chapter, Lesson

COURSES = [
    {
        "slug": "web-foundations",
        "category": ("web", "网页开发", "Web development"),
        "titles": ("网页基础", "Web Foundations"),
        "cover": "web",
        "description": (
            "从一张空白页面开始，认识 HTML 的结构与 CSS 的样式。用四个小课时，理解浏览器如何把代码变成你眼前的网页，并动手构建一个简单的个人介绍页。",
            "Start with a blank page and discover how HTML structure and CSS styles work together. In four short lessons, learn how browsers turn code into a page and build a simple personal introduction.",
        ),
        "objectives": (
            [
                "用语义化 HTML 描述内容",
                "为元素添加有层次的 CSS 样式",
                "用 Flexbox 创建简单布局",
                "组合结构与样式，完成个人介绍页",
            ],
            [
                "Describe content using semantic HTML",
                "Style elements with CSS selectors",
                "Create a simple Flexbox layout",
                "Combine structure and style in a personal page",
            ],
        ),
        "chapters": [
            (
                "认识网页的结构",
                "Meet the structure of the web",
                [
                    (
                        "网页是如何构成的",
                        "How a web page is built",
                        12,
                        '网页可以分成三层：HTML 描述内容，CSS 决定外观，JavaScript 提供交互。浏览器读取这些文件，再把结果绘制在屏幕上。\n\n## 第一个页面\n\n把下面的代码保存为 `index.html`，然后用浏览器打开：\n\n```html\n<!doctype html>\n<html lang="zh-CN">\n  <head><meta charset="UTF-8"><title>我的起点</title></head>\n  <body><h1>你好，世界</h1><p>这是我的第一个网页。</p></body>\n</html>\n```\n\n`head` 保存页面信息；`body` 保存显示的内容。`h1` 是一级标题，`p` 是段落。\n\n## 动手试试\n\n把标题换成你的名字，保存文件并刷新浏览器。修改源码不会自动改变已经打开的文件，刷新会重新读取它。',
                        'A web page has three layers: HTML describes content, CSS controls appearance, and JavaScript adds interaction. A browser reads these files and paints the result on screen.\n\n## Your first page\n\nSave this as `index.html` and open it in a browser:\n\n```html\n<!doctype html>\n<html lang="en">\n  <head><meta charset="UTF-8"><title>My starting point</title></head>\n  <body><h1>Hello, world</h1><p>This is my first page.</p></body>\n</html>\n```\n\nThe `head` holds page information. The `body` holds visible content. An `h1` is a main heading and a `p` is a paragraph.\n\n## Try it\n\nReplace the heading with your name, save, and refresh the browser. Refreshing reads the changed file again.',
                    ),
                    (
                        "让内容有意义：常用 HTML 元素",
                        "Give content meaning with HTML",
                        15,
                        '选择 HTML 元素时，先问内容是什么，而不是希望它长什么样。标题使用 `h1` 到 `h6`，列表使用 `ul` 和 `li`，导航链接使用 `a`，触发动作使用 `button`。\n\n```html\n<main>\n  <h1>我的学习清单</h1>\n  <ul><li>认识 HTML</li><li>学习 CSS</li></ul>\n  <a href="https://developer.mozilla.org/">阅读网页文档</a>\n  <button type="button">记录灵感</button>\n</main>\n```\n\n链接负责导航，按钮负责操作。给图片提供描述内容的 `alt`，也让不能看到图片的读者理解它。\n\n## 动手试试\n\n把个人介绍页分成标题、简介、兴趣列表。按 Tab 键检查链接和按钮是否能被选中。好的结构能同时帮助读者、搜索工具和辅助技术。',
                        'Choose an HTML element by asking what the content means before deciding how it should look. Use `h1` through `h6` for headings, `ul` and `li` for lists, `a` for navigation, and `button` for actions.\n\n```html\n<main>\n  <h1>My learning list</h1>\n  <ul><li>Meet HTML</li><li>Learn CSS</li></ul>\n  <a href="https://developer.mozilla.org/">Read web documentation</a>\n  <button type="button">Save an idea</button>\n</main>\n```\n\nLinks navigate; buttons perform actions. Describe meaningful images with `alt` text so people who cannot see them can understand their purpose.\n\n## Try it\n\nGive your introduction a heading, a paragraph and a list of interests. Press Tab to check that links and buttons can receive focus. Meaningful structure helps readers and assistive tools.',
                    ),
                ],
            ),
            (
                "给网页一点风格",
                "Give your page some style",
                [
                    (
                        "CSS 选择器与盒模型",
                        "CSS selectors and the box model",
                        18,
                        'CSS 规则由选择器和声明组成。类选择器 `.card` 匹配 `class="card"` 的元素；声明用属性和值描述样式。\n\n```css\n.card {\n  color: #194c40;\n  padding: 24px;\n  border: 1px solid #dde5dd;\n  margin: 16px;\n  border-radius: 12px;\n  box-sizing: border-box;\n}\n```\n\n盒模型从内到外是内容、内边距 padding、边框 border、外边距 margin。`border-box` 让声明的宽度包含内边距和边框，布局更容易计算。\n\n## 动手试试\n\n给介绍页的内容容器添加 `card` 类。分别修改 padding 和 margin，观察内部留白与外部间距的区别。样式只改变展示，不替代 HTML 的语义。',
                        'A CSS rule contains a selector and declarations. The class selector `.card` matches an element with `class="card"`. Declarations pair a property with a value.\n\n```css\n.card {\n  color: #194c40;\n  padding: 24px;\n  border: 1px solid #dde5dd;\n  margin: 16px;\n  border-radius: 12px;\n  box-sizing: border-box;\n}\n```\n\nFrom the inside out, the box model contains content, padding, a border and margin. With `border-box`, the declared width includes padding and borders.\n\n## Try it\n\nAdd the `card` class to your introduction container. Change padding and margin separately. Notice that padding creates space inside a box while margin separates it from neighbors. CSS changes appearance without replacing HTML meaning.',
                    ),
                    (
                        "用 Flexbox 搭建个人介绍页",
                        "Build a profile layout with Flexbox",
                        20,
                        "Flexbox 适合沿一个方向排列元素。在父元素设置 `display: flex`，子元素就会沿主轴排列。`gap` 提供间距，`flex-wrap` 允许换行。\n\n```css\n.profile { display: flex; gap: 24px; flex-wrap: wrap; }\n.bio { flex: 1; min-width: 220px; }\n@media (max-width: 600px) {\n  .profile { flex-direction: column; }\n}\n```\n\n默认主轴是水平的。`align-items` 沿交叉轴对齐，`justify-content` 沿主轴分配空间。\n\n## 完成一个小作品\n\n在个人页加入头像区域和简介区域，把它们放进 `.profile`。缩小浏览器，确认内容仍能阅读。不要给正文设置过小的固定宽度，给不同设备留下空间。",
                        "Flexbox arranges elements along one direction. Set `display: flex` on a parent to place its children along the main axis. Use `gap` for spacing and `flex-wrap` to allow wrapping.\n\n```css\n.profile { display: flex; gap: 24px; flex-wrap: wrap; }\n.bio { flex: 1; min-width: 220px; }\n@media (max-width: 600px) {\n  .profile { flex-direction: column; }\n}\n```\n\nThe default main axis is horizontal. `align-items` aligns along the cross axis, while `justify-content` distributes space on the main axis.\n\n## Build something small\n\nPut an avatar area and a biography inside `.profile`. Narrow the browser and check that everything remains readable. Avoid tiny fixed widths for text and leave room for different screens.",
                    ),
                ],
            ),
        ],
    },
    {
        "slug": "javascript-basics",
        "category": ("javascript", "JavaScript", "JavaScript"),
        "titles": ("JavaScript 入门", "JavaScript Basics"),
        "cover": "javascript",
        "description": (
            "让静态页面动起来。从变量与循环，到函数与 DOM 事件，认识 JavaScript 的基本思路。用简单可运行的例子，把重复操作交给代码，做出你的第一个网页交互。",
            "Bring a static page to life. Explore variables, loops, functions and DOM events through small runnable examples. Let code handle repeated work and build your first interactive web page.",
        ),
        "objectives": (
            [
                "理解变量、基本类型与数组",
                "使用条件和循环描述规则",
                "编写可复用的函数",
                "通过 DOM 事件更新网页内容",
            ],
            [
                "Understand variables, primitive types and arrays",
                "Express rules with conditions and loops",
                "Write reusable functions",
                "Update a page with DOM events",
            ],
        ),
        "chapters": [
            (
                "认识脚本的思路",
                "Think in small instructions",
                [
                    (
                        "变量与数据类型",
                        "Variables and data types",
                        15,
                        '变量给数据起名字。用 `const` 声明不重新赋值的绑定，用 `let` 声明需要改变的绑定。字符串用引号包围，数字可以计算，布尔值表示真假。\n\n```javascript\nconst learner = "Lin";\nlet lessons = 0;\nlessons = lessons + 1;\nconst ready = true;\nconsole.log(learner, lessons, ready);\n```\n\n数组保存有顺序的数据，例如 `const topics = ["HTML", "CSS"];`。数组下标从 0 开始，`topics[0]` 得到第一个值。\n\n## 动手试试\n\n在浏览器开发者工具的控制台运行例子。把 `lessons` 增加两次，比较数字 `1` 和字符串 `"1"`：相同的写法外观不代表相同的数据类型。',
                        'Variables give data a name. Use `const` for a binding you do not reassign and `let` for one you will change. Strings use quotes, numbers support arithmetic, and booleans represent true or false.\n\n```javascript\nconst learner = "Lin";\nlet lessons = 0;\nlessons = lessons + 1;\nconst ready = true;\nconsole.log(learner, lessons, ready);\n```\n\nArrays store ordered data: `const topics = ["HTML", "CSS"];`. Indexes start at zero, so `topics[0]` gives the first value.\n\n## Try it\n\nRun the example in your browser console. Increase `lessons` twice. Compare the number `1` with the string `"1"`: similar-looking values can have different types.',
                    ),
                    (
                        "条件判断与循环",
                        "Conditions and loops",
                        18,
                        '条件让程序选择分支，循环让程序重复操作。`if` 根据表达式是否为真执行代码；`for...of` 逐个读取数组中的值。\n\n```javascript\nconst scores = [50, 80, 90];\nfor (const score of scores) {\n  if (score >= 60) {\n    console.log("通过", score);\n  } else {\n    console.log("继续练习", score);\n  }\n}\n```\n\n`>=` 表示大于或等于，`===` 比较类型和值。不要把赋值 `=` 当成比较。\n\n## 动手试试\n\n增加一个 60 分的成绩，预测输出后再运行。边界值是检查条件的好方法。循环应有明确结束的条件，避免无休止地执行。',
                        'Conditions choose a path; loops repeat an action. An `if` statement runs code when an expression is true. A `for...of` loop reads each value in an array.\n\n```javascript\nconst scores = [50, 80, 90];\nfor (const score of scores) {\n  if (score >= 60) {\n    console.log("Passed", score);\n  } else {\n    console.log("Keep practicing", score);\n  }\n}\n```\n\n`>=` means greater than or equal to. `===` compares both type and value. Do not confuse assignment `=` with comparison.\n\n## Try it\n\nAdd a score of 60, predict the output and then run it. Boundary values help test a condition. Every loop should have a clear stopping point.',
                    ),
                ],
            ),
            (
                "让代码和网页互动",
                "Connect code to a page",
                [
                    (
                        "把步骤装进函数",
                        "Package steps into functions",
                        18,
                        '函数把一组步骤命名，参数提供输入，`return` 给出结果。调用函数时才执行函数体。\n\n```javascript\nfunction greet(name) {\n  return "你好，" + name;\n}\nconst message = greet("小林");\nconsole.log(message);\n```\n\n函数内声明的变量通常只在函数内可用，这是作用域。让输入输出清晰，可以减少依赖外部状态，使代码容易测试。\n\n## 动手试试\n\n写一个 `double(number)` 函数返回输入的两倍。分别传入 0、3 和 -2。先写出预期值，再观察运行结果。没有 `return` 的函数默认返回 `undefined`。',
                        'A function names a group of steps. Parameters provide input and `return` provides a result. The function body runs when the function is called.\n\n```javascript\nfunction greet(name) {\n  return "Hello, " + name;\n}\nconst message = greet("Lin");\nconsole.log(message);\n```\n\nVariables declared inside a function are usually local to it. This is scope. Clear inputs and outputs reduce reliance on outside state and make functions easier to test.\n\n## Try it\n\nWrite `double(number)` to return twice its input. Call it with 0, 3 and -2. Write your expected results before running it. A function without a `return` statement returns `undefined`.',
                    ),
                    (
                        "DOM 与按钮点击事件",
                        "DOM and button click events",
                        20,
                        'DOM 是浏览器中网页的对象表示。`querySelector` 找到元素，`addEventListener` 监听操作，`textContent` 安全地更新文字。\n\n```html\n<button id="hello" type="button">打个招呼</button>\n<p id="message"></p>\n<script>\n  const button = document.querySelector("#hello");\n  const message = document.querySelector("#message");\n  button.addEventListener("click", () => {\n    message.textContent = "你完成了第一次交互！";\n  });\n</script>\n```\n\n把脚本放在元素后面，让查找时元素已经存在。避免把不可信文字插入 `innerHTML`。\n\n## 动手试试\n\n做一个点击计数器：用变量记录次数，在事件中加一，再更新文字。让按钮也能通过键盘 Enter 触发。',
                        'The DOM is the browser’s object representation of a page. `querySelector` finds an element, `addEventListener` listens for actions, and `textContent` safely updates text.\n\n```html\n<button id="hello" type="button">Say hello</button>\n<p id="message"></p>\n<script>\n  const button = document.querySelector("#hello");\n  const message = document.querySelector("#message");\n  button.addEventListener("click", () => {\n    message.textContent = "Your first interaction works!";\n  });\n</script>\n```\n\nPlace the script after the elements so they exist when queried. Avoid inserting untrusted text using `innerHTML`.\n\n## Try it\n\nBuild a click counter: keep a count in a variable, increment it in the event handler and update the text. Check that Enter also activates the button.',
                    ),
                ],
            ),
        ],
    },
    {
        "slug": "python-basics",
        "category": ("python", "Python 编程", "Python programming"),
        "titles": ("Python 入门", "Python Basics"),
        "cover": "python",
        "description": (
            "用简洁的代码解决日常小问题。学习 Python 的变量、数据结构、流程控制与函数，再用一个小型数据处理练习，把零散的知识连起来，迈出自动化的第一步。",
            "Solve everyday problems with readable code. Learn Python variables, collections, control flow and functions, then connect the ideas in a small data-processing exercise—your first step toward automation.",
        ),
        "objectives": (
            [
                "使用列表和字典组织数据",
                "通过缩进理解条件与循环",
                "定义有输入与返回值的函数",
                "过滤并汇总一组学习记录",
            ],
            [
                "Organize data using lists and dictionaries",
                "Understand conditions, loops and indentation",
                "Define functions with inputs and return values",
                "Filter and summarize learning records",
            ],
        ),
        "chapters": [
            (
                "让 Python 认识你的数据",
                "Introduce your data to Python",
                [
                    (
                        "变量、列表与字典",
                        "Variables, lists and dictionaries",
                        15,
                        'Python 用名字引用值，不必先声明类型。列表保存顺序，字典把键映射到值。\n\n```python\nname = "小林"\ntopics = ["网页", "Python"]\nlearner = {"name": name, "lessons": 2}\nprint(topics[0])\nprint(learner["name"])\n```\n\n列表下标从 0 开始。字典的键必须存在才能直接读取，也可以用 `.get("key", default)` 提供默认值。\n\n## 动手试试\n\n把例子保存为 `hello.py` 并用 `python hello.py` 运行。向列表追加一个主题，修改字典中的课时数，再打印结果。注意字符串需要引号，变量名不需要。',
                        'Python names refer to values without a separate type declaration. A list preserves order; a dictionary maps keys to values.\n\n```python\nname = "Lin"\ntopics = ["Web", "Python"]\nlearner = {"name": name, "lessons": 2}\nprint(topics[0])\nprint(learner["name"])\n```\n\nList indexes begin at zero. A key must exist for direct dictionary access. Use `.get("key", default)` to provide a fallback.\n\n## Try it\n\nSave this as `hello.py` and run `python hello.py`. Append a topic, update the lesson count, and print the results. Strings need quotation marks; variable names do not.',
                    ),
                    (
                        "用条件和循环处理任务",
                        "Handle tasks with conditions and loops",
                        18,
                        'Python 用缩进表示代码块。一个代码块中的语句应保持相同缩进，通常使用四个空格。条件后和循环后需要冒号。\n\n```python\nminutes = [10, 25, 0, 15]\nfor value in minutes:\n    if value > 0:\n        print("学习了", value, "分钟")\n    else:\n        print("今天先休息")\n```\n\n`for` 逐个读取列表中的值。`range(3)` 依次产生 0、1、2，不包含结束值 3。\n\n## 动手试试\n\n用变量 `total = 0` 累加有效分钟数。预测结果后运行。不要混用 Tab 和空格；遇到缩进错误时，从代码块的起点检查。',
                        'Python uses indentation to define blocks. Statements in the same block need consistent indentation, usually four spaces. Conditions and loops end with a colon.\n\n```python\nminutes = [10, 25, 0, 15]\nfor value in minutes:\n    if value > 0:\n        print("Studied", value, "minutes")\n    else:\n        print("Rest today")\n```\n\nA `for` loop reads values one at a time. `range(3)` produces 0, 1 and 2, excluding the endpoint 3.\n\n## Try it\n\nStart with `total = 0` and accumulate the positive minutes. Predict the total before running. Do not mix tabs and spaces. When an indentation error appears, check the start of the block.',
                    ),
                ],
            ),
            (
                "把小工具写出来",
                "Build a small tool",
                [
                    (
                        "定义与复用函数",
                        "Define and reuse functions",
                        18,
                        "`def` 声明函数，参数写在括号中，`return` 返回结果。函数定义本身不执行函数体，调用才会执行。\n\n```python\ndef average(values):\n    if not values:\n        return 0\n    return sum(values) / len(values)\n\nprint(average([10, 20, 30]))\nprint(average([]))\n```\n\n空列表在条件中为假，提前返回避免除以零。`sum` 求和，`len` 得到元素个数。没有显式 `return` 时函数返回 `None`。\n\n## 动手试试\n\n增加一个函数，把分钟转换成小时。分别用 0、60、90 验证结果。让函数只负责一件事，把输出展示留给调用者。",
                        "`def` declares a function. Parameters go in parentheses and `return` supplies the result. Defining a function does not run its body; calling it does.\n\n```python\ndef average(values):\n    if not values:\n        return 0\n    return sum(values) / len(values)\n\nprint(average([10, 20, 30]))\nprint(average([]))\n```\n\nAn empty list is false in a condition. Returning early avoids division by zero. `sum` adds values and `len` counts them. Without an explicit return, a function returns `None`.\n\n## Try it\n\nWrite another function to convert minutes into hours. Test 0, 60 and 90. Give each function a single purpose and leave presentation to its caller.",
                    ),
                    (
                        "整理一份学习记录",
                        "Summarize a learning log",
                        20,
                        '把列表、字典、条件和函数组合起来，就能处理一份简单的学习记录。先检查数据，再过滤，最后汇总。\n\n```python\nrecords = [\n    {"topic": "HTML", "minutes": 20},\n    {"topic": "CSS", "minutes": 0},\n    {"topic": "Python", "minutes": 30},\n]\n\ndef total_minutes(items):\n    valid = [r["minutes"] for r in items if r["minutes"] > 0]\n    return sum(valid)\n\nprint(total_minutes(records))  # 50\n```\n\n列表推导式创建新列表，不修改原记录。复杂规则可以先用普通循环写清楚，再考虑简写。\n\n## 完成一个小作品\n\n添加一个新主题，输出有效记录条数、总分钟数和平均分钟数。也测试空列表。不要只检查正常输入：边界情况同样属于程序的行为。',
                        'Combine lists, dictionaries, conditions and functions to process a small learning log. Check data, filter it and summarize it.\n\n```python\nrecords = [\n    {"topic": "HTML", "minutes": 20},\n    {"topic": "CSS", "minutes": 0},\n    {"topic": "Python", "minutes": 30},\n]\n\ndef total_minutes(items):\n    valid = [r["minutes"] for r in items if r["minutes"] > 0]\n    return sum(valid)\n\nprint(total_minutes(records))  # 50\n```\n\nA list comprehension creates a new list without changing the records. For complex rules, write a clear loop before considering a shorter form.\n\n## Build something small\n\nAdd another topic and report the number of positive records, total minutes and average. Test an empty list too. Boundary cases are part of a program’s behavior, not an afterthought.',
                    ),
                ],
            ),
        ],
    },
]


def seed_demo():
    created = 0
    for index, item in enumerate(COURSES):
        if db.session.scalar(db.select(Course).where(Course.slug == item["slug"])):
            continue
        slug, zh, en = item["category"]
        category = db.session.scalar(db.select(Category).where(Category.slug == slug))
        if category is None:
            category = Category(slug=slug, name_zh=zh, name_en=en, sort_order=index)
            db.session.add(category)
            db.session.flush()
        course = Course(
            slug=item["slug"],
            category_id=category.id,
            title_zh=item["titles"][0],
            title_en=item["titles"][1],
            description_zh=item["description"][0],
            description_en=item["description"][1],
            objectives_zh=item["objectives"][0],
            objectives_en=item["objectives"][1],
            cover_kind=item["cover"],
            status="published",
        )
        db.session.add(course)
        db.session.flush()
        for chapter_index, (title_zh, title_en, lessons) in enumerate(item["chapters"]):
            chapter = Chapter(
                course_id=course.id,
                title_zh=title_zh,
                title_en=title_en,
                sort_order=chapter_index,
            )
            db.session.add(chapter)
            db.session.flush()
            for lesson_index, (zh, en, duration, body_zh, body_en) in enumerate(
                lessons
            ):
                db.session.add(
                    Lesson(
                        chapter_id=chapter.id,
                        title_zh=zh,
                        title_en=en,
                        body_zh=body_zh,
                        body_en=body_en,
                        duration_minutes=duration,
                        sort_order=lesson_index,
                    )
                )
        created += 1
    from .seed_learning import seed_learning

    seed_learning()
    db.session.commit()
    return created
