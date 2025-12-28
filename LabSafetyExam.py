from playwright.sync_api import sync_playwright
from string_utils import StringUtils as su
import time
import re
from log import log
from deepseek import GetAnswer #推理答案模块
def handle_exam_popups(page):
    """
    在一个周期内处理所有可见弹窗
    """
    try:
        # 中断提示
        layer_btn = page.locator(".layui-layer-btn0").first
        if layer_btn.is_visible():
            print("发现中断提示，点击恢复考试...")
            layer_btn.click()
            page.wait_for_timeout(500) 

        # 进入全屏
        btn_full = page.locator("#btnFull").first
        if btn_full.is_visible():
            print("发现全屏确认，点击进入...")
            btn_full.click()
            page.wait_for_timeout(500)

        # -防切屏警告
        cheat_alert = page.locator("#blurCountModal .btn-ok, #blurCountModal1 .btn-gray, #alertModal .btn-gray").first
        if cheat_alert.is_visible():
            print("发现作弊/切屏警告，点击确定...")
            cheat_alert.click()
            page.wait_for_timeout(500)

    except Exception as e:
        print(f"弹窗处理检测中: {e}")

def parse_answers(answer_text: str):
    single = {}
    multi = {}
    judge = {}

    lines = [line.strip() for line in answer_text.splitlines() if line.strip()]

    current_q_num = 0

    for line in lines:
        # 提取题号（如 "41." "41、" "41：" 等）
        num_match = re.match(r'^(\d+)[.、:：\s]+(.*)', line) #用正则匹配为题号+答案  group(0)是题号+答案，group(1)是题号，group(2)是答案
        if num_match:
            current_q_num = int(num_match.group(1))
            content = num_match.group(2).strip()
        else:
            # 没有题号的行，尝试接在上一个题号
            content = line
            if current_q_num == 0:
                continue

        # 判断题：包含 正确/错误/对/错
        if re.search(r'(正确|错误|对|错)', content):
            judge[current_q_num] = '正确' in content or '对' in content #正确和对 直接定义为 True
            continue

        # 多选：字母 ≥2 个，且不含“正确”等判断词
        letters_match = re.findall(r'[A-Z]', content.upper())
        if len(letters_match) >= 2:
            multi[current_q_num] = letters_match
            continue

        # 单选：只有一个字母
        single_match = re.match(r'^[A-D]$', content.upper())
        if single_match:
            single[current_q_num] = single_match.group(0)
            continue

        # 备选：内容直接是如 "B" "BD" "正确"
        if re.match(r'^[A-D]+$', content.upper()):
            letters = list(content.upper())
            if len(letters) == 1:
                single[current_q_num] = letters[0]
            elif len(letters) >= 2:
                multi[current_q_num] = letters
    return single, multi, judge
def select_option(q_div, option_letter):
    """
    单选、判断题专用：直接点击 input
    """
    tmindex = q_div.get_attribute("tmindex") #题号
    if not tmindex:
        raise Exception("无法获取 tmindex")

    input_id = f"{tmindex}{option_letter}"  # 如 "1A", "51Y"

    # 使用属性选择器，完全避免 #id 数字开头问题
    input_elem = q_div.locator(f"input[id='{input_id}']")

    if input_elem.count() == 0:
        raise Exception(f"未找到选项 input[id='{input_id}'] (tmindex={tmindex}, letter={option_letter})")

    input_elem.first.scroll_into_view_if_needed()#滚动到可见
    input_elem.first.click(force=True)
    page.wait_for_timeout(200)


