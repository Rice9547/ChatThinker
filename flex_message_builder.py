from linebot.models import (
    FlexSendMessage, BubbleContainer, BoxComponent, 
    TextComponent, ButtonComponent, SeparatorComponent,
    CarouselContainer, URIAction, PostbackAction,
    MessageAction
)

class FlexMessageBuilder:
    """建立 LINE Flex Message 卡片"""
    
    @staticmethod
    def create_reply_options_carousel(options):
        """建立回覆選項的輪播卡片"""
        bubbles = []
        
        for idx, option in enumerate(options):
            bubble = BubbleContainer(
                size='kilo',
                header=BoxComponent(
                    layout='vertical',
                    contents=[
                        BoxComponent(
                            layout='horizontal',
                            contents=[
                                TextComponent(
                                    text=option['emoji'],
                                    size='sm',
                                    flex=0
                                ),
                                TextComponent(
                                    text=option['title'],
                                    weight='bold',
                                    color='#1DB446',
                                    size='sm',
                                    flex=1,
                                    margin='md'
                                )
                            ]
                        )
                    ],
                    backgroundColor='#F0F0F0',
                    paddingAll='10px'
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text=option['text'],
                            wrap=True,
                            size='sm',
                            color='#333333'
                        )
                    ],
                    paddingAll='15px'
                ),
                footer=BoxComponent(
                    layout='vertical',
                    contents=[
                        ButtonComponent(
                            action=MessageAction(
                                label='📋 使用這個',
                                text=option['text']
                            ),
                            style='primary',
                            color='#1DB446',
                            height='sm'
                        ),
                        ButtonComponent(
                            action=PostbackAction(
                                label='✏️ 調整語氣',
                                data=f'action=adjust_tone&index={idx}&style={option["style"]}'
                            ),
                            style='secondary',
                            height='sm',
                            margin='sm'
                        )
                    ],
                    spacing='sm',
                    paddingAll='10px'
                )
            )
            bubbles.append(bubble)
        
        carousel = CarouselContainer(contents=bubbles)
        return FlexSendMessage(alt_text='回覆選項', contents=carousel)
    
    @staticmethod
    def create_quick_scenarios_menu():
        """建立快速情境選單"""
        bubble = BubbleContainer(
            header=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text='🚀 快速情境',
                        weight='bold',
                        size='md',
                        color='#FFFFFF'
                    )
                ],
                backgroundColor='#1DB446',
                paddingAll='15px'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text='選擇常見情境，立即獲得回覆建議：',
                        size='sm',
                        color='#666666',
                        wrap=True
                    ),
                    SeparatorComponent(margin='md'),
                    
                    # 請假
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text='🏥', flex=0, size='lg'),
                            ButtonComponent(
                                action=PostbackAction(
                                    label='請假',
                                    data='scenario=請假'
                                ),
                                flex=1,
                                style='link',
                                height='sm'
                            )
                        ],
                        margin='md',
                        spacing='md'
                    ),
                    
                    # 拒絕加班
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text='🌙', flex=0, size='lg'),
                            ButtonComponent(
                                action=PostbackAction(
                                    label='拒絕加班',
                                    data='scenario=拒絕加班'
                                ),
                                flex=1,
                                style='link',
                                height='sm'
                            )
                        ],
                        spacing='md'
                    ),
                    
                    # 催進度
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text='⏰', flex=0, size='lg'),
                            ButtonComponent(
                                action=PostbackAction(
                                    label='催進度',
                                    data='scenario=催進度'
                                ),
                                flex=1,
                                style='link',
                                height='sm'
                            )
                        ],
                        spacing='md'
                    ),
                    
                    # 道歉
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text='🙏', flex=0, size='lg'),
                            ButtonComponent(
                                action=PostbackAction(
                                    label='道歉',
                                    data='scenario=道歉'
                                ),
                                flex=1,
                                style='link',
                                height='sm'
                            )
                        ],
                        spacing='md'
                    ),
                    
                    # 自訂
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text='💭', flex=0, size='lg'),
                            ButtonComponent(
                                action=MessageAction(
                                    label='自訂情境',
                                    text='我要自訂情境'
                                ),
                                flex=1,
                                style='link',
                                height='sm'
                            )
                        ],
                        spacing='md'
                    )
                ],
                spacing='sm',
                paddingAll='20px'
            )
        )
        
        return FlexSendMessage(alt_text='快速情境選單', contents=bubble)
    
    @staticmethod
    def create_tone_adjustment_menu(original_text):
        """建立語氣調整選單"""
        bubble = BubbleContainer(
            header=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text='✏️ 調整語氣',
                        weight='bold',
                        size='md',
                        color='#FFFFFF'
                    )
                ],
                backgroundColor='#FF6B6B',
                paddingAll='15px'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text='原文：',
                        size='xs',
                        color='#999999'
                    ),
                    TextComponent(
                        text=original_text[:50] + '...' if len(original_text) > 50 else original_text,
                        size='sm',
                        wrap=True,
                        margin='sm'
                    ),
                    SeparatorComponent(margin='md'),
                    TextComponent(
                        text='選擇想要的語氣：',
                        size='sm',
                        color='#666666',
                        margin='md'
                    ),
                    
                    BoxComponent(
                        layout='vertical',
                        contents=[
                            ButtonComponent(
                                action=PostbackAction(
                                    label='👔 更正式',
                                    data=f'tone=formal&text={original_text[:100]}'
                                ),
                                style='secondary',
                                height='sm'
                            ),
                            ButtonComponent(
                                action=PostbackAction(
                                    label='😊 更輕鬆',
                                    data=f'tone=casual&text={original_text[:100]}'
                                ),
                                style='secondary',
                                height='sm',
                                margin='sm'
                            ),
                            ButtonComponent(
                                action=PostbackAction(
                                    label='🤝 更委婉',
                                    data=f'tone=polite&text={original_text[:100]}'
                                ),
                                style='secondary',
                                height='sm',
                                margin='sm'
                            ),
                            ButtonComponent(
                                action=PostbackAction(
                                    label='💪 更直接',
                                    data=f'tone=direct&text={original_text[:100]}'
                                ),
                                style='secondary',
                                height='sm',
                                margin='sm'
                            )
                        ],
                        margin='md',
                        spacing='sm'
                    )
                ],
                paddingAll='20px'
            )
        )
        
        return FlexSendMessage(alt_text='調整語氣', contents=bubble)
    
    @staticmethod
    def create_simple_reply_card(text, title="建議回覆"):
        """建立簡單的回覆卡片（單一選項）"""
        bubble = BubbleContainer(
            size='kilo',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text=title,
                        weight='bold',
                        size='sm',
                        color='#1DB446'
                    ),
                    TextComponent(
                        text=text,
                        wrap=True,
                        size='md',
                        margin='md'
                    )
                ],
                paddingAll='20px'
            ),
            footer=BoxComponent(
                layout='horizontal',
                contents=[
                    ButtonComponent(
                        action=MessageAction(
                            label='📋 複製使用',
                            text=text
                        ),
                        style='primary',
                        color='#1DB446'
                    )
                ],
                paddingAll='10px'
            )
        )
        
        return FlexSendMessage(alt_text=title, contents=bubble)