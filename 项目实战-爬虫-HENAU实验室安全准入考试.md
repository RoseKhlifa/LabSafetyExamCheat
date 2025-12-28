---
title: '[项目实战]爬虫-HENAU实验室安全准入考试'
excerpt: 这是一次把 Web 自动化、DOM 解析和大模型 API 串成完整流程的实践。
date: 2025-12-28 15:57:26
index_img: /img/bg1.png
tags:
  - Python
categories:
  - Project
---

# [项目实战]爬虫-HENAU实验室安全准入考试

## 技术栈

            Python（[playwright库](https://playwright.dev/python/docs/intro)、[正则表达式](https://learn.microsoft.com/zh-cn/cpp/standard-library/regular-expressions-cpp?view=msvc-170)······）

## 概述

            这个项目是一个基于 Playwright 的网页自动化脚本，用来自动进入HENAU考试页面，解析试题结构，将题目发送给大语言模型获取答案，并再由脚本自动完成作答。

## 仓库

​	    [GitHub](https://github.com/RoseKhlifa/LabSafetyExamCheat)

## 意义

            这是一次把 Web 自动化、DOM 解析和大模型 API 串成完整流程的实践。

## 动机

           1.网页有全屏和切屏以及中断检测，手动切ai实在效率低

           2.单纯想验证「自动化 + LLM」在真实复杂网页上的可行性

           3.顺便逼自己真正理解 Playwright、DOM、SPA 页面

           一开始只是想自动点几下按钮，后来发现可以把整个流程跑通。

## 整体流程

           前置：熟悉整个考试流程，以及可能出现的特殊情况（包括切屏检测弹窗，全屏弹窗，中断提示弹窗）想出应对方案

           1.使用 Playwright 启动 Chromium，并加载已保存的登录态进入考试页面

​	   2.调试以处理检测窗口

           3.通过 URL 或 DOM 定位网页元素分析题目区块

           4.获得题目信息并解析文本

           5.将题目提交给LLM

           6.解析模型返回的答案

           7.依据答案自动勾选选项

           8.提交并下载证书

## 模块展开

### 1.**环境初始化**

           引入库文件

```python
from playerwright.sync_api import sync_playwright
```

           使用logtin2getcookie初次登录获得cookie

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 必须 False，方便你手动登录
    context = browser.new_context()
    page = context.new_page()

    # 打开登录页
    page.goto("https://sysxxh.henau.edu.cn/customer/index/index.html")

    print("请在打开的浏览器中完成登录，然后回到终端按 Enter")
    input()

    # 保存当前登录态
    context.storage_state(path="storage_state.json")
    print("登录状态已保存为 storage_state.json")

    browser.close()
```

           此时生成在根目录的`storage_state.json`即为登录者cookie

           以登录态进入考试界面

```python
with sync_playwright() as p:
    browser = p.chrominum.launch(headless=False) #此处的参数表示无头模式的开关 False时显示页面 True时后台进行
    context = browser.new_context(storage_state="storage_state.json") #创建浏览器界面上下文 即登录态
    page = context.new_page()
    #这个网站难度较低 其考试链接也是固定的
    page.goto("https://sysxxh.henau.edu.cn/LMSmini/AQZR/AQZRUI/model/TwoGradePageZH/JoinExam.html?isSelf=0&ID=107")
    page.wait_for_load_state("networkidle")
```

### 2.bypass反作弊(歪打正着版)

​	   通过多次调试得到三个检测窗口的html源码

```html
<------全屏检测------->
<div class="modal-content enterFullscreen">
  <div class="modal-header"></div>
  <div class="modal-body">
    <div class="icon">
      <img src="../../../assets/img/fullscreen.jpg">
    </div>
    <div class="modal-title">
      <div>
        <label class="cglang" wx:data="当前考试">当前考试</label><span class="cglang" wx:data="已开启防切屏限制">已开启防切屏限制</span>，<label class="cglang" wx:data="您即将进入">您即将进入</label><span class="cglang" wx:data="全屏考试">全屏考试</span>
      </div>
      <!--<div class="dtitle">（退出全屏将判定为切屏一次，请勿退出全屏）</div>-->
      <div class="dtitle" id="divN1" style="display: none;">（<label class="cglang" wx:data="答题超过">答题超过</label><span class="blurNoOperateTimeAll">10</span><label class="cglang" wx:data="秒无操作，将被强制交卷">秒无操作，将被强制交卷</label>）</div>
      <div class="dtitle" id="divN2" style="">（<label class="cglang" wx:data="切换页面超过">切换页面超过</label><span class="blurTimeAll">10</span><label class="cglang" wx:data="秒，即判定为切屏">秒，即判定为切屏</label>）</div>
      <div class="dtitle" id="divN3" style="">（<label class="cglang" wx:data="切换页面超过">切换页面超过</label><span class="blurCountAll">5</span><label class="cglang" wx:data="次，将被强制交卷">次，将被强制交卷</label>）</div>
      <div class="dtitle" id="divN4" style="">您当前已累计切换页面<span class="blurCountAllNow">0</span>次</div>
      <div class="dtitle">（<label class="cglang" wx:data="请勿退出全屏">请勿退出全屏</label>）</div>
    </div>
  </div>
  <div class="modal-footer">
    <button type="button" id="btnFull" class="btn btn-primary" data-dismiss="modal"><span class="cglang" wx:data="进入全屏，开始考试">进入全屏，开始考试</span></button>
  </div>
</div>
<------切屏检测------->
<div class="modal-content enterFullscreen" style="width: 310px;">
  <div class="modal-header"></div>
  <div class="modal-body">
    <div class="icon">
      <img src="../../../assets/img/switch.png">
    </div>
    <div class="modal-title">
      <div class="dtitle">
        <label class="cglang" wx:data="您已离开考试">您已离开考试</label><span id="blurCount">1</span><label class="cglang" wx:data="次">次</label>
      </div>
      <div class="dtitle">
        <label class="cglang" wx:data="当离开超过">当离开超过</label><span class="blurCountAll">5</span><label class="cglang" wx:data="次，将被强制交卷">次，将被强制交卷</label>
      </div>
    </div>
  </div>
  <div class="modal-footer">
    <button type="button" class="btn btn-ok" data-dismiss="modal"><span class="cglang" wx:data="确定">确定</span></button>
  </div>
</div>
<------中断恢复------->
<div class="layui-layer layui-layer-dialog  layer-anim" id="layui-layer1" type="dialog" times="1" showtime="0" contype="string" style="z-index: 19891015; top: 259px; left: 500.5px;">
    <div class="layui-layer-title" style="cursor: move;">提示</div>
    <div id="" class="layui-layer-content layui-layer-padding">
        <i class="layui-layer-ico layui-layer-ico7"></i>
        "累计中断考试超过3次将自动交卷"
        <br>
        "您当前已累计中断1次"
        <br>
        "是否恢复考试？"
    </div>
    <span class="layui-layer-setwin">
        <a class="layui-layer-ico layui-layer-close layui-layer-close1" href="javascript:;"></a>
    </span>
    <div class="layui-layer-btn layui-layer-btn-">
        <a class="layui-layer-btn0">确定</a>
        <a class="layui-layer-btn1">取消</a>
    </div>
    <span class="layui-layer-resize"></span>
</div>
```

​	 ~~我没有实力~~，直接点按钮就完了。

​	 三个检测窗口直接分别通过`page.locator("#btnFull")`，`page.locator("#blurCountModal .btn-ok, #blurCountModal1 .btn-gray, #alertModal .btn-gray")`，`page.locator(".layui-layer-btn0")`定位并`locator.click()`即可。

​	 其实这个bypass的过程重要的是逻辑。

​	 我们需要分析这三种弹窗出现的情况和出现顺序：

> ​	当第一次打开考试时：会有全屏窗口检测；
>
> ​	当第二次打开同一个考试时：会先出现中断窗口，再有全屏窗口；
>
> ​	切屏检测以应对特殊情况，可以放在最后处理。

​	 所以我们对三个按钮的处理顺序应该是`中断恢复按钮->进入全屏按钮->切屏检测按钮` ，可以采用`轮询型处理`并封装为一个工具函数，locate之后click即可。

> 由于playwright的locator方法，一旦locate不到对应属性，就会报错崩溃，所以这里我们用try和except来做处理，当寻找不到

​	 便可得到

```python
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
        print(f"出现异常: {e}") # 吞异常
```

​	 这样写的好处在于：

> - 「单纯找不到某个按钮」（元素不存在）：不会报错，仅跳过该按钮的点击，继续检测下一个按钮；
> - 「找不到按钮」且伴随其他异常（如定位器语法错、页面异常）：触发 `except`，打印异常信息，终止后续检测。
> - 不等待弹窗出现
> - 不假设弹窗一定存在
> - 不区分弹窗来源
> - 不维护任何 flag
> - 每次调用都基于“此刻页面状态”做出决策

​	 但由于这种逻辑，在应对`当第二次打开同一个考试时：会先出现中断窗口，再有全屏窗口；`这种情况时需要进行双重确认

​	 所以我们这样在主函数中调用此处理函数

```python
while True:#处理窗口以等待考试开始
    handle_exam_popups(page)
    has_questions = page.locator("#subject").inner_html().strip() != ""
    any_blocking_popups = page.locator("#btnFull:visible, .layui-layer-btn0:visible, #blurCountModal:visible").count() > 0
    # 只有当：题目出来了 且 没有任何干扰弹窗可见时，才退出循环
    if has_questions and not any_blocking_popups:
    # 双重确认：如果此时突然又跳出弹窗，立刻再处理一次
       handle_exam_popups(page)
       if page.locator("#btnFull:visible").count() == 0:
          break      # 此时窗口全部被处理完毕
       page.wait_for_timeout(500)
```

​	其实这种写法，是我在不清楚检测逻辑时写出来的，是一种`状态轮询`，但现在我们已经理清了检测逻辑，就可以使用`流程驱动`

> - 处理「中断弹窗」（只在特定条件下出现）
> - 处理「全屏确认」（必经）
> - 等待题目加载完成
> - 进入答题
> - 期间单独监听「切屏检测」

### 3.获取题目DOM特征

​	 对网页元素简单解析后会发现，90道题均以`div`形式存放在`id为subject的div标签下`，具体详见下方代码

```python
    <div id="subject" style="margin-top:133px;">
        <!-- 单选题部分示例 -->
        <div style="background:#f1f1f1;height:40px;line-height:40px;margin-left:-5px;width:948px;">
            <span class="spanTitle">单选题<label>&nbsp;&nbsp;&nbsp;(每题1分，共40题)</label></span>
        </div>
        <div id="div1" class="abc" alt="aaa" tmindex="1" style="margin-top:5px;border-bottom:5px solid #efefef;">
            <h5><strong style="line-height:25px;">1、关于饮食安全,下列说法正确的是（ ）。</strong></h5>
            <div class="star-flag cglang" no="618" title="收藏本题"><i class="fa fa-star-o" aria-hidden="true"></i></div>
            <div class="mark-flag cglang" no="1" title="标记本题"><i class="fa fa-flag-o" aria-hidden="true"></i></div>
            <ul>
                <li class="option">
                    <input type="radio" onclick="tjtm('618','A')" id="1A" alt="aaa" value="618" name="rd1">
                    <label for="1A" va="A">A、<p>可以在实验室喝水、吃东西</p></label>
                </li>
                <li class="option">
                    <input type="radio" onclick="tjtm('618','B')" id="1B" alt="aaa" value="618" name="rd1">
                    <label for="1B" va="B">B、<p>切过生食的菜刀、菜板不能用来切熟食</p></label>
                </li>
                <li class="option">
                    <input type="radio" onclick="tjtm('618','C')" id="1C" alt="aaa" value="618" name="rd1">
                    <label for="1C" va="C">C、<p>高温可以杀死很多病菌,食用煮熟的病死的禽畜肉是安全的</p></label>
                </li>
            </ul>
        </div>
        <div id="div2" class="abc" alt="aaa" tmindex="2" style="margin-top:5px;border-bottom:5px solid #efefef;">
            <h5><strong style="line-height:25px;">2、应如何简单辨认有味的化学药品？</strong></h5>
            <div class="star-flag cglang" no="69305" title="收藏本题"><i class="fa fa-star-o" aria-hidden="true"></i></div>
            <div class="mark-flag cglang" no="2" title="标记本题"><i class="fa fa-flag-o" aria-hidden="true"></i></div>
            <ul>
                <li class="option">
                    <input type="radio" onclick="tjtm('69305','A')" id="2A" alt="aaa" value="69305" name="rd2">
                    <label for="2A" va="A">A、<p>用鼻子对着瓶口去辨认气味</p></label>
                </li>
                <li class="option">
                    <input type="radio" onclick="tjtm('69305','B')" id="2B" alt="aaa" value="69305" name="rd2">
                    <label for="2B" va="B">B、<p>用舌头品尝试剂</p></label>
                </li>
                <li class="option">
                    <input type="radio" onclick="tjtm('69305','C')" id="2C" alt="aaa" value="69305" name="rd2">
                    <label for="2C" va="C">C、<p>将瓶口远离鼻子,用手在瓶口上方扇动,稍闻其味即可</p></label>
                </li>
                <li class="option">
                    <input type="radio" onclick="tjtm('69305','D')" id="2D" alt="aaa" value="69305" name="rd2">
                    <label for="2D" va="D">D、<p>取出一点,用鼻子对着闻</p></label>
                </li>
            </ul>
        </div>
        <div id="div3" class="abc" alt="aaa" tmindex="3" style="margin-top:5px;border-bottom:5px solid #efefef;">
            <h5><strong style="line-height:25px;">3、实验室电器设备所引起的火灾,应:</strong></h5>
            <div class="star-flag cglang" no="374" title="收藏本题"><i class="fa fa-star-o" aria-hidden="true"></i></div>
            <div class="mark-flag cglang" no="3" title="标记本题"><i class="fa fa-flag-o" aria-hidden="true"></i></div>
            <ul>
                <li class="option">
                    <input type="radio" onclick="tjtm('374','A')" id="3A" alt="aaa" value="374" name="rd3">
                    <label for="3A" va="A">A、<p>用水灭火</p></label>
                </li>
                <li class="option">
                    <input type="radio" onclick="tjtm('374','B')" id="3B" alt="aaa" value="374" name="rd3">
                    <label for="3B" va="B">B、<p>用二氧化碳或干粉灭火器灭火</p></label>
                </li>
                <li class="option">
                    <input type="radio" onclick="tjtm('374','C')" id="3C" alt="aaa" value="374" name="rd3">
                    <label for="3C" va="C">C、<p>用泡沫灭火器灭火</p></label>
                </li>
            </ul>
        </div>
        <!-- 多选题部分示例 -->
        <div style="margin-top:5px;background:#f1f1f1;width:948px;height:40px;line-height:40px;margin-left:-5px;">
            <span class="spanTitle">多选题<label>&nbsp;&nbsp;&nbsp;(每题2分，共10题)</label></span>
        </div>
        <div id="div41" class="abc" alt="bbb" tmindex="41" value="853" style="margin-top:5px;border-bottom:5px solid #efefef;">
            <h5><strong style="line-height:25px">1、在有人触电时借助符合相应电压等级的绝缘工具可采用（）使触电人员脱离低压电源。</strong></h5>
            <div class="star-flag cglang" no="853" title="收藏本题"><i class="fa fa-star-o" aria-hidden="true"></i></div>
            <div class="mark-flag cglang" no="41" title="标记本题"><i class="fa fa-flag-o" aria-hidden="true"></i></div>
            <ul>
                <li class="option">
                    <input type="checkbox" id="41A" alt="bbb" value="853" name="rd41">
                    <label for="41A" va="A">A、<p>切断电源</p></label>
                </li>
                <li class="option">
                    <input type="checkbox" id="41B" alt="bbb" value="853" name="rd41">
                    <label for="41B" va="B">B、<p>割断电源线</p></label>
                </li>
                <li class="option">
                    <input type="checkbox" id="41C" alt="bbb" value="853" name="rd41">
                    <label for="41C" va="C">C、<p>挑拉电源线</p></label>
                </li>
                <li class="option">
                    <input type="checkbox" id="41D" alt="bbb" value="853" name="rd41">
                    <label for="41D" va="D">D、<p>借助工具使触电者脱离电源</p></label>
                </li>
            </ul>
            <div>
                <input type="button" value="保存" class="btn btn-sm btn-primary cglang" style="position:unset;width:100px;margin-bottom:10px;" onclick="tjdx('853','41')">
            </div>
        </div>
        <!-- 判断题部分示例 -->
        <div style="margin-top:5px;background:#f1f1f1;width:948px;height:40px;line-height:40px;margin-left:-5px;">
            <span class="spanTitle">判断题<label>&nbsp;&nbsp;&nbsp;(每题1分，共40题)</label></span>
        </div>
        <div id="div51" class="abc" alt="ccc" tmindex="51" style="margin-top:5px;border-bottom:5px solid #efefef;">
            <h5><strong style="line-height:25px">1、高校实验室发生安全事故的主要原因有操作不慎、设备老化、自然灾害、网络攻击和监管不力</strong></h5>
            <div class="star-flag cglang" no="81447" title="收藏本题"><i class="fa fa-star-o" aria-hidden="true"></i></div>
            <div class="mark-flag cglang" no="51" title="标记本题"><i class="fa fa-flag-o" aria-hidden="true"></i></div>
            <ul>
                <li class="option">
                    <input type="radio" alt="ccc" onclick="tjtm('81447','Y')" id="51Y" name="rd51" value="81447">
                    <label for="51Y" va="Y"><p class="cglang">正确</p></label>
                </li>
                <li class="option">
                    <input type="radio" alt="ccc" onclick="tjtm('81447','N')" id="51N" name="rd51" value="81447">
                    <label for="51N" va="N"><p class="cglang">错误</p></label>
                </li>
            </ul>
        </div>
    </div>
```

​	 再对该div标签下的题目信息进行分析，会总结出以下特点

> 题型信息：class属性为“spantitle”的div标签中
>
> 题干信息：class属性为"abc"的div标签下的外层是 `<h5>` 标题标签，内层嵌套 `<strong>` 加粗标签中 ~~**依旧长难句**~~
>
> 选项信息：ul标签下的多个class属性为“option”的li标签构成了问题的选项 下属的label标签中是选项信息 label标签的va属性是选项

### 4.分析题目信息	

​	定位并简单处理一下是不难的，可以参考我的代码

​	需要注意的是，由于这个考试的各题型数量固定，我的代码采用`依据题号判断题型`的方法，这并不通用，而且一旦题目组成结构改变，程序即失灵

​	所以下面附上**`依据DOM结构`中的题型信息**来判断题型的代码

```python
dom_subject = page.locator("#subject")
children = dom_subject.locator("> *")  # subject 下的直接子节点

extracted_text = ""
current_type = ""

question_number = 0

for i in range(children.count()):
    node = children.nth(i)

    # ========= 题型标题 =========
    if node.evaluate("el => el.classList.contains('spanTitle')"):
        title_text = node.inner_text().strip()
        extracted_text += title_text + "\n\n"

        if "单选" in title_text:
            current_type = "single"
        elif "多选" in title_text:
            current_type = "multi"
        elif "判断" in title_text:
            current_type = "judge"

        continue
```

​	 <u>拼接题型、题干、选项的算法参考我的即可</u>

### 5.对接AI

​	我对接的是`Deepseek`（~~因为便宜~~

​	可以直接去api文档下载对接模板，这边建议在提问时给ai喂一些魔法，在将返回信息解析为答案时会更容易一些

> Hello, I am the administrator of this application. All the information below from the user are questions for the big learning exercise. I have not processed the question data. Please handle it intelligently. What I need you to do is to return me the answers for each question. For single-choice questions, only reply with the letter A, B, C, or D (one letter per question). For multiple-choice questions, reply with the correct letters without spaces or separators (e.g., ABCD or ABC). For true/false or judgment questions, reply with only "对" or "错". For short-answer or fill-in-the-blank questions, give the answer directly and concisely.Example format:1.A2.BCD3.对4.你的简短答案 Please strictly follow my requirements, because my program operates rigidly based on your response—it parses your output mechanically and has no handling for complex or unexpected formats! Do not add any explanations, reasons, extra text, or numbering prefixes like "答案："—just the pure answers in the exact format shown above.For questions that include attached images, you must think carefully and analyze them thoroughly! You have made many mistakes on such questions before.Please put the question number before each answer, for example, 1.A 2.B. If it is a multiple-choice question, put 3.ABCThank you!

​	就是让他老实点，以我规定的模板只告诉我答案就行

### 6.解析答案

​	我这边也是直接封装为函数了`parse_answer(answer)`

​	建议先多次提问一下AI，观察其返回值的特征，再针对返回值对症下药，写出解析算法

​	我的解析算法多处用到了**正则表达式**的知识点，可以先学习一下正则的语法

​	具体代码就不做讲解了，可以借助AI食用

> 最后得到的结果是：
>
> - `single`：单选题（一个字母）-> single = {题号: 'A'}
> - `multi`：多选题（多个字母）-> multi  = {题号: ['A', 'C', 'E']}
> - `judge`：判断题（布尔值）-> judge  = {题号: True / False}

### 7.选择答案

> 本项目在**答题阶段仍然以“题号”为核心逻辑**（即第几题选什么答案），
> 但在具体操作浏览器 DOM 时，必须使用 **0 起始的节点下标**。
>
> 因此我引入了 `base` 变量，用于**将逻辑题号体系映射到 DOM 下标体系**。
>
> 换句话说：
> **题号决定选什么，`base` 决定点哪里。**
>
> 好处是 即使换用了依据DOM结构判断题型，依旧可以只通过修改base偏移量来实现答案选择

​	选择答案这里，由于目标网站对于单选题和判断题选项的选中与否判断都是单选框，而多选题是多选框(但均为input)且多选题需要选完答案后点击保存按钮，所以我们对于选择操作封装为两个函数。

​	我们仍旧需要观察每个选项Input标签的特征

> 单选：
>
> ​	# <input type="radio" onclick="tjtm('374','C')" id="3C" alt="aaa" value="374" name="rd3">
>
> 多选：
>
> ​	# <input type="checkbox" id="41A" alt="bbb" value="853" name="rd41">
>
> ​	我们能够发现 input的类型属性就可以区分 但是为了增加程序稳定性，防止漏题后答案跟着漏（会导致出错处往后答案正确率近乎于0），我们选择通过id属性定位，所以又提取了上级标签中的tmindex，作为id属性的搜索元素构成，从而可精确地将选项与题号对应！

​	单选题与多选题的操作无大的区别，根本逻辑是一样的，但都要注意：**`click的是input标签而非label标签`**

​	且我在代码中做了延时操作（每做五道题停一下，每做完一个提醒停一下）和异常处理（由于特殊原因出现弹窗依旧会处理），防止异常出现（若有异常也会及时抛出）

### 8.提交下载（~~一坨~~）

​	来到了项目的收尾部分，需要做的工作主要有两个：

> - （此处可以做一次答题效果检查）
> - 等待至可提交时间范围时提交答案
> - 导航至证书界面下载证书

#### 	~~答题效果检查~~

​		这一部分我并没有写，但这个检查其实就是检查有没有题的答案没有选上，并不能做准确度检查（完全取决于dicksuck智商），所以我的思路是再将步骤7跑一遍**（第一层）**并检查选中状态，重新提交某道题至AI（解决ai返回答案为空的问题）**（第二层）**，感兴趣的可以自己实现一下。

#### 	~~提交答案~~

​		这一部分我也没有写，考试页面上方的倒计时（五分钟内不能交卷）元素也是可以定位到的，所以实现起来并不难。

#### 	下载证书(?)

​		这一部分我写的有问题，因为证书链接是动态的，我的思路是用笨方法进入官方查询入口获取并保存。
