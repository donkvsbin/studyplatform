"""One-time additions to the original demo content; existing edits stay intact."""

from ..extensions import db
from ..models import Course, Quiz, QuizQuestion, SeedRevision

# Each item: bilingual prompt, bilingual options, correct stable ID, bilingual explanation.
QUESTIONS = {
    "web-foundations": [
        (
            "哪个 HTML 元素保存网页的可见内容？",
            "Which HTML element holds visible page content?",
            [("a", "body", "body"), ("b", "head", "head"), ("c", "meta", "meta")],
            "a",
            "body 包含显示给读者的内容；head 保存标题和元信息。",
            "The body holds visible content. The head holds the title and metadata.",
        ),
        (
            "CSS 的 padding 控制哪一部分间距？",
            "Which spacing does CSS padding control?",
            [
                ("a", "元素之间的外部距离", "Space outside the element"),
                ("b", "内容与边框之间的距离", "Space between content and border"),
                ("c", "字符之间的距离", "Space between characters"),
            ],
            "b",
            "padding 是内边距，margin 是外边距。",
            "Padding creates space inside a box; margin creates space outside it.",
        ),
        (
            "如何让父容器使用 Flexbox 布局？",
            "How do you enable Flexbox on a parent?",
            [
                ("a", "color: flex", "color: flex"),
                ("b", "position: flex", "position: flex"),
                ("c", "display: flex", "display: flex"),
            ],
            "c",
            "给父容器设置 display: flex，其子元素就会参与弹性布局。",
            "Set display: flex on the parent to lay out its children using Flexbox.",
        ),
    ],
    "javascript-basics": [
        (
            "需要重新赋值的变量应该用哪个关键字声明？",
            "Which keyword declares a variable you will reassign?",
            [("a", "let", "let"), ("b", "const", "const"), ("c", "return", "return")],
            "a",
            "let 允许重新赋值；const 创建不可重新赋值的绑定。",
            "let allows reassignment; const creates a binding that cannot be reassigned.",
        ),
        (
            "for...of 循环逐个读取数组的什么？",
            "What does for...of read from an array?",
            [
                ("a", "属性名称", "Property names"),
                ("b", "元素的值", "Element values"),
                ("c", "只有长度", "Only its length"),
            ],
            "b",
            "for...of 遍历可迭代对象中的值。",
            "for...of iterates through the values of an iterable.",
        ),
        (
            "安全地更新元素中的普通文字，应使用什么？",
            "What should update plain text in an element safely?",
            [
                ("a", "eval", "eval"),
                ("b", "innerHTML", "innerHTML"),
                ("c", "textContent", "textContent"),
            ],
            "c",
            "textContent 将内容视为文字，不会解析为 HTML。",
            "textContent treats content as text rather than parsing it as HTML.",
        ),
    ],
    "python-basics": [
        (
            "Python 列表第一个元素的下标是多少？",
            "What is the index of the first Python list item?",
            [("a", "0", "0"), ("b", "1", "1"), ("c", "-0.5", "-0.5")],
            "a",
            "列表下标从 0 开始。",
            "List indexing starts at zero.",
        ),
        (
            "Python 通过什么表示代码块？",
            "How does Python define a code block?",
            [
                ("a", "花括号", "Curly braces"),
                ("b", "一致的缩进", "Consistent indentation"),
                ("c", "引号", "Quotation marks"),
            ],
            "b",
            "Python 使用缩进划分代码块，通常使用四个空格。",
            "Python uses indentation for blocks, conventionally four spaces.",
        ),
        (
            "计算平均值前检查空列表，主要是为了避免什么？",
            "Why check for an empty list before computing its average?",
            [
                ("a", "列表自动排序", "Automatic sorting"),
                ("b", "字符串变长", "Longer strings"),
                ("c", "除以零", "Division by zero"),
            ],
            "c",
            "空列表的长度为零，应提前返回或明确处理。",
            "An empty list has length zero, so handle it before division.",
        ),
    ],
}


def seed_learning():
    if db.session.get(SeedRevision, "v040-learning-content"):
        return
    for slug, items in QUESTIONS.items():
        course = db.session.scalar(db.select(Course).where(Course.slug == slug))
        if course is None:
            continue
        quiz = db.session.scalar(db.select(Quiz).where(Quiz.course_id == course.id))
        if quiz is None:
            quiz = Quiz(
                course_id=course.id,
                title_zh=course.title_zh + "结课测验",
                title_en=course.title_en + " quiz",
            )
            db.session.add(quiz)
            db.session.flush()
            for index, (
                zh,
                en,
                options,
                correct,
                explanation_zh,
                explanation_en,
            ) in enumerate(items):
                db.session.add(
                    QuizQuestion(
                        quiz_id=quiz.id,
                        prompt_zh=zh,
                        prompt_en=en,
                        options=[
                            {"id": key, "text_zh": text_zh, "text_en": text_en}
                            for key, text_zh, text_en in options
                        ],
                        correct_option_id=correct,
                        explanation_zh=explanation_zh,
                        explanation_en=explanation_en,
                        sort_order=index,
                    )
                )
        if slug == "web-foundations":
            first = next(
                (
                    lesson
                    for chapter in course.chapters
                    for lesson in chapter.lessons
                    if lesson.title_en == "How a web page is built"
                ),
                None,
            )
            if first and first.video_url is None:
                first.video_url = "/demo/web-welcome.mp4"
    db.session.add(SeedRevision(name="v040-learning-content"))
