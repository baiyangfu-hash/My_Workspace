"""
情景对话数据模块
预置多场景英语对话内容
"""

DIALOGS = {
    "restaurant": {
        "title": "在餐厅点餐",
        "title_en": "At the Restaurant",
        "category": "日常生活",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "Waiter",
                "text": "Good evening! Welcome to our restaurant. Do you have a reservation?",
                "translation": "晚上好！欢迎光临。您有预订吗？",
                "highlight_words": ["reservation"]
            },
            {
                "speaker": "You",
                "text": "No, I don't. Do you have a table for two?",
                "translation": "没有。你们有两人桌吗？",
                "highlight_words": ["table"]
            },
            {
                "speaker": "Waiter",
                "text": "Yes, we do. Right this way, please. Here is the menu.",
                "translation": "有的。请这边走。这是菜单。",
                "highlight_words": ["menu"]
            },
            {
                "speaker": "Waiter",
                "text": "Are you ready to order?",
                "translation": "您准备好点餐了吗？",
                "highlight_words": ["order"]
            },
            {
                "speaker": "You",
                "text": "Yes, I'd like the steak, please. Medium rare.",
                "translation": "是的，我要牛排，五分熟。",
                "highlight_words": ["steak", "rare"]
            },
            {
                "speaker": "Waiter",
                "text": "Would you like any sides with that? We have mashed potatoes, salad, or fries.",
                "translation": "您需要配菜吗？我们有土豆泥、沙拉或薯条。",
                "highlight_words": ["sides", "mashed", "potatoes", "salad", "fries"]
            },
            {
                "speaker": "You",
                "text": "I'll have the mashed potatoes, please. And a glass of water.",
                "translation": "我要土豆泥。还有一杯水。",
                "highlight_words": ["mashed", "potatoes", "glass"]
            },
            {
                "speaker": "Waiter",
                "text": "Anything else?",
                "translation": "还要别的吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "That's all, thank you.",
                "translation": "就这些，谢谢。",
                "highlight_words": []
            },
            {
                "speaker": "Waiter",
                "text": "Your order will be ready in about 15 minutes. Enjoy your meal!",
                "translation": "您的餐点大约15分钟后准备好。祝您用餐愉快！",
                "highlight_words": ["order", "enjoy", "meal"]
            }
        ]
    },
    "airport": {
        "title": "在机场",
        "title_en": "At the Airport",
        "category": "旅行",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Staff",
                "text": "Good morning. May I see your passport and ticket, please?",
                "translation": "早上好。请出示您的护照和机票。",
                "highlight_words": ["passport", "ticket"]
            },
            {
                "speaker": "You",
                "text": "Here you are. I'd like a window seat, please.",
                "translation": "给您。我想要一个靠窗的座位。",
                "highlight_words": ["window", "seat"]
            },
            {
                "speaker": "Staff",
                "text": "Let me check... Yes, we have a window seat available. Do you have any checked baggage?",
                "translation": "让我查一下……是的，我们有靠窗座位。您有托运行李吗？",
                "highlight_words": ["available", "checked", "baggage"]
            },
            {
                "speaker": "You",
                "text": "Yes, I have two suitcases to check in.",
                "translation": "是的，我有两个行李箱要托运。",
                "highlight_words": ["suitcases", "check"]
            },
            {
                "speaker": "Staff",
                "text": "Please place them on the scale. Your flight departs from Gate 12 at 10:30 AM.",
                "translation": "请把它们放在秤上。您的航班上午10:30从12号登机口起飞。",
                "highlight_words": ["scale", "flight", "departs", "gate"]
            },
            {
                "speaker": "You",
                "text": "Thank you. Where is the security check?",
                "translation": "谢谢。安检在哪里？",
                "highlight_words": ["security"]
            },
            {
                "speaker": "Staff",
                "text": "Go straight ahead and turn left. You can't miss it.",
                "translation": "直走然后左转。你不会错过的。",
                "highlight_words": ["straight", "ahead"]
            },
            {
                "speaker": "You",
                "text": "Thank you very much.",
                "translation": "非常感谢。",
                "highlight_words": []
            }
        ]
    },
    "hotel": {
        "title": "在酒店入住",
        "title_en": "Hotel Check-in",
        "category": "旅行",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "Receptionist",
                "text": "Welcome to Grand Hotel. How may I help you?",
                "translation": "欢迎来到大酒店。有什么可以帮您？",
                "highlight_words": ["receptionist"]
            },
            {
                "speaker": "You",
                "text": "I have a reservation under the name Li Ming.",
                "translation": "我预订了一个房间，名字是李明。",
                "highlight_words": ["reservation"]
            },
            {
                "speaker": "Receptionist",
                "text": "Let me check... Yes, we have a double room reserved for you for three nights.",
                "translation": "让我查一下……是的，我们为您预留了一间双人房，住三晚。",
                "highlight_words": ["double", "reserved", "nights"]
            },
            {
                "speaker": "You",
                "text": "That's correct. What time is breakfast?",
                "translation": "没错。早餐几点开始？",
                "highlight_words": ["breakfast"]
            },
            {
                "speaker": "Receptionist",
                "text": "Breakfast is served from 7:00 AM to 10:00 AM in the restaurant on the first floor.",
                "translation": "早餐供应时间是早上7点到10点，在一楼的餐厅。",
                "highlight_words": ["served", "floor"]
            },
            {
                "speaker": "You",
                "text": "Great. Is Wi-Fi included?",
                "translation": "好的。包含Wi-Fi吗？",
                "highlight_words": ["included"]
            },
            {
                "speaker": "Receptionist",
                "text": "Yes, the password is in your room. Here is your key card. Room 305, on the third floor.",
                "translation": "是的，密码在您的房间里。这是您的房卡。305房间，在三楼。",
                "highlight_words": ["password", "key", "card"]
            },
            {
                "speaker": "You",
                "text": "Thank you. Is there an elevator?",
                "translation": "谢谢。有电梯吗？",
                "highlight_words": ["elevator"]
            },
            {
                "speaker": "Receptionist",
                "text": "Yes, it's right around the corner. Enjoy your stay!",
                "translation": "有的，就在拐角处。祝您入住愉快！",
                "highlight_words": ["corner", "stay"]
            }
        ]
    },
    "shopping": {
        "title": "在商场购物",
        "title_en": "Shopping at the Mall",
        "category": "日常生活",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "Shop Assistant",
                "text": "Hi there! Can I help you find something?",
                "translation": "您好！需要帮您找什么吗？",
                "highlight_words": ["assistant"]
            },
            {
                "speaker": "You",
                "text": "Yes, I'm looking for a T-shirt. Do you have this in a medium size?",
                "translation": "是的，我想找一件T恤。这件有中号吗？",
                "highlight_words": ["medium", "size"]
            },
            {
                "speaker": "Shop Assistant",
                "text": "Let me check... Yes, we do. Would you like to try it on?",
                "translation": "让我查一下……有的。您想试穿一下吗？",
                "highlight_words": ["try"]
            },
            {
                "speaker": "You",
                "text": "Yes, please. Where is the fitting room?",
                "translation": "好的。试衣间在哪里？",
                "highlight_words": ["fitting", "room"]
            },
            {
                "speaker": "Shop Assistant",
                "text": "It's right over there. Let me know if you need a different size.",
                "translation": "就在那边。如果您需要其他尺寸请告诉我。",
                "highlight_words": ["different"]
            },
            {
                "speaker": "You",
                "text": "This fits well. How much is it?",
                "translation": "这件很合身。多少钱？",
                "highlight_words": ["fits"]
            },
            {
                "speaker": "Shop Assistant",
                "text": "It's $29.99. We have a 20% discount today.",
                "translation": "29.99美元。今天有八折优惠。",
                "highlight_words": ["discount"]
            },
            {
                "speaker": "You",
                "text": "I'll take it. Can I pay by credit card?",
                "translation": "我买了。可以用信用卡支付吗？",
                "highlight_words": ["credit", "card"]
            },
            {
                "speaker": "Shop Assistant",
                "text": "Of course. Please insert your card here. Would you like a receipt?",
                "translation": "当然可以。请在这里刷卡。您需要收据吗？",
                "highlight_words": ["insert", "receipt"]
            },
            {
                "speaker": "You",
                "text": "Yes, please. Thank you!",
                "translation": "是的，谢谢！",
                "highlight_words": []
            }
        ]
    },
    "job_interview": {
        "title": "工作面试",
        "title_en": "Job Interview",
        "category": "职场",
        "difficulty": "高级",
        "lines": [
            {
                "speaker": "Interviewer",
                "text": "Good morning. Please have a seat. I'm John Smith, the HR manager.",
                "translation": "早上好。请坐。我是约翰·史密斯，人力资源经理。",
                "highlight_words": ["interviewer", "manager"]
            },
            {
                "speaker": "You",
                "text": "Nice to meet you, Mr. Smith. Thank you for having me.",
                "translation": "很高兴见到您，史密斯先生。感谢您给我这次机会。",
                "highlight_words": []
            },
            {
                "speaker": "Interviewer",
                "text": "So, tell me about yourself and your background.",
                "translation": "那么，请介绍一下您自己和您的背景。",
                "highlight_words": ["background"]
            },
            {
                "speaker": "You",
                "text": "I graduated from Beijing University with a degree in Computer Science. I have three years of experience in software development.",
                "translation": "我毕业于北京大学，计算机科学专业。我有三年的软件开发经验。",
                "highlight_words": ["graduated", "degree", "experience", "development"]
            },
            {
                "speaker": "Interviewer",
                "text": "What are your strengths and weaknesses?",
                "translation": "您的优点和缺点是什么？",
                "highlight_words": ["strengths", "weaknesses"]
            },
            {
                "speaker": "You",
                "text": "My strength is problem-solving. I'm good at analyzing complex issues. As for my weakness, I sometimes focus too much on details.",
                "translation": "我的优点是解决问题。我擅长分析复杂问题。至于缺点，我有时会过于关注细节。",
                "highlight_words": ["problem-solving", "analyzing", "complex", "issues", "focus", "details"]
            },
            {
                "speaker": "Interviewer",
                "text": "Why do you want to work for our company?",
                "translation": "您为什么想加入我们公司？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "I'm impressed by your company's innovative products and culture. I believe my skills align well with your team's needs.",
                "translation": "贵公司创新的产品和文化给我留下了深刻印象。我相信我的技能与团队的需求很匹配。",
                "highlight_words": ["impressed", "innovative", "products", "culture", "skills", "align"]
            },
            {
                "speaker": "Interviewer",
                "text": "Do you have any questions for me?",
                "translation": "您有什么问题要问我吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Yes, could you tell me about the team I would be working with?",
                "translation": "是的，您能告诉我我将与哪个团队合作吗？",
                "highlight_words": []
            },
            {
                "speaker": "Interviewer",
                "text": "Of course. You'll be joining our development team of ten people. We'll be in touch within a week. Thank you for coming.",
                "translation": "当然。您将加入我们十人的开发团队。我们会在一周内联系您。感谢您的到来。",
                "highlight_words": ["development", "touch"]
            }
        ]
    }
}

def get_all_dialogs():
    """获取所有对话列表"""
    result = []
    for key, dialog in DIALOGS.items():
        result.append({
            "id": key,
            "title": dialog["title"],
            "title_en": dialog["title_en"],
            "category": dialog["category"],
            "difficulty": dialog["difficulty"],
            "line_count": len(dialog["lines"])
        })
    return result

def get_dialog(dialog_id):
    """获取指定对话内容"""
    return DIALOGS.get(dialog_id)
