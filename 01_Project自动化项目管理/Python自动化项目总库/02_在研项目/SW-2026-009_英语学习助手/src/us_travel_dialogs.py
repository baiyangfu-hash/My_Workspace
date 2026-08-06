"""
美国出差实用英语对话数据模块
专为在美国工作的商务出差人士设计，包含超市购物、交通出行、问路、日常交流、美国特有场景等
"""

DIALOGS = {

    # ============================================================
    # Category: 超市购物 (Supermarket)
    # ============================================================
    "supermarket_find": {
        "title": "超市找商品+结账",
        "title_en": "Finding Items & Checkout at Supermarket",
        "category": "超市购物",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "You",
                "text": "Excuse me, could you tell me where the peanut butter is?",
                "translation": "打扰一下，请问花生酱在哪里？",
                "highlight_words": ["peanut butter"]
            },
            {
                "speaker": "Staff",
                "text": "Sure, that'd be in aisle 7, on the left side, top shelf.",
                "translation": "当然，在7号通道，左边，最上面那层。",
                "highlight_words": ["aisle", "shelf"]
            },
            {
                "speaker": "You",
                "text": "Great, thanks. And do you have any gluten-free bread?",
                "translation": "好的，谢谢。你们有无麸质面包吗？",
                "highlight_words": ["gluten-free"]
            },
            {
                "speaker": "Staff",
                "text": "Yes, check the bakery section, right next to the organic area.",
                "translation": "有的，在烘焙区，就在有机食品区旁边。",
                "highlight_words": ["bakery", "organic"]
            },
            {
                "speaker": "You",
                "text": "Perfect. One more thing — where can I find trash bags?",
                "translation": "太好了。还有一件事——垃圾袋在哪里？",
                "highlight_words": ["trash bags"]
            },
            {
                "speaker": "Staff",
                "text": "Aisle 12, with the cleaning supplies and paper towels.",
                "translation": "12号通道，跟清洁用品和纸巾在一起。",
                "highlight_words": ["cleaning supplies", "paper towels"]
            },
            {
                "speaker": "Cashier",
                "text": "Hi, did you find everything you were looking for?",
                "translation": "您好，您要的东西都找到了吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Yeah, I think so. Thanks.",
                "translation": "嗯，都找到了。谢谢。",
                "highlight_words": []
            },
            {
                "speaker": "Cashier",
                "text": "Paper or plastic?",
                "translation": "要纸袋还是塑料袋？",
                "highlight_words": ["paper", "plastic"]
            },
            {
                "speaker": "You",
                "text": "Plastic is fine. Actually, I brought my own bag — here you go.",
                "translation": "塑料袋就行。其实我带了购物袋——给你。",
                "highlight_words": ["brought my own bag"]
            },
            {
                "speaker": "Cashier",
                "text": "Oh great, I'll bag those for you. Would you like to sign up for our rewards card? You'd save 10% today.",
                "translation": "哦太好了，我帮您装袋。您想注册我们的会员卡吗？今天可以省10%。",
                "highlight_words": ["rewards card", "sign up"]
            },
            {
                "speaker": "You",
                "text": "No thanks, I'm just visiting. Debit or credit?",
                "translation": "不了谢谢，我只是来出差。刷卡还是借记？",
                "highlight_words": ["debit", "credit"]
            },
            {
                "speaker": "Cashier",
                "text": "Go ahead and insert your card. You can remove it now. Would you like cash back?",
                "translation": "请插卡。现在可以拔卡了。需要现金返还吗？",
                "highlight_words": ["insert", "cash back"]
            },
            {
                "speaker": "You",
                "text": "No, I'm good. Thank you!",
                "translation": "不用了，谢谢！",
                "highlight_words": ["I'm good"]
            },
            {
                "speaker": "Cashier",
                "text": "You're all set. Have a great day!",
                "translation": "都办好了。祝您愉快！",
                "highlight_words": ["You're all set"]
            }
        ]
    },

    "self_checkout": {
        "title": "自助结账",
        "title_en": "Self-Checkout",
        "category": "超市购物",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Machine",
                "text": "Welcome. Please scan your first item.",
                "translation": "欢迎。请扫描您的第一件商品。",
                "highlight_words": ["scan"]
            },
            {
                "speaker": "You",
                "text": "(scanning items) ... okay, that's everything.",
                "translation": "（扫描商品中）……好的，都扫完了。",
                "highlight_words": []
            },
            {
                "speaker": "Machine",
                "text": "Unexpected item in the bagging area. Please remove the item and try again.",
                "translation": "装袋区出现未扫描商品。请移除商品后重试。",
                "highlight_words": ["unexpected item", "bagging area"]
            },
            {
                "speaker": "You",
                "text": "Ugh, not again... (removes item and rescans)",
                "translation": "又来了……（移除商品重新扫描）",
                "highlight_words": []
            },
            {
                "speaker": "Machine",
                "text": "Please wait for assistance. An attendant has been notified.",
                "translation": "请等待协助。已通知工作人员。",
                "highlight_words": ["assistance", "attendant"]
            },
            {
                "speaker": "Attendant",
                "text": "Hey, no worries. Let me override that for you. What happened?",
                "translation": "嘿，没事。我来帮您解除。怎么了？",
                "highlight_words": ["override"]
            },
            {
                "speaker": "You",
                "text": "It kept saying unexpected item. I think the scale is just being sensitive.",
                "translation": "它一直说有未扫描商品。我觉得是秤太敏感了。",
                "highlight_words": ["scale", "sensitive"]
            },
            {
                "speaker": "Attendant",
                "text": "Yeah, these machines can be finicky. I've cleared the error. Go ahead and continue.",
                "translation": "是啊，这些机器有时候挺挑剔的。我已经清除了错误，继续吧。",
                "highlight_words": ["finicky", "clear the error"]
            },
            {
                "speaker": "You",
                "text": "Thanks. Now... do I need to weigh these bananas?",
                "translation": "谢谢。现在……我需要称这些香蕉吗？",
                "highlight_words": ["weigh"]
            },
            {
                "speaker": "Attendant",
                "text": "Yep, put them on the scale and hit the lookup button. Search 'bananas' on the screen.",
                "translation": "对，放在秤上然后按查找键。在屏幕上搜索'bananas'。",
                "highlight_words": ["lookup"]
            },
            {
                "speaker": "You",
                "text": "Got it. And how do I pay?",
                "translation": "明白了。怎么付款？",
                "highlight_words": []
            },
            {
                "speaker": "Attendant",
                "text": "Just tap your card or phone on the reader when you're done scanning.",
                "translation": "扫完后在感应器上刷一下卡或手机就行。",
                "highlight_words": ["tap", "reader"]
            },
            {
                "speaker": "Machine",
                "text": "Please select your payment method.",
                "translation": "请选择付款方式。",
                "highlight_words": ["payment method"]
            },
            {
                "speaker": "You",
                "text": "(taps card) ... there we go.",
                "translation": "（刷卡）……好了。",
                "highlight_words": []
            },
            {
                "speaker": "Machine",
                "text": "Your transaction is complete. Please take your receipt. Thank you for shopping with us.",
                "translation": "交易完成。请取走收据。感谢光临。",
                "highlight_words": ["transaction", "receipt"]
            },
            {
                "speaker": "Attendant",
                "text": "You're good to go! Have a nice one.",
                "translation": "可以走了！祝您愉快。",
                "highlight_words": ["good to go"]
            }
        ]
    },

    "supermarket_return": {
        "title": "超市退换货",
        "title_en": "Returning / Exchanging Items at Supermarket",
        "category": "超市购物",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "You",
                "text": "Hi, I'd like to return this. I bought it yesterday but it's expired.",
                "translation": "你好，我想退这个。昨天买的，但已经过期了。",
                "highlight_words": ["return", "expired"]
            },
            {
                "speaker": "CS Staff",
                "text": "I'm sorry about that. Do you have your receipt with you?",
                "translation": "很抱歉。您带收据了吗？",
                "highlight_words": ["receipt"]
            },
            {
                "speaker": "You",
                "text": "Yes, here it is. And I paid with my credit card.",
                "translation": "带了，在这里。我是用信用卡付的。",
                "highlight_words": []
            },
            {
                "speaker": "CS Staff",
                "text": "Perfect, that makes it easy. Let me scan the item... yep, I can see the purchase right here.",
                "translation": "太好了，这样很方便。让我扫一下商品……好的，我能看到购买记录。",
                "highlight_words": ["purchase"]
            },
            {
                "speaker": "CS Staff",
                "text": "Would you like a refund or would you prefer to exchange it for a fresh one?",
                "translation": "您想退款还是换一个新鲜的？",
                "highlight_words": ["refund", "exchange"]
            },
            {
                "speaker": "You",
                "text": "I'd like to exchange it, please. Do you have another one that's not expired?",
                "translation": "我想换一个。你们有没过期的吗？",
                "highlight_words": ["exchange"]
            },
            {
                "speaker": "CS Staff",
                "text": "Let me check... Actually, all the ones on the shelf have the same date. I can give you a refund instead, or I can check if we have more in the back.",
                "translation": "我看看……实际上货架上所有的都是同一日期。我可以给您退款，或者我去后面仓库看看有没有新的。",
                "highlight_words": ["in the back"]
            },
            {
                "speaker": "You",
                "text": "Could you check in the back? I'd rather get the product if possible.",
                "translation": "能去后面看看吗？如果能买到的话我宁愿换货。",
                "highlight_words": ["I'd rather"]
            },
            {
                "speaker": "CS Staff",
                "text": "Sure, give me just a sec. ... Good news, I found a fresh batch!",
                "translation": "当然，稍等一下。……好消息，我找到了一批新鲜的！",
                "highlight_words": ["batch", "just a sec"]
            },
            {
                "speaker": "You",
                "text": "Awesome, thank you so much.",
                "translation": "太好了，非常感谢。",
                "highlight_words": []
            },
            {
                "speaker": "CS Staff",
                "text": "Here you go. The refund difference will go back to your card within 3 to 5 business days.",
                "translation": "给您。退款差额会在3到5个工作日内退回您的卡。",
                "highlight_words": ["business days"]
            },
            {
                "speaker": "You",
                "text": "Wait, there's a price difference?",
                "translation": "等等，有差价？",
                "highlight_words": ["price difference"]
            },
            {
                "speaker": "CS Staff",
                "text": "Just a few cents — the new one is slightly cheaper. It'll be credited back automatically.",
                "translation": "就几美分——新的便宜一点。会自动退回的。",
                "highlight_words": ["credited", "automatically"]
            },
            {
                "speaker": "You",
                "text": "Oh, no worries about that. Thanks again for your help!",
                "translation": "哦，那没关系。再次感谢你的帮助！",
                "highlight_words": ["no worries"]
            },
            {
                "speaker": "CS Staff",
                "text": "No problem at all. Have a good one!",
                "translation": "完全没问题。祝您愉快！",
                "highlight_words": ["No problem"]
            }
        ]
    },

    # ============================================================
    # Category: 交通出行 (Transportation)
    # ============================================================
    "rental_car": {
        "title": "租车取车",
        "title_en": "Rental Car Pickup",
        "category": "交通出行",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Agent",
                "text": "Welcome to Enterprise. What's your name and confirmation number?",
                "translation": "欢迎来到Enterprise。请问您的名字和确认号？",
                "highlight_words": ["confirmation number"]
            },
            {
                "speaker": "You",
                "text": "Hi, I'm Li Wei. My confirmation number is... let me pull it up... it's 748291.",
                "translation": "你好，我是李伟。确认号是……我查一下……748291。",
                "highlight_words": ["pull it up"]
            },
            {
                "speaker": "Agent",
                "text": "Great, I've got your reservation right here. A compact car for five days, returning on Friday. That's correct?",
                "translation": "好的，找到您的预订了。小型车，5天，周五还车。对吗？",
                "highlight_words": ["compact", "reservation"]
            },
            {
                "speaker": "You",
                "text": "Yes, that's right.",
                "translation": "对，没错。",
                "highlight_words": []
            },
            {
                "speaker": "Agent",
                "text": "Can I see your driver's license and a credit card?",
                "translation": "请出示您的驾照和信用卡。",
                "highlight_words": ["driver's license"]
            },
            {
                "speaker": "You",
                "text": "Sure, here's my license. And here's my credit card. I have an international driver's permit as well — do you need that?",
                "translation": "当然，这是我的驾照。这是信用卡。我还有国际驾照许可——需要吗？",
                "highlight_words": ["international driver's permit"]
            },
            {
                "speaker": "Agent",
                "text": "Thanks. We don't need the international permit for most states, but good that you have it. Now, would you like to add any insurance coverage?",
                "translation": "谢谢。大多数州不需要国际驾照许可，但有的话也好。现在，您要加保险吗？",
                "highlight_words": ["insurance coverage"]
            },
            {
                "speaker": "You",
                "text": "What are my options?",
                "translation": "都有哪些选项？",
                "highlight_words": ["options"]
            },
            {
                "speaker": "Agent",
                "text": "We have CDW — Collision Damage Waiver — which covers damage to the rental car. That's $15 a day. We also offer liability coverage for $12 a day.",
                "translation": "我们有CDW——碰撞损害免责——涵盖租车本身的损坏，每天15美元。还有责任险，每天12美元。",
                "highlight_words": ["Collision Damage Waiver", "liability"]
            },
            {
                "speaker": "You",
                "text": "My personal auto insurance and credit card already cover rental cars, so I think I'll pass on those.",
                "translation": "我的个人车险和信用卡已经覆盖租车了，所以就不加了。",
                "highlight_words": ["pass on those"]
            },
            {
                "speaker": "Agent",
                "text": "No problem. I do want to let you know we're running a special — I can upgrade you to a full-size sedan for just $5 more a day. Interested?",
                "translation": "没问题。我想告诉您我们有个特价——只要每天多5美元就能升级到全尺寸轿车。有兴趣吗？",
                "highlight_words": ["upgrade", "full-size sedan"]
            },
            {
                "speaker": "You",
                "text": "Hmm, what kind of car would that be?",
                "translation": "嗯，是什么样的车？",
                "highlight_words": []
            },
            {
                "speaker": "Agent",
                "text": "It'd be a Nissan Altima or similar. More room, better for highway driving.",
                "translation": "日产Altima或同级别车型。空间更大，高速驾驶更舒适。",
                "highlight_words": ["or similar", "highway"]
            },
            {
                "speaker": "You",
                "text": "Sure, why not. Let's do the upgrade.",
                "translation": "行，那就升级吧。",
                "highlight_words": ["Let's do"]
            },
            {
                "speaker": "Agent",
                "text": "Awesome. Your total comes to $275 including tax. I'll need you to initial here and sign at the bottom. The car is in spot C-14. Full tank of gas — please return it with a full tank to avoid the refueling charge.",
                "translation": "太好了。含税总共275美元。请在这里首字母签名，底部签全名。车在C-14车位。油箱是满的——请加满油还车，避免加油费。",
                "highlight_words": ["initial", "full tank", "refueling charge"]
            },
            {
                "speaker": "You",
                "text": "Got it. Is there a GPS in the car?",
                "translation": "明白了。车里有GPS吗？",
                "highlight_words": []
            },
            {
                "speaker": "Agent",
                "text": "It has Apple CarPlay and Android Auto, so you can use Google Maps or Waze. Here are your keys. Drive safe!",
                "translation": "有Apple CarPlay和Android Auto，可以用Google Maps或Waze。这是钥匙。注意安全！",
                "highlight_words": ["Apple CarPlay", "Android Auto"]
            }
        ]
    },

    "rental_car_return": {
        "title": "还车",
        "title_en": "Returning a Rental Car",
        "category": "交通出行",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "Attendant",
                "text": "Welcome back! Returning the Altima?",
                "translation": "欢迎回来！还Altima吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Yes, here are the keys. I filled up the tank at the station down the road.",
                "translation": "是的，这是钥匙。我在路边的加油站加满了油。",
                "highlight_words": ["filled up the tank"]
            },
            {
                "speaker": "Attendant",
                "text": "Great, let me check the fuel gauge... looks good, it's on F. I'll walk around and do a quick inspection.",
                "translation": "好的，我看看油表……不错，是满的。我绕车检查一下。",
                "highlight_words": ["fuel gauge", "inspection"]
            },
            {
                "speaker": "Attendant",
                "text": "Looks clean. I don't see any new damage. You're all good.",
                "translation": "看起来很干净。没有发现新的损坏。都没问题。",
                "highlight_words": ["damage"]
            },
            {
                "speaker": "You",
                "text": "Oh, by the way, I noticed a small scratch on the passenger side door when I picked it up. I took a photo of it.",
                "translation": "哦对了，取车时我注意到乘客侧车门上有个小划痕。我拍了照片。",
                "highlight_words": ["scratch"]
            },
            {
                "speaker": "Attendant",
                "text": "Good thinking. Let me check the pre-rental inspection... yeah, that scratch was already noted. No worries there.",
                "translation": "想得周到。我查一下租前检查记录……是的，那个划痕已经记录了。没问题。",
                "highlight_words": ["pre-rental", "noted"]
            },
            {
                "speaker": "You",
                "text": "That's a relief. Can I get a copy of the final receipt?",
                "translation": "那就好。我能要一份最终收据的副本吗？",
                "highlight_words": ["That's a relief", "copy"]
            },
            {
                "speaker": "Attendant",
                "text": "Absolutely. It'll be emailed to the address on file. Anything else I can help you with?",
                "translation": "当然。会发到您留的邮箱。还有其他需要帮忙的吗？",
                "highlight_words": ["on file"]
            },
            {
                "speaker": "You",
                "text": "No, that's it. Thanks for making this easy!",
                "translation": "没了，就这样。谢谢，很顺利！",
                "highlight_words": []
            },
            {
                "speaker": "Attendant",
                "text": "You bet. Have a safe flight home!",
                "translation": "不客气。祝您飞行平安！",
                "highlight_words": ["You bet"]
            }
        ]
    },

    "gas_station": {
        "title": "加油站",
        "title_en": "At the Gas Station",
        "category": "交通出行",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "You",
                "text": "Hi, could I get $40 on pump 5, please?",
                "translation": "你好，5号加油机加40美元的油。",
                "highlight_words": ["pump"]
            },
            {
                "speaker": "Cashier",
                "text": "Sure. Cash or credit?",
                "translation": "好的。现金还是刷卡？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Credit, please.",
                "translation": "刷卡。",
                "highlight_words": []
            },
            {
                "speaker": "Cashier",
                "text": "Go ahead, it's authorized.",
                "translation": "可以了，已授权。",
                "highlight_words": ["authorized"]
            },
            {
                "speaker": "You",
                "text": "Thanks. ... (pumps gas) ... Excuse me, which one is the regular unleaded?",
                "translation": "谢谢。……（加油中）……打扰一下，哪个是普通无铅汽油？",
                "highlight_words": ["regular unleaded"]
            },
            {
                "speaker": "Cashier",
                "text": "The green handle is regular. Yellow is mid-grade, and red is premium.",
                "translation": "绿色把手是普通油。黄色是中级，红色是高级。",
                "highlight_words": ["mid-grade", "premium"]
            },
            {
                "speaker": "You",
                "text": "Oh wait, I already used the yellow one by mistake. Is that going to be a problem?",
                "translation": "哦不，我已经误用了黄色的。这会有问题吗？",
                "highlight_words": ["by mistake"]
            },
            {
                "speaker": "Cashier",
                "text": "Nah, it's fine. Mid-grade won't hurt the car. It just costs a little more. The pump will stop at your $40 limit.",
                "translation": "没事的。中级油不会伤车，就是贵一点。加油枪会在40美元时自动停。",
                "highlight_words": ["limit"]
            },
            {
                "speaker": "You",
                "text": "Oh good. By the way, do you have a squeegee? My windshield is pretty dirty.",
                "translation": "哦好的。顺便问一下，有刮水器吗？我的挡风玻璃挺脏的。",
                "highlight_words": ["squeegee", "windshield"]
            },
            {
                "speaker": "Cashier",
                "text": "Yeah, there's one right next to the pump on the side.",
                "translation": "有，就在加油机旁边的架子上。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Great. And can I get a receipt?",
                "translation": "好的。能给我一张收据吗？",
                "highlight_words": ["receipt"]
            },
            {
                "speaker": "Cashier",
                "text": "It'll print at the pump. You can also choose 'yes' for receipt on the screen.",
                "translation": "加油机上会打印出来。您也可以在屏幕上选择'要收据'。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Perfect. Thanks!",
                "translation": "太好了。谢谢！",
                "highlight_words": []
            }
        ]
    },

    "uber_ride": {
        "title": "Uber/Lyft乘车",
        "title_en": "Taking an Uber/Lyft Ride",
        "category": "交通出行",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Driver",
                "text": "Hey, are you Wei?",
                "translation": "嘿，你是伟吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Yes, that's me!",
                "translation": "对，是我！",
                "highlight_words": []
            },
            {
                "speaker": "Driver",
                "text": "Great, hop in. How's it going?",
                "translation": "太好了，上车吧。最近怎么样？",
                "highlight_words": ["hop in"]
            },
            {
                "speaker": "You",
                "text": "Good, thanks. So the destination I put in is the Marriott on 5th Street, but could you drop me off at the entrance on the north side? The main entrance gets really backed up.",
                "translation": "挺好的，谢谢。目的地我设的是第五街的万豪酒店，但能不能把我放在北门入口？正门那边经常堵。",
                "highlight_words": ["drop off", "backed up"]
            },
            {
                "speaker": "Driver",
                "text": "No problem, I know exactly where that is. I'll take Broadway — it's a bit faster this time of day.",
                "translation": "没问题，我清楚在哪。我走百老汇大街——这个时段快一些。",
                "highlight_words": ["this time of day"]
            },
            {
                "speaker": "You",
                "text": "Sounds good. By the way, do you mind if I make a quick phone call?",
                "translation": "好的。对了，介意我打个简短的电话吗？",
                "highlight_words": ["do you mind"]
            },
            {
                "speaker": "Driver",
                "text": "Not at all, go right ahead.",
                "translation": "完全没关系，请便。",
                "highlight_words": ["go right ahead"]
            },
            {
                "speaker": "You",
                "text": "(on phone) ... Okay, I'll be there in about 15 minutes. Thanks. (hangs up) Sorry about that.",
                "translation": "（打电话中）……好的，我大概15分钟后到。谢谢。（挂断）抱歉。",
                "highlight_words": ["hang up"]
            },
            {
                "speaker": "Driver",
                "text": "All good. So, are you visiting from out of town?",
                "translation": "没事。你是外地来的吗？",
                "highlight_words": ["out of town"]
            },
            {
                "speaker": "You",
                "text": "Yeah, I'm here for a conference. First time in Chicago, actually.",
                "translation": "对，来开会。其实是第一次来芝加哥。",
                "highlight_words": ["conference"]
            },
            {
                "speaker": "Driver",
                "text": "Oh nice! You should check out the lakefront while you're here. The view is amazing.",
                "translation": "哦不错！你应该趁此机会去湖边看看，风景很棒。",
                "highlight_words": ["lakefront", "check out"]
            },
            {
                "speaker": "You",
                "text": "I'll definitely do that. Hey, the entrance is coming up on the right — you can pull over right after the crosswalk.",
                "translation": "一定会的。嘿，北门入口就在右边前方——过人行横道后靠边停就行。",
                "highlight_words": ["pull over", "crosswalk"]
            },
            {
                "speaker": "Driver",
                "text": "Here you go. Watch your step getting out. Have a great trip!",
                "translation": "到了。下车注意安全。旅途愉快！",
                "highlight_words": ["Watch your step"]
            },
            {
                "speaker": "You",
                "text": "Thanks a lot. You too — take care!",
                "translation": "非常感谢。你也是——保重！",
                "highlight_words": ["take care"]
            }
        ]
    },

    "domestic_flight": {
        "title": "国内航班值机+安检",
        "title_en": "Domestic Flight Check-in & TSA Security",
        "category": "交通出行",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Agent",
                "text": "Good morning. May I see your ID, please?",
                "translation": "早上好。请出示您的身份证件。",
                "highlight_words": ["ID"]
            },
            {
                "speaker": "You",
                "text": "Sure, here's my passport. I'm checking in for flight AA 2147 to Dallas.",
                "translation": "当然，这是我的护照。我要办理AA 2147航班去达拉斯的值机。",
                "highlight_words": ["checking in"]
            },
            {
                "speaker": "Agent",
                "text": "Are you checking any bags today?",
                "translation": "今天有托运行李吗？",
                "highlight_words": ["checking bags"]
            },
            {
                "speaker": "You",
                "text": "Yes, one bag to check. My carry-on is just a backpack.",
                "translation": "是的，一件托运。随身行李只有一个背包。",
                "highlight_words": ["carry-on", "backpack"]
            },
            {
                "speaker": "Agent",
                "text": "Okay, that'll be $30 for the first checked bag. Would you like to pay now?",
                "translation": "好的，第一件托运行李30美元。现在付款吗？",
                "highlight_words": ["checked bag"]
            },
            {
                "speaker": "You",
                "text": "Yes, go ahead and charge it to the card on file.",
                "translation": "好的，用之前留的卡扣款吧。",
                "highlight_words": ["charge it"]
            },
            {
                "speaker": "Agent",
                "text": "Done. I've got you in seat 14A, a window seat. Your bag tag is attached — just drop it at the baggage drop down the hall. Your flight boards at 2:15 from Gate B22.",
                "translation": "好了。您的座位是14A，靠窗。行李标签已贴好——在大厅那头的行李托运处放下就行。航班2:15开始登机，B22登机口。",
                "highlight_words": ["bag tag", "boards", "gate"]
            },
            {
                "speaker": "You",
                "text": "Great. Do I need to take out my laptop at the security checkpoint?",
                "translation": "好的。安检时需要把笔记本电脑拿出来吗？",
                "highlight_words": ["security checkpoint", "laptop"]
            },
            {
                "speaker": "Agent",
                "text": "Yes, and any liquids need to be in a quart-sized bag. You know the drill.",
                "translation": "是的，液体需要放在一夸脱大小的袋子里。你应该知道的。",
                "highlight_words": ["liquids", "quart-sized", "You know the drill"]
            },
            {
                "speaker": "TSA Officer",
                "text": "Please place your belongings in the bin. Shoes off, belt off, and laptops need to go in a separate bin.",
                "translation": "请把物品放入托盘。脱鞋、解皮带，笔记本电脑放单独的托盘。",
                "highlight_words": ["bin", "belt off"]
            },
            {
                "speaker": "You",
                "text": "Sure. Do I need to take out my tablet too?",
                "translation": "好的。平板电脑也需要拿出来吗？",
                "highlight_words": ["tablet"]
            },
            {
                "speaker": "TSA Officer",
                "text": "No, tablets can stay in the bag. Just laptops.",
                "translation": "不用，平板可以放在包里。只有笔记本电脑需要拿出来。",
                "highlight_words": []
            },
            {
                "speaker": "TSA Officer",
                "text": "Step through, please. Arms up. ... You're good to go. Grab your stuff on the other side.",
                "translation": "请走过安检门。双手举起。……可以了。在另一边拿好您的物品。",
                "highlight_words": ["Arms up"]
            },
            {
                "speaker": "You",
                "text": "Thank you. Which way to Gate B22?",
                "translation": "谢谢。B22登机口怎么走？",
                "highlight_words": []
            },
            {
                "speaker": "TSA Officer",
                "text": "Go past the food court, take a left, and follow the signs. It's about a 10-minute walk.",
                "translation": "走过美食广场，左转，跟着指示牌走。大约走10分钟。",
                "highlight_words": ["food court", "follow the signs"]
            }
        ]
    },

    "ferry": {
        "title": "轮渡",
        "title_en": "Taking the Ferry",
        "category": "交通出行",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "You",
                "text": "Hi, I'd like to buy a round-trip ticket to Bainbridge Island, please.",
                "translation": "你好，我想买一张去班布里奇岛的往返票。",
                "highlight_words": ["round-trip ticket"]
            },
            {
                "speaker": "Ticket Agent",
                "text": "Sure thing. Adult or senior?",
                "translation": "没问题。成人票还是老年票？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Adult, please. How much is it?",
                "translation": "成人票。多少钱？",
                "highlight_words": []
            },
            {
                "speaker": "Ticket Agent",
                "text": "That'll be $18.50 for a round-trip. The next ferry leaves at 2:45 and it takes about 35 minutes.",
                "translation": "往返票18.50美元。下一班轮渡2:45出发，大约35分钟。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Sounds good. Can I pay with Apple Pay?",
                "translation": "好的。可以用Apple Pay吗？",
                "highlight_words": ["Apple Pay"]
            },
            {
                "speaker": "Ticket Agent",
                "text": "Absolutely. Just tap here. ... There you go. Here's your ticket. You can board from either the upper or lower deck.",
                "translation": "当然。在这里刷一下。……好了。这是您的票。可以从上层或下层甲板上船。",
                "highlight_words": ["tap", "upper deck", "lower deck"]
            },
            {
                "speaker": "You",
                "text": "Is there indoor seating? It's pretty chilly out here.",
                "translation": "有室内座位吗？外面挺冷的。",
                "highlight_words": ["indoor seating", "chilly"]
            },
            {
                "speaker": "Ticket Agent",
                "text": "Yes, the main cabin is heated. There's also a snack bar on the lower level if you get hungry.",
                "translation": "有的，主舱有暖气。下层还有小吃吧，饿了可以去。",
                "highlight_words": ["main cabin", "heated", "snack bar"]
            },
            {
                "speaker": "You",
                "text": "Perfect. And do I need to validate this ticket somewhere, or is this it?",
                "translation": "太好了。我需要在什么地方验票吗，还是就这样？",
                "highlight_words": ["validate"]
            },
            {
                "speaker": "Ticket Agent",
                "text": "That's your ticket — just keep it handy and show it when boarding. Enjoy the ride!",
                "translation": "这就是您的票——随身带着，上船时出示即可。旅途愉快！",
                "highlight_words": ["keep it handy"]
            }
        ]
    },

    # ============================================================
    # Category: 问路 (Asking Directions)
    # ============================================================
    "street_directions": {
        "title": "街头问路",
        "title_en": "Asking Directions on the Street",
        "category": "问路",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "You",
                "text": "Excuse me, could you tell me how to get to the nearest CVS pharmacy?",
                "translation": "打扰一下，请问最近的CVS药房怎么走？",
                "highlight_words": ["CVS pharmacy"]
            },
            {
                "speaker": "Pedestrian",
                "text": "Sure! Go down this street for two blocks, then make a right on Elm Street. You'll see it on the corner, next to a Chipotle.",
                "translation": "当然！沿这条街走两个街区，然后在Elm街右转。你会在拐角看到它，就在Chipotle旁边。",
                "highlight_words": ["blocks", "make a right", "corner"]
            },
            {
                "speaker": "You",
                "text": "Two blocks down, then right on Elm. Got it. Is it walkable from here?",
                "translation": "走两个街区，然后在Elm街右转。明白了。从这走着去方便吗？",
                "highlight_words": ["walkable"]
            },
            {
                "speaker": "Pedestrian",
                "text": "Yeah, it's about a 5-minute walk. You can't miss it — it's got a big red sign.",
                "translation": "方便的，大约走5分钟。你不会错过的——有个很大的红色招牌。",
                "highlight_words": ["You can't miss it"]
            },
            {
                "speaker": "You",
                "text": "Great. One more question — is there a good coffee shop around here?",
                "translation": "太好了。还有一个问题——这附近有好喝的咖啡店吗？",
                "highlight_words": []
            },
            {
                "speaker": "Pedestrian",
                "text": "There's a Blue Bottle Coffee just past CVS, about a block further down Elm. Really good coffee.",
                "translation": "过了CVS有一家Blue Bottle Coffee，沿Elm街再走一个街区。咖啡非常好喝。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Awesome, I'll check it out. Thanks for your help!",
                "translation": "太棒了，我去看看。谢谢你的帮助！",
                "highlight_words": []
            },
            {
                "speaker": "Pedestrian",
                "text": "No problem. Have a good one!",
                "translation": "不客气。祝您愉快！",
                "highlight_words": []
            }
        ]
    },

    "subway": {
        "title": "地铁问路",
        "title_en": "Subway / Metro Navigation",
        "category": "问路",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "You",
                "text": "Excuse me, which line do I take to get to Times Square?",
                "translation": "打扰一下，去时代广场坐哪条线？",
                "highlight_words": ["line"]
            },
            {
                "speaker": "Stranger",
                "text": "You can take the 1, 2, 3, N, Q, R, or 7 train — they all stop there. What station are you at now?",
                "translation": "你可以坐1、2、3、N、Q、R或7号线——都到那里。你现在在哪个站？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "I'm at Penn Station.",
                "translation": "我在Penn Station。",
                "highlight_words": []
            },
            {
                "speaker": "Stranger",
                "text": "Oh perfect, just take the 1 train uptown. It's three stops — 34th, 42nd, then Times Square at 42nd Street.",
                "translation": "哦太好了，坐1号线往北方向就行。三站——34街、42街，然后就是时代广场42街站。",
                "highlight_words": ["uptown", "stops"]
            },
            {
                "speaker": "You",
                "text": "Uptown, got it. Where do I buy the MetroCard?",
                "translation": "往北方向，明白了。在哪里买地铁卡？",
                "highlight_words": ["MetroCard"]
            },
            {
                "speaker": "Stranger",
                "text": "There's a vending machine by the turnstiles. You can also use the MTA app and tap your phone — it's actually cheaper that way.",
                "translation": "闸机旁边有自动售票机。你也可以用MTA app刷手机——那样还便宜一些。",
                "highlight_words": ["vending machine", "turnstiles", "tap"]
            },
            {
                "speaker": "You",
                "text": "Good to know. Is the 1 train on the upper or lower level?",
                "translation": "知道了。1号线在上层还是下层？",
                "highlight_words": ["upper level", "lower level"]
            },
            {
                "speaker": "Stranger",
                "text": "Follow the signs that say '1, 2, 3 trains uptown'. It's downstairs. The platform will be on the right side.",
                "translation": "跟着标有'1、2、3号线往北'的指示牌走。在楼下。站台在右边。",
                "highlight_words": ["platform", "signs"]
            },
            {
                "speaker": "You",
                "text": "Thanks so much. One last thing — do the trains run 24 hours?",
                "translation": "非常感谢。最后一个问题——地铁是24小时运营的吗？",
                "highlight_words": ["24 hours"]
            },
            {
                "speaker": "Stranger",
                "text": "The 1 train runs 24/7, but on weekends there might be some construction delays. Check the MTA app for updates.",
                "translation": "1号线是全天运营的，但周末可能有施工延误。查一下MTA app了解最新情况。",
                "highlight_words": ["24/7", "construction delays"]
            },
            {
                "speaker": "You",
                "text": "Will do. Thanks again!",
                "translation": "好的。再次感谢！",
                "highlight_words": ["Will do"]
            }
        ]
    },

    "mall_directions": {
        "title": "商场内问路",
        "title_en": "Finding Stores in a Mall",
        "category": "问路",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "You",
                "text": "Excuse me, do you know where the Apple Store is in this mall?",
                "translation": "打扰一下，你知道这个商场里的Apple Store在哪吗？",
                "highlight_words": []
            },
            {
                "speaker": "Info Desk",
                "text": "Sure, it's on the second floor, right across from the food court. If you take the escalator near the main entrance, it'll be straight ahead.",
                "translation": "当然，在二楼，就在美食广场对面。从正门附近的自动扶梯上去，直走就到。",
                "highlight_words": ["escalator", "food court", "straight ahead"]
            },
            {
                "speaker": "You",
                "text": "Great. And is there a bathroom nearby?",
                "translation": "好的。附近有洗手间吗？",
                "highlight_words": ["bathroom"]
            },
            {
                "speaker": "Info Desk",
                "text": "Yes, there's one right next to the Apple Store, between it and the Gap.",
                "translation": "有的，就在Apple Store旁边，在它和Gap之间。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Perfect. Also, do you know what time the stores close today?",
                "translation": "太好了。还有，你知道今天商场几点关门吗？",
                "highlight_words": ["close"]
            },
            {
                "speaker": "Info Desk",
                "text": "Most stores close at 9 PM on weekdays, but the Apple Store stays open until 10. The mall itself shuts down at 9:30.",
                "translation": "大部分工作日是9点关门，但Apple Store开到10点。商场本身9:30关闭。",
                "highlight_words": ["shut down"]
            },
            {
                "speaker": "You",
                "text": "Good to know. Is there a good place to get a quick bite around here?",
                "translation": "知道了。这附近有什么吃简餐的好地方吗？",
                "highlight_words": ["quick bite"]
            },
            {
                "speaker": "Info Desk",
                "text": "The food court on the second floor has a lot of options — Chick-fil-A, Panda Express, and a Shake Shack. There's also a Starbucks on the first floor near the south entrance.",
                "translation": "二楼美食广场选择很多——Chick-fil-A、Panda Express，还有Shake Shack。一楼南门附近还有一家星巴克。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Awesome. Thanks for all the help!",
                "translation": "太棒了。谢谢你的帮助！",
                "highlight_words": []
            }
        ]
    },

    # ============================================================
    # Category: 日常交流 (Daily Communication)
    # ============================================================
    "hotel_checkin": {
        "title": "酒店入住",
        "title_en": "Hotel Check-in",
        "category": "日常交流",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Receptionist",
                "text": "Welcome to the Westin. Checking in today?",
                "translation": "欢迎来到Westin酒店。今天入住吗？",
                "highlight_words": ["checking in"]
            },
            {
                "speaker": "You",
                "text": "Yes, I have a reservation. The name is Li Wei.",
                "translation": "是的，我有预订。名字是李伟。",
                "highlight_words": ["reservation"]
            },
            {
                "speaker": "Receptionist",
                "text": "Let me pull that up for you... Here we go. A king room for four nights, checking out Friday. Can I see a photo ID and the credit card used for booking?",
                "translation": "我帮您查一下……找到了。大床房，住四晚，周五退房。请出示带照片的身份证件和预订用的信用卡。",
                "highlight_words": ["king room", "photo ID"]
            },
            {
                "speaker": "You",
                "text": "Sure, here's my passport and my Amex.",
                "translation": "当然，这是我的护照和American Express卡。",
                "highlight_words": ["Amex"]
            },
            {
                "speaker": "Receptionist",
                "text": "Thank you. I'll need to place a hold of $150 on your card for incidentals. It'll be released at checkout.",
                "translation": "谢谢。我需要在您的卡上预授权150美元作为杂费押金，退房时会释放。",
                "highlight_words": ["hold", "incidentals", "released"]
            },
            {
                "speaker": "You",
                "text": "No problem. Is it possible to get a room away from the elevator? I'm a light sleeper.",
                "translation": "没问题。能安排一间远离电梯的房间吗？我睡眠浅。",
                "highlight_words": ["light sleeper"]
            },
            {
                "speaker": "Receptionist",
                "text": "Absolutely. I've got you in room 714 — it's at the end of the hall, nice and quiet. And it faces the courtyard, so no street noise.",
                "translation": "当然可以。给您安排了714房间——在走廊尽头，很安静。而且朝向庭院，没有街道噪音。",
                "highlight_words": ["end of the hall", "courtyard", "street noise"]
            },
            {
                "speaker": "You",
                "text": "That sounds perfect. My flight got in early — is there any chance I can check in before 3 PM?",
                "translation": "听起来很完美。我的航班早到了——有可能在下午3点之前入住吗？",
                "highlight_words": ["got in early", "check in"]
            },
            {
                "speaker": "Receptionist",
                "text": "Let me see... The room is actually ready right now, so you're in luck! Or, if you'd prefer, I can hold your luggage and you can explore the area first.",
                "translation": "让我看看……房间其实已经准备好了，您运气不错！或者如果您愿意，我可以先帮您寄存行李，您先去周围逛逛。",
                "highlight_words": ["hold your luggage", "in luck"]
            },
            {
                "speaker": "You",
                "text": "The room is ready now? That's great, I'll go ahead and check in. I've been traveling all day.",
                "translation": "房间现在就准备好了？太好了，我直接入住吧。赶了一天的路。",
                "highlight_words": ["traveling all day"]
            },
            {
                "speaker": "Receptionist",
                "text": "I totally understand. Here's your key card — you'll need it for the elevator and your room. Breakfast is complimentary and served from 6:30 to 10 AM in the restaurant on the lobby level. The gym is open 24 hours.",
                "translation": "完全理解。这是您的房卡——电梯和房间都需要用到。早餐是免费的，在酒店大堂层的餐厅供应，时间是6:30到10点。健身房24小时开放。",
                "highlight_words": ["complimentary", "lobby level", "gym"]
            },
            {
                "speaker": "You",
                "text": "Does the room have a desk? I need to get some work done tonight.",
                "translation": "房间有书桌吗？我今晚需要处理一些工作。",
                "highlight_words": ["desk"]
            },
            {
                "speaker": "Receptionist",
                "text": "Yes, all our rooms have a work desk with an ergonomic chair and free Wi-Fi. The password is on the desk card in your room.",
                "translation": "有的，所有房间都有工作台，配有人体工学椅和免费Wi-Fi。密码在房间的桌上卡片上。",
                "highlight_words": ["ergonomic chair"]
            },
            {
                "speaker": "You",
                "text": "Perfect. One last thing — is there a laundry service?",
                "translation": "太好了。最后一件事——有洗衣服务吗？",
                "highlight_words": ["laundry service"]
            },
            {
                "speaker": "Receptionist",
                "text": "Yes, there's a laundry bag in your closet. Just fill it out and leave it by the door before 9 AM, and you'll get it back the same day. Enjoy your stay!",
                "translation": "有的，您衣柜里有一个洗衣袋。填好单子放在门口，上午9点之前，当天就能拿回来。祝您入住愉快！",
                "highlight_words": ["closet"]
            }
        ]
    },

    "hotel_service": {
        "title": "酒店客房服务",
        "title_en": "Hotel Room Service & Maintenance",
        "category": "日常交流",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "You",
                "text": "Hi, this is room 714. I just checked in and the AC doesn't seem to be working. It's pretty warm in here.",
                "translation": "你好，这里是714房间。我刚入住，空调好像不工作。房间里挺热的。",
                "highlight_words": ["AC"]
            },
            {
                "speaker": "Front Desk",
                "text": "I'm sorry about that, sir. Let me send someone up to take a look. Can you describe the issue?",
                "translation": "很抱歉，先生。我派人上去看看。您能描述一下问题吗？",
                "highlight_words": ["take a look"]
            },
            {
                "speaker": "You",
                "text": "The unit is on, but it's only blowing room-temperature air. I've tried lowering the thermostat, but nothing changes.",
                "translation": "空调开着，但只吹常温空气。我试过调低温度，但没有变化。",
                "highlight_words": ["blowing", "thermostat"]
            },
            {
                "speaker": "Front Desk",
                "text": "I understand. I'll send our maintenance team right away. They should be there within 15 minutes. In the meantime, would you like me to move you to a different room?",
                "translation": "我明白了。我马上派维修团队过去。他们15分钟内到。同时，您想换一间房吗？",
                "highlight_words": ["maintenance", "right away"]
            },
            {
                "speaker": "You",
                "text": "Let me wait and see if they can fix it first. I've already unpacked.",
                "translation": "我先等等看他们能不能修好。我已经把行李拆出来了。",
                "highlight_words": ["unpacked"]
            },
            {
                "speaker": "Maintenance",
                "text": "(knocking) Housekeeping! ... Oh, sorry — maintenance. Hi, I'm here about the AC issue.",
                "translation": "（敲门）客房服务！……哦抱歉——维修。你好，我来修空调的。",
                "highlight_words": ["Housekeeping"]
            },
            {
                "speaker": "You",
                "text": "Come in! Thanks for coming so quickly.",
                "translation": "请进！谢谢这么快就来。",
                "highlight_words": []
            },
            {
                "speaker": "Maintenance",
                "text": "No problem. Let me check the filter... ah, here's the issue. The filter was clogged. I've replaced it. Give it about 10 minutes and it should start cooling down.",
                "translation": "没问题。让我检查一下滤网……啊，找到问题了。滤网堵了。我已经换了。大约10分钟后应该开始降温。",
                "highlight_words": ["filter", "clogged", "cooling down"]
            },
            {
                "speaker": "You",
                "text": "Great, I can already feel it starting to work. Thanks!",
                "translation": "太好了，我已经感觉到开始制冷了。谢谢！",
                "highlight_words": []
            },
            {
                "speaker": "Maintenance",
                "text": "You're welcome. By the way, I noticed your TV remote batteries are low — I'll swap those out for you too.",
                "translation": "不客气。顺便说一下，我注意到您的电视遥控器电池快没电了——我也帮您换一下。",
                "highlight_words": ["remote", "batteries", "swap out"]
            },
            {
                "speaker": "You",
                "text": "Oh, I appreciate that. You guys are on top of it.",
                "translation": "哦，太感谢了。你们服务真周到。",
                "highlight_words": ["on top of it"]
            },
            {
                "speaker": "Maintenance",
                "text": "That's what we're here for. Is there anything else?",
                "translation": "这就是我们的工作。还有其他需要吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "No, that's everything. Thanks again!",
                "translation": "没了，就这些。再次感谢！",
                "highlight_words": []
            }
        ]
    },

    "hotel_checkout": {
        "title": "酒店退房",
        "title_en": "Hotel Checkout",
        "category": "日常交流",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "You",
                "text": "Hi, I'd like to check out. Room 714.",
                "translation": "你好，我要退房。714房间。",
                "highlight_words": ["check out"]
            },
            {
                "speaker": "Receptionist",
                "text": "Good morning! How was your stay, Mr. Li?",
                "translation": "早上好！李先生，入住体验怎么样？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "It was great, thank you. Very comfortable room.",
                "translation": "非常好，谢谢。房间很舒适。",
                "highlight_words": []
            },
            {
                "speaker": "Receptionist",
                "text": "Glad to hear that. Let me pull up your folio... You had the room for four nights at $189 per night, plus one room service charge of $32. The total comes to $788 before tax. With tax, it's $891.",
                "translation": "很高兴听您这么说。我调出您的账单……住了四晚，每晚189美元，加上一次客房服务费32美元。税前总计788美元。含税891美元。",
                "highlight_words": ["folio", "room service charge"]
            },
            {
                "speaker": "You",
                "text": "That matches what I expected. Could I get a detailed invoice for my company? They need it for expense reimbursement.",
                "translation": "跟我预期的一致。能给我一份详细发票吗？公司报销需要。",
                "highlight_words": ["invoice", "expense reimbursement"]
            },
            {
                "speaker": "Receptionist",
                "text": "Absolutely. I can email it to you right now. What's the best email address?",
                "translation": "当然。我现在就可以发给您。最好的邮箱地址是？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Please send it to wei.li@company.com. And could you make sure it's itemized? My finance department needs a breakdown of each charge.",
                "translation": "请发到wei.li@company.com。能确保是明细的吗？财务部门需要每笔费用的明细。",
                "highlight_words": ["itemized", "breakdown"]
            },
            {
                "speaker": "Receptionist",
                "text": "Of course, I'll send the itemized version. I'll also release the $150 incidental hold on your card. That may take 3 to 5 business days to reflect on your statement.",
                "translation": "当然，我发明细版。我也会释放您卡上的150美元杂费押金。可能需要3到5个工作日才会在账单上显示。",
                "highlight_words": ["incidental hold", "reflect on your statement"]
            },
            {
                "speaker": "You",
                "text": "Sounds good. I also used the laundry service — was that already added to the bill?",
                "translation": "好的。我还用了洗衣服务——已经加到账单上了吗？",
                "highlight_words": []
            },
            {
                "speaker": "Receptionist",
                "text": "Yes, the laundry charge of $45 is included. It's listed on the invoice as well.",
                "translation": "是的，45美元的洗衣费已经包含了。发票上也列出来了。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Perfect. Do I need to return the key card, or just leave it in the room?",
                "translation": "好的。我需要归还房卡吗，还是放在房间里就行？",
                "highlight_words": []
            },
            {
                "speaker": "Receptionist",
                "text": "Either way works. You can just drop it in the basket right here. Did you need a taxi or an Uber to the airport?",
                "translation": "都可以。直接放在这边的篮子里就行。您需要出租车或Uber去机场吗？",
                "highlight_words": ["Either way works"]
            },
            {
                "speaker": "You",
                "text": "No thanks, I already have a ride arranged. Thanks for everything!",
                "translation": "不用了谢谢，我已经安排好了车。感谢一切！",
                "highlight_words": []
            },
            {
                "speaker": "Receptionist",
                "text": "You're welcome. Safe travels, Mr. Li! We hope to see you again.",
                "translation": "不客气。一路平安，李先生！希望下次再见。",
                "highlight_words": ["Safe travels"]
            }
        ]
    },

    "restaurant_ordering": {
        "title": "餐厅点餐",
        "title_en": "Full Restaurant Ordering",
        "category": "日常交流",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Hostess",
                "text": "Hi there, welcome to The Capital Grille. Table for one?",
                "translation": "您好，欢迎来到The Capital Grille。一位？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Yes, just me tonight.",
                "translation": "是的，今晚就我一个人。",
                "highlight_words": []
            },
            {
                "speaker": "Hostess",
                "text": "Right this way. I've got a nice booth for you. Your server will be with you in just a moment.",
                "translation": "这边请。给您安排了一个不错的卡座。服务员马上就来。",
                "highlight_words": ["booth", "server"]
            },
            {
                "speaker": "Server",
                "text": "Good evening! My name's Jake, and I'll be taking care of you tonight. Can I start you off with something to drink?",
                "translation": "晚上好！我叫Jake，今晚由我为您服务。先给您来点喝的吗？",
                "highlight_words": ["start you off", "taking care of you"]
            },
            {
                "speaker": "You",
                "text": "Just a sparkling water for now, thanks. Could I also see the wine list?",
                "translation": "先来一杯气泡水，谢谢。能看一下酒单吗？",
                "highlight_words": ["sparkling water", "wine list"]
            },
            {
                "speaker": "Server",
                "text": "Of course. Here you go. And I'll be right back with your water. Take your time with the menu.",
                "translation": "当然。给您。我马上把水端来。慢慢看菜单。",
                "highlight_words": ["Take your time"]
            },
            {
                "speaker": "Server",
                "text": "Here's your water. Are you ready to order, or do you need a few more minutes?",
                "translation": "这是您的气泡水。您准备好点餐了吗，还是需要再看看？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "I think I'm ready. I'll have the filet mignon, medium rare. Does it come with any sides?",
                "translation": "我想好了。我要菲力牛排，三分熟。有配菜吗？",
                "highlight_words": ["filet mignon", "medium rare"]
            },
            {
                "speaker": "Server",
                "text": "It comes with your choice of one side — we have mashed potatoes, creamed spinach, asparagus, or truffle fries.",
                "translation": "可以选一份配菜——有土豆泥、奶油菠菜、芦笋或松露薯条。",
                "highlight_words": ["creamed spinach", "asparagus", "truffle fries"]
            },
            {
                "speaker": "You",
                "text": "I'll go with the truffle fries. Also, I have a nut allergy — is there anything I should avoid on the menu?",
                "translation": "我要松露薯条。还有，我对坚果过敏——菜单上有什么我需要避免的吗？",
                "highlight_words": ["nut allergy", "avoid"]
            },
            {
                "speaker": "Server",
                "text": "Good thing you mentioned that. The filet is fine, but I'd skip the dessert — several of them contain tree nuts. I'll make a note for the kitchen.",
                "translation": "还好您提了。菲力牛排没问题，但甜点就别点了——好几款含树坚果。我给厨房备注一下。",
                "highlight_words": ["tree nuts", "make a note"]
            },
            {
                "speaker": "You",
                "text": "I appreciate that. That's all for now, thank you.",
                "translation": "非常感谢。暂时就这些，谢谢。",
                "highlight_words": []
            },
            {
                "speaker": "Server",
                "text": "Sounds great. I'll get that started for you. ... How's everything tasting?",
                "translation": "好的，我去下单。……味道怎么样？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Excellent, the steak is cooked perfectly. Could I get the check when you get a chance?",
                "translation": "非常好，牛排火候完美。方便的时候能给我账单吗？",
                "highlight_words": ["get the check"]
            },
            {
                "speaker": "Server",
                "text": "Absolutely. Would you like to see the dessert menu?",
                "translation": "当然。您想看甜点菜单吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "No thanks, I'm pretty full. Just the check, please.",
                "translation": "不了谢谢，我挺饱的。账单就好。",
                "highlight_words": ["pretty full"]
            },
            {
                "speaker": "Server",
                "text": "Here you go. No rush at all. I can split it however you'd like. Is there anything else I can do for you?",
                "translation": "给您。不着急。账单可以按您需要的方式分开。还有其他需要吗？",
                "highlight_words": ["No rush", "split"]
            },
            {
                "speaker": "You",
                "text": "I'm all set, thanks. Just put it all on one card.",
                "translation": "都好了，谢谢。全部刷一张卡就行。",
                "highlight_words": ["I'm all set"]
            }
        ]
    },

    "starbucks": {
        "title": "星巴克点咖啡",
        "title_en": "Ordering at Starbucks",
        "category": "日常交流",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Barista",
                "text": "Hi there, what can I get for you today?",
                "translation": "你好，今天想喝点什么？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Hi, can I get a grande latte, please?",
                "translation": "你好，我要一杯中杯拿铁。",
                "highlight_words": ["grande", "latte"]
            },
            {
                "speaker": "Barista",
                "text": "Sure! Hot or iced?",
                "translation": "好的！热的还是冰的？",
                "highlight_words": ["hot", "iced"]
            },
            {
                "speaker": "You",
                "text": "Iced, please. With oat milk if you have it.",
                "translation": "冰的。如果有燕麦奶的话用燕麦奶。",
                "highlight_words": ["oat milk"]
            },
            {
                "speaker": "Barista",
                "text": "We do. Any sweetener? We have sugar, vanilla, or sugar-free vanilla syrup.",
                "translation": "有。要加甜味剂吗？有糖、香草糖浆或无糖香草糖浆。",
                "highlight_words": ["sweetener", "vanilla syrup"]
            },
            {
                "speaker": "You",
                "text": "Just one pump of vanilla, please. And could I get that with less ice?",
                "translation": "加一泵香草糖浆。能少放点冰吗？",
                "highlight_words": ["pump", "less ice"]
            },
            {
                "speaker": "Barista",
                "text": "You got it. Anything else?",
                "translation": "没问题。还要别的吗？",
                "highlight_words": ["You got it"]
            },
            {
                "speaker": "You",
                "text": "Yeah, can I also get a blueberry muffin?",
                "translation": "嗯，再来一个蓝莓松饼。",
                "highlight_words": ["muffin"]
            },
            {
                "speaker": "Barista",
                "text": "Sure thing. For here or to go?",
                "translation": "没问题。在这喝还是带走？",
                "highlight_words": ["For here or to go"]
            },
            {
                "speaker": "You",
                "text": "To go, please.",
                "translation": "带走。",
                "highlight_words": []
            },
            {
                "speaker": "Barista",
                "text": "That'll be $7.45. Would you like to leave a tip on the screen?",
                "translation": "一共7.45美元。您要在屏幕上留小费吗？",
                "highlight_words": ["leave a tip"]
            },
            {
                "speaker": "You",
                "text": "Sure, I'll add a dollar.",
                "translation": "好的，加一美元。",
                "highlight_words": []
            },
            {
                "speaker": "Barista",
                "text": "Thanks so much. Your drink will be ready at the pickup counter. Have a great day!",
                "translation": "非常感谢。您的饮品在取餐台取。祝您愉快！",
                "highlight_words": ["pickup counter"]
            },
            {
                "speaker": "Barista",
                "text": "Iced vanilla latte with oat milk and a blueberry muffin! ... Here you go.",
                "translation": "燕麦奶冰香草拿铁和蓝莓松饼！……给您。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Thanks! Have a good one.",
                "translation": "谢谢！祝您愉快。",
                "highlight_words": []
            }
        ]
    },

    "drive_thru": {
        "title": "快餐得来速",
        "title_en": "Fast Food Drive-Thru",
        "category": "日常交流",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "Speaker",
                "text": "Welcome to McDonald's. What can I get started for you today?",
                "translation": "欢迎来到麦当劳。今天想吃什么？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Hi, can I get a Quarter Pounder with cheese meal, please?",
                "translation": "你好，我要一个四分之一磅芝士堡套餐。",
                "highlight_words": ["Quarter Pounder", "meal"]
            },
            {
                "speaker": "Speaker",
                "text": "Sure. What size would you like for your drink and fries — small, medium, or large?",
                "translation": "好的。饮料和薯条要什么尺寸——小、中还是大？",
                "highlight_words": ["size"]
            },
            {
                "speaker": "You",
                "text": "Medium, please. And a Dr. Pepper for the drink.",
                "translation": "中号的。饮料要Dr. Pepper。",
                "highlight_words": ["Dr. Pepper"]
            },
            {
                "speaker": "Speaker",
                "text": "Got it. Anything else?",
                "translation": "好的。还要别的吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "No mustard on the burger, please. That's it.",
                "translation": "汉堡不要芥末。就这些。",
                "highlight_words": ["mustard"]
            },
            {
                "speaker": "Speaker",
                "text": "No mustard, got it. Your total is $9.27. Please pull up to the first window.",
                "translation": "不要芥末，知道了。一共9.27美元。请开到第一个窗口。",
                "highlight_words": ["total", "pull up"]
            },
            {
                "speaker": "Cashier",
                "text": "Hi, $9.27.",
                "translation": "你好，9.27美元。",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "(hands card) Here you go.",
                "translation": "（递卡）给你。",
                "highlight_words": []
            },
            {
                "speaker": "Cashier",
                "text": "Thank you. Please pull forward to the next window for your food.",
                "translation": "谢谢。请往前开到下一个窗口取餐。",
                "highlight_words": ["pull forward"]
            },
            {
                "speaker": "Staff",
                "text": "Here's your Quarter Pounder meal, medium, no mustard. Ketchup is in the bag. Enjoy!",
                "translation": "这是您的四分之一磅芝士堡套餐，中号，不要芥末。番茄酱在袋子里。请慢用！",
                "highlight_words": ["ketchup"]
            },
            {
                "speaker": "You",
                "text": "Thanks! Have a good one.",
                "translation": "谢谢！祝您愉快。",
                "highlight_words": []
            }
        ]
    },

    "small_talk": {
        "title": "同事闲聊",
        "title_en": "Small Talk with Colleagues",
        "category": "日常交流",
        "difficulty": "中级",
        "lines": [
            {
                "speaker": "Colleague",
                "text": "Hey! How was your weekend?",
                "translation": "嘿！周末过得怎么样？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "Pretty good! I checked out a couple of museums downtown. How about you?",
                "translation": "挺好的！我去市中心的几个博物馆逛了逛。你呢？",
                "highlight_words": ["checked out", "downtown"]
            },
            {
                "speaker": "Colleague",
                "text": "Not bad. Mostly just relaxed and caught up on some Netflix. Did you see the game last night?",
                "translation": "还行。主要就是休息，追了些Netflix。昨晚的比赛你看了吗？",
                "highlight_words": ["caught up on", "game"]
            },
            {
                "speaker": "You",
                "text": "I didn't, actually. Who was playing?",
                "translation": "没看。谁和谁比？",
                "highlight_words": []
            },
            {
                "speaker": "Colleague",
                "text": "The Eagles vs. the Cowboys. It was a nail-biter — Eagles won in overtime, 31-28.",
                "translation": "老鹰队对牛仔队。比赛很激烈——老鹰队加时赛赢了，31比28。",
                "highlight_words": ["nail-biter", "overtime"]
            },
            {
                "speaker": "You",
                "text": "Oh nice! I'll have to catch the highlights. I'm still learning American football.",
                "translation": "哦不错！我得看看集锦。我还在学美式足球。",
                "highlight_words": ["highlights", "American football"]
            },
            {
                "speaker": "Colleague",
                "text": "Ha, no worries. It takes a while to get into it. Hey, crazy weather we've been having, right? It was 70 degrees yesterday and now it's freezing.",
                "translation": "哈，没事。慢慢就会上瘾的。嘿，最近天气真够疯狂的吧？昨天还70度，今天就冻死了。",
                "highlight_words": ["crazy weather", "freezing"]
            },
            {
                "speaker": "You",
                "text": "Yeah, I didn't pack for this. I had to buy a jacket yesterday.",
                "translation": "是啊，我没准备这样的天气。昨天不得不买了件外套。",
                "highlight_words": ["pack"]
            },
            {
                "speaker": "Colleague",
                "text": "That's Texas weather for you. Wait five minutes and it'll change. Anyway, ready for the team meeting?",
                "translation": "德州天气就是这样。等五分钟就会变。对了，准备好开团队会了吗？",
                "highlight_words": ["That's ... for you", "team meeting"]
            },
            {
                "speaker": "You",
                "text": "Yeah, I just finished reviewing the deck. Should be a good discussion.",
                "translation": "嗯，我刚看完演示文稿。应该会有不错的讨论。",
                "highlight_words": ["deck", "discussion"]
            },
            {
                "speaker": "Colleague",
                "text": "Cool. Let's grab coffee after the meeting. There's a place downstairs that makes a decent cold brew.",
                "translation": "好的。会后一起去喝杯咖啡吧。楼下有家店的冷萃咖啡不错。",
                "highlight_words": ["grab coffee", "cold brew"]
            },
            {
                "speaker": "You",
                "text": "Sounds like a plan. See you in there!",
                "translation": "说好了。会议室见！",
                "highlight_words": ["Sounds like a plan"]
            }
        ]
    },

    "phone_call": {
        "title": "打电话",
        "title_en": "Business Phone Call",
        "category": "日常交流",
        "difficulty": "高级",
        "lines": [
            {
                "speaker": "Receptionist",
                "text": "Good morning, TechVentures. How may I direct your call?",
                "translation": "早上好，这里是TechVentures。请问您找谁？",
                "highlight_words": ["direct your call"]
            },
            {
                "speaker": "You",
                "text": "Hi, this is Li Wei from DataStream Solutions. Could I speak with Sarah Johnson, please?",
                "translation": "你好，我是DataStream Solutions的李伟。请帮我接Sarah Johnson。",
                "highlight_words": []
            },
            {
                "speaker": "Receptionist",
                "text": "Let me check if she's available. ... I'm sorry, she's in a meeting right now. Would you like to leave a voicemail?",
                "translation": "我看看她是否方便。……抱歉，她现在在开会。您要留语音留言吗？",
                "highlight_words": ["voicemail"]
            },
            {
                "speaker": "You",
                "text": "Yes, please. Could you also let her know it's regarding the Q3 partnership proposal?",
                "translation": "好的。能麻烦转告她是关于第三季度合作提案的吗？",
                "highlight_words": ["regarding", "partnership proposal"]
            },
            {
                "speaker": "Receptionist",
                "text": "Absolutely. I'll make sure she gets the message. Let me transfer you to her voicemail.",
                "translation": "当然。我会确保她收到消息。我帮您转接到语音信箱。",
                "highlight_words": ["transfer"]
            },
            {
                "speaker": "Voicemail",
                "text": "Hi, you've reached Sarah Johnson. I'm either away from my desk or on another call. Please leave your name, number, and a brief message, and I'll get back to you as soon as I can.",
                "translation": "您好，您已到达Sarah Johnson的语音信箱。我不在座位上或在另一个电话中。请留下您的姓名、号码和简短留言，我会尽快回复。",
                "highlight_words": ["away from my desk", "get back to you"]
            },
            {
                "speaker": "You",
                "text": "Hi Sarah, this is Li Wei from DataStream Solutions. I'm calling about the Q3 partnership proposal we sent over last week. I'd love to schedule a follow-up call to go over the details. My number is 555-0142, or you can reach me at wei.li@datastream.com. Thanks, and I look forward to hearing from you. Have a great day!",
                "translation": "Sarah你好，我是DataStream Solutions的李伟。我打电话是关于上周发的第三季度合作提案。希望能安排一个后续电话讨论细节。我的号码是555-0142，也可以发邮件到wei.li@datastream.com。谢谢，期待您的回复。祝您愉快！",
                "highlight_words": ["follow-up call", "go over", "reach me"]
            },
            {
                "speaker": "Sarah",
                "text": "(later, calling back) Hi Li, this is Sarah Johnson returning your call. Sorry I missed you earlier!",
                "translation": "（稍后回电）李伟你好，我是Sarah Johnson，回你的电话。抱歉刚才没接到！",
                "highlight_words": ["returning your call"]
            },
            {
                "speaker": "You",
                "text": "Hey Sarah, thanks for getting back to me! I know you're busy.",
                "translation": "Sarah你好，谢谢回复！我知道你很忙。",
                "highlight_words": ["getting back to me"]
            },
            {
                "speaker": "Sarah",
                "text": "No problem at all. I actually read through the proposal this morning — it looks really promising. Do you have some time this Thursday around 2 PM EST?",
                "translation": "完全没关系。我今早其实已经看了提案——看起来很有前景。你这周四美东时间下午2点左右有空吗？",
                "highlight_words": ["read through", "promising", "EST"]
            },
            {
                "speaker": "You",
                "text": "Thursday at 2 PM works perfectly for me. Should we do a Zoom call?",
                "translation": "周四下午2点没问题。用Zoom通话可以吗？",
                "highlight_words": ["works perfectly", "Zoom call"]
            },
            {
                "speaker": "Sarah",
                "text": "Zoom sounds great. I'll send over a calendar invite with the link. Talk to you then!",
                "translation": "Zoom可以。我会发一个带链接的日历邀请。到时候聊！",
                "highlight_words": ["calendar invite"]
            },
            {
                "speaker": "You",
                "text": "Sounds good. Thanks, Sarah. Looking forward to it!",
                "translation": "好的。谢谢Sarah。期待通话！",
                "highlight_words": ["Looking forward to it"]
            }
        ]
    },

    # ============================================================
    # Category: 美国特有 (US-Specific)
    # ============================================================
    "customs_entry": {
        "title": "海关入境",
        "title_en": "CBP Interview at US Customs",
        "category": "美国特有",
        "difficulty": "高级",
        "lines": [
            {
                "speaker": "CBP Officer",
                "text": "Good morning. May I see your passport, please?",
                "translation": "早上好。请出示护照。",
                "highlight_words": ["passport"]
            },
            {
                "speaker": "You",
                "text": "Good morning. Here you go.",
                "translation": "早上好。给您。",
                "highlight_words": []
            },
            {
                "speaker": "CBP Officer",
                "text": "What is the purpose of your visit to the United States?",
                "translation": "您来美国的目的是什么？",
                "highlight_words": ["purpose of your visit"]
            },
            {
                "speaker": "You",
                "text": "I'm here for business. I have a conference in San Francisco and I'll be visiting our company's US office in Austin as well.",
                "translation": "我是来出差的。在旧金山有个会议，还要去奥斯汀访问我们公司的美国办公室。",
                "highlight_words": ["business"]
            },
            {
                "speaker": "CBP Officer",
                "text": "How long do you plan to stay?",
                "translation": "您计划停留多长时间？",
                "highlight_words": ["plan to stay"]
            },
            {
                "speaker": "You",
                "text": "About two weeks. I'll be leaving on the 28th.",
                "translation": "大约两周。我28号离开。",
                "highlight_words": []
            },
            {
                "speaker": "CBP Officer",
                "text": "Where will you be staying?",
                "translation": "您住在哪里？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "I'll be at the Marriott Marquis in San Francisco for the first week, and then a hotel in downtown Austin for the second week.",
                "translation": "第一周住在旧金山的Marriott Marquis，第二周住在奥斯汀市中心的酒店。",
                "highlight_words": []
            },
            {
                "speaker": "CBP Officer",
                "text": "Do you have the hotel confirmation with you?",
                "translation": "您有酒店确认单吗？",
                "highlight_words": ["confirmation"]
            },
            {
                "speaker": "You",
                "text": "Yes, right here in my phone. I can also show you my return flight itinerary.",
                "translation": "有的，在我手机里。我也可以给您看返程航班行程单。",
                "highlight_words": ["itinerary"]
            },
            {
                "speaker": "CBP Officer",
                "text": "That's fine. How much currency are you carrying?",
                "translation": "您携带了多少现金？",
                "highlight_words": ["currency"]
            },
            {
                "speaker": "You",
                "text": "About $500 in cash, and I have my credit cards as well.",
                "translation": "大约500美元现金，还有信用卡。",
                "highlight_words": []
            },
            {
                "speaker": "CBP Officer",
                "text": "Do you have any food, plants, or agricultural products with you?",
                "translation": "您携带了任何食品、植物或农产品吗？",
                "highlight_words": ["agricultural products"]
            },
            {
                "speaker": "You",
                "text": "No, I don't.",
                "translation": "没有。",
                "highlight_words": []
            },
            {
                "speaker": "CBP Officer",
                "text": "Have you visited any other countries in the past 14 days?",
                "translation": "过去14天内您去过其他国家吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "No, I flew directly from Shanghai.",
                "translation": "没有，我从上海直飞过来的。",
                "highlight_words": ["directly"]
            },
            {
                "speaker": "CBP Officer",
                "text": "Is this your first time in the United States?",
                "translation": "这是您第一次来美国吗？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "No, I've been here a few times before — mostly for conferences and business trips.",
                "translation": "不是，我之前来过几次——主要是开会和出差。",
                "highlight_words": []
            },
            {
                "speaker": "CBP Officer",
                "text": "What do you do for work?",
                "translation": "您做什么工作？",
                "highlight_words": []
            },
            {
                "speaker": "You",
                "text": "I'm a software engineer at a tech company based in Shanghai.",
                "translation": "我在上海一家科技公司做软件工程师。",
                "highlight_words": ["software engineer"]
            },
            {
                "speaker": "CBP Officer",
                "text": "Alright, everything looks good. Welcome to the United States. Enjoy your stay.",
                "translation": "好的，都没问题。欢迎来到美国。祝您停留愉快。",
                "highlight_words": ["Welcome to"]
            },
            {
                "speaker": "You",
                "text": "Thank you very much!",
                "translation": "非常感谢！",
                "highlight_words": []
            }
        ]
    },

    "tipping_guide": {
        "title": "小费指南",
        "title_en": "Tipping Etiquette Guide",
        "category": "美国特有",
        "difficulty": "初级",
        "lines": [
            {
                "speaker": "Guide",
                "text": "Tipping is expected in the US for most service interactions. Not tipping can be considered rude.",
                "translation": "在美国，大多数服务场景都需要给小费。不给小费可能被认为是不礼貌的。",
                "highlight_words": ["tipping", "rude"]
            },
            {
                "speaker": "Guide",
                "text": "Restaurants (sit-down): Tip 15-20% of the pre-tax bill. 18% is standard for good service. For excellent service, 20-25%. Large parties (6+ people) may have an automatic gratuity of 18% added.",
                "translation": "餐厅（堂食）：小费为税前账单的15-20%。18%是服务良好时的标准。服务特别好的话20-25%。大型聚会（6人以上）可能会自动加收18%的服务费。",
                "highlight_words": ["pre-tax bill", "standard", "gratuity"]
            },
            {
                "speaker": "Guide",
                "text": "Coffee shops (Starbucks, etc.): $1 per drink is common, or round up. Use the tip screen — $1 is fine.",
                "translation": "咖啡店（星巴克等）：每杯饮料1美元很常见，或者凑整。用屏幕上的小费功能——1美元就行。",
                "highlight_words": ["round up", "tip screen"]
            },
            {
                "speaker": "Guide",
                "text": "Bars: Tip $1-2 per drink. If you're running a tab, tip 15-20% of the total.",
                "translation": "酒吧：每杯饮料给1-2美元小费。如果是记账消费，给总额的15-20%。",
                "highlight_words": ["running a tab"]
            },
            {
                "speaker": "Guide",
                "text": "Food delivery (DoorDash, Uber Eats): Tip at least 15-20%. The driver relies on tips since base pay is low.",
                "translation": "外卖送餐（DoorDash、Uber Eats）：至少给15-20%。司机主要靠小费，因为基础工资很低。",
                "highlight_words": ["base pay"]
            },
            {
                "speaker": "Guide",
                "text": "Ride-hailing (Uber/Lyft): Tip $3-5 for a typical ride. You can add it in the app after the ride. 5 stars is NOT a tip — drivers need both.",
                "translation": "网约车（Uber/Lyft）：普通行程给3-5美元小费。可以在行程结束后在app里加。5星评价不是小费——司机两个都需要。",
                "highlight_words": ["5 stars"]
            },
            {
                "speaker": "Guide",
                "text": "Hotel housekeeping: $2-5 per night. Leave it on the pillow or nightstand with a thank-you note. Tip daily, not just at checkout.",
                "translation": "酒店客房清洁：每晚2-5美元。放在枕头或床头柜上，附一张感谢便条。每天给，不要只在退房时给。",
                "highlight_words": ["housekeeping", "nightstand"]
            },
            {
                "speaker": "Guide",
                "text": "Hotel bellhop (luggage help): $2-3 per bag. Tip when they deliver your bags to the room.",
                "translation": "酒店行李员（帮忙搬行李）：每件行李2-3美元。在他们把行李送到房间时给。",
                "highlight_words": ["bellhop"]
            },
            {
                "speaker": "Guide",
                "text": "Valet parking: $3-5 when they return your car.",
                "translation": "代客泊车：他们把车还给你时给3-5美元。",
                "highlight_words": ["valet parking"]
            },
            {
                "speaker": "Guide",
                "text": "Hair salon / barber: 15-20% of the service cost.",
                "translation": "理发店/美发沙龙：服务费用的15-20%。",
                "highlight_words": ["hair salon", "barber"]
            },
            {
                "speaker": "Guide",
                "text": "NO tipping needed at: fast food counters, grocery stores, gas stations, retail stores, pharmacies, and most self-service situations.",
                "translation": "以下场景不需要小费：快餐柜台、超市、加油站、零售店、药店，以及大多数自助服务场景。",
                "highlight_words": ["retail stores", "pharmacies", "self-service"]
            },
            {
                "speaker": "Guide",
                "text": "Quick formula: For restaurants, double the tax (tax is usually ~8-10%). That gives you roughly 16-20%, which is a safe tip.",
                "translation": "快速计算法：在餐厅，税额翻倍（税通常约8-10%）。这样大约是16-20%，是一个安全的小费比例。",
                "highlight_words": ["double the tax"]
            }
        ]
    }
}


def get_all_us_dialogs():
    """获取所有美国出差对话列表"""
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


def get_us_dialog(dialog_id):
    """获取指定美国出差对话内容"""
    return DIALOGS.get(dialog_id)