def answer_multi_question(page, question_index, answer_letters):
    """
    多选题专用：点击多个选项 + 保存
    """
    if not answer_letters or len(answer_letters) < 2:
        print(f"警告: 多选题 {question_index + 1} 答案无效或少于2个: {answer_letters}")
        # 不 return，继续尝试点击已有的（避免空答案直接跳过）
        # return

    q_div = page.locator("div.abc").nth(question_index)
    tmindex = q_div.get_attribute("tmindex")
    if not tmindex:
        raise Exception("多选题无法获取 tmindex")

    # 点击每个选项
    clicked_count = 0
    for letter in answer_letters:
        input_id = f"{tmindex}{letter}"
        input_elem = q_div.locator(f"input[id='{input_id}']")
        if input_elem.count() > 0:
            input_elem.first.scroll_into_view_if_needed()
            input_elem.first.click(force=True)
            clicked_count += 1
            page.wait_for_timeout(200)
        else:
            print(f"多选题警告: 未找到选项 {input_id}")

    if clicked_count < 2:
        print(f"严重警告: 多选题 {question_index + 1} 只选中了 {clicked_count} 个选项，可能触发提示")

    # 点击保存按钮
    save_btn = q_div.locator("input[value='保存']").first
    if save_btn.count() > 0:
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)
        page.wait_for_timeout(600)
    else:
        print(f"第 {question_index + 1} 题未找到保存按钮，已跳过保存")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    t0 = time.time()
    art_text = r"""
         _____                _  ___     _ _  __      
        |  __ \              | |/ / |   | (_)/ _|     
        | |__) |___  ___  ___| ' /| |__ | |_| |_ __ _ 
        |  _  // _ \/ __|/ _ \  < | '_ \| | |  _/ _` |
        | | \ \ (_) \__ \  __/ . \| | | | | | || (_| |
        |_|  \_\___/|___/\___|_|\_\_| |_|_|_|_| \__,_|
    """
    print(art_text)
    log("程序启动")
    context = browser.new_context(storage_state="storage_state.json")
    page = context.new_page()
    page.goto("https://sysxxh.henau.edu.cn/LMSmini/AQZR/AQZRUI/model/TwoGradePageZH/JoinExam.html?isSelf=0&ID=107")
    page.wait_for_load_state("networkidle")
    t1 = time.time()
    log("页面加载完成", t1 - t0)
    while True:#处理窗口以等待考试开始
        handle_exam_popups(page)
        has_questions = page.locator("#subject").inner_html().strip() != ""
        any_blocking_popups = page.locator("#btnFull:visible, .layui-layer-btn0:visible, #blurCountModal:visible").count() > 0
        # 只有当：题目出来了 且 没有任何干扰弹窗可见时，才退出循环
        if has_questions and not any_blocking_popups:
            # 双重确认：如果此时突然又跳出弹窗，立刻再处理一次
            handle_exam_popups(page)
            if page.locator("#btnFull:visible").count() == 0:
                t2 = time.time()
                log("所有干扰已排除，正式进入考试。",t2-t1)
                break
                
        page.wait_for_timeout(500)

    dom_subject = page.locator("div[id='subject']")
        # ==================== 开始提取题目（修复版）===================
    # 1. 提取大标题
    extracted_text = ""

    question_divs = page.locator("div.abc")
    current_type = " "  # 当前题型：single / multi / judge

    for index in range(question_divs.count()):
        q_div = question_divs.nth(index)
        question_number = index + 1  # 真实题号

        # ============ 根据题号强制切换题型标题 ============
        if question_number == 1 and current_type != "single":
            extracted_text += "\n单选题   (每题1分，共40题)\n\n"
            current_type = "single"
        elif question_number == 41 and current_type != "multi":
            extracted_text += "\n多选题   (每题2分，共10题)\n\n"
            current_type = "multi"
        elif question_number == 51 and current_type != "judge":
            extracted_text += "\n判断题   (每题1分，共40题)\n\n"
            current_type = "judge"
        # 提取题目文本
        strong = q_div.locator("strong").first
        if strong.is_visible():
            q_text = strong.inner_text().strip()
            q_text = re.sub(r'^(\d+)[、,\s]+', r'\1. ', q_text)
        else:
            q_text = f"{question_number}. [题目文本缺失]"

        # 提取选项
        options = []
        option_lis = q_div.locator("li.option")
        for j in range(option_lis.count()):
            li = option_lis.nth(j)
            label = li.locator("label").first
            if label.is_visible():
                va = label.get_attribute("va")
                option_text = label.inner_text().strip()
                option_text = re.sub(r'^[A-Z][、.\s]+', '', option_text).strip()
                options.append(f"{va}: {option_text}")

        # 添加到结果
        extracted_text += q_text + "\n"
        for opt in options:
            extracted_text += opt + "\n"
        extracted_text += "\n"  # 空行分隔

    output_file = "实验室安全考试题目.txt"
    with open(output_file, "w", encoding="utf-8") as f:
         f.write(extracted_text)
    t3 = time.time()
    log(f"题目提取完成，共提取 {question_divs.count()} 道题",t3-t2)

    
    #print(extracted_text[:500] + "...")
    answer = GetAnswer(extracted_text)
    output_file = "GetAnswer.txt"
    with open(output_file, "w", encoding="utf-8") as f:
         f.write(answer)
    t4 = time.time()
    log(f"AI推理完成",t4-t3)
    single_answers, multi_answers, judge_answers = parse_answers(answer)
    t5 = time.time()
    log(f"答案解析完成,并将开始答题...")
    # 开始答题
    for i in range(40):
        if i % 5 == 0:
            page.wait_for_timeout(700)
        q_div = question_divs.nth(i)
        answer_letter = single_answers.get(i + 1)
        if answer_letter:
            select_option(q_div, answer_letter)
    handle_exam_popups(page)
    page.wait_for_timeout(500)
    base = 40  # 多选题从第 41 道开始
    for i in range(10):
        answer_multi_question(page,base + i,multi_answers.get(i + 1, []))
    handle_exam_popups(page)
    page.wait_for_timeout(500)
    base = 50
    for i in range(40):
        if i % 5 == 0:
            page.wait_for_timeout(700)
        q_div = question_divs.nth(base + i)
        is_true = judge_answers.get(i + 1)
        select_option(q_div, 'Y' if is_true else 'N')
    handle_exam_popups(page)
    page.wait_for_timeout(500)
    t6 = time.time()
    log(f"答题完成",t6-t0)
    print("[!!!!!!!]答题结束，请自行提交。")
    print("[!!!!!!!]请注意：请在提交前，先检查是否有未保存的答案。")
    print("[!!!!!!!]请注意：作业要求五分钟内不得交卷，请勿退出此程序，安静等待五分钟后自行提交！")
    input("提交后，请在此处按任意键，将导航至证书页面...")
    page_zhengshu = context.new_page()
    page_zhengshu.bring_to_front() 
    page_zhengshu.goto("https://sysxxh.henau.edu.cn/LMSmini/AQZR/Examination/Certificate/zsmb1.html?KSID=70102")
    try:
        page_zhengshu.wait_for_load_state("networkidle", timeout=10000)
        print("证书页面加载成功！")
    except:
        print("证书页面加载超时，可能需要手动刷新或检查登录状态")
    page_zhengshu.screenshot(path="证书截图.png", full_page=True)
    print("已保存证书截图到当前目录：证书截图.png")
    print("证书页面已打开！如果没自动跳转，请手动切换到新标签页查看。")
    print("程序已完成全部任务，浏览器将保持打开状态，你可以手动关闭。")

    input("查看完毕后，按任意键退出程序...")
    